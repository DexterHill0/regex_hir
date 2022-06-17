"""
Contains a class representing character classes.
"""

__all__ = ["CharacterClass", "CharacterRange"]

from dataclasses import dataclass

from regex_hir.token import Token
from regex_hir.ops import Opcode
from regex_hir.utils import override, uord


@dataclass
class CharacterRange:
    """
    Start and end character codes of a single range. If start and end are equal it is a single character. Start cannot be larger than end.
    """
    start: int
    end: int


@dataclass
class CharacterClass(Token):
    """
    Represents a range of characters.
    - `hir(r"[az]")` -> `CharacterClass(ranges=[CharacterRange(start=97, end=97), CharacterRange(start=122, end=122)], negate=False)`
    - `hir(r"[^a-z]")` -> `CharacterClass(ranges=[CharacterRange(start=97, end=122)], negate=True)`

    Note: A pattern like `a|b` is also represented as a character class as it is identical to `[ab]`.
    """
    ranges: list[CharacterRange]
    negate: bool

    @override
    def from_pat(pat):
        negated = False
        ranges = []

        match pat.data:
            case [(Opcode.IN, [(Opcode.NEGATE, _), *rest])]:
                negated = True
                ranges = rest

            case [(Opcode.IN, rest)]:
                ranges = rest

            case _:
                return
        
        for i, r in enumerate(ranges):
            match r:
                case (Opcode.RANGE, (start, end)):
                    # Replace the element in the array to save making a new array.
                    ranges[i] = CharacterRange(start, end)

                case (Opcode.LITERAL, lit):
                    ranges[i] = CharacterRange(lit, lit)

        return CharacterClass(ranges, negated)

    def push(self, range: CharacterRange):
        """
        Adds a new range to the character class.
        """
        self.ranges.append(range)

    def negate(self):
        """
        Negates the character class in place.
        """
        self.negate = True

    def case_fold_simple(self):
        """
        Performs a simple unicode case folding on the character ranges. For example, a character class containing the range:
        - `a-z`
        
        after case folding will contain the ranges:
        - `a-z`
        - `A-Z`
        """
        new = []

        for r in self.ranges:
            # Use python's builtin case folding for strings.
            # I could generate a massive dictionary mapping from Unicode's case folding text file but this seems easier.
            start = ord(chr(r.start).casefold())
            end = ord(chr(r.end).casefold())

            if start > end:
                raise ValueError("`start` is larger than `end` after case folding!")

            new.append(CharacterRange(start, end))
        
        self.ranges.extend(new)

    def is_all_ascii(self) -> bool:
        """
        Return true if the character class contains only ASCII characters (also returns true if it matches nothing).
        """
        for r in self.ranges:
            # Last ascii character.
            if r.end > ord("\x7F"):
                return False
                
        return True

    def is_char_in(self, char: str):
        """
        Return true if the given character is contained within any of the ranges. 
        
        If the class is negated, it returns true if the character is not within any of the ranges.
        """
        o, _ = uord(char)
        for r in self.ranges:
            if o >= r.start and o <= r.end:
                return not self.negate

        return self.negate

    def __iter__(self):
        yield from self.ranges