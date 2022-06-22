"""
Contains a class representing character classes.
"""

__all__ = ["CharacterClass", "CharacterRange"]

from dataclasses import dataclass, field
import unicategories as unc

from regex_hir.token import Token
from regex_hir.ops import Opcode
from regex_hir.utils import override, uord
from regex_hir.flags import Flags


@dataclass
class CharacterRange:
    """
    Start and end character codes of a single range. If start and end are equal it is a single character. Start cannot be larger than end.

    Note: Start and end are inclusive.
    """
    start: int
    end: int

    def __hash__(self):
      return hash((self.start, self.end))


# Creates a function that returns different character ranges depending on the flags set.
# `default` is the "base" character range.
# All keywords arguments go `<flag>=<ranges>`. If the flag `<flag>` is enabled, `<ranges>` is added to `default`.
def crange(default, **kwargs):
    def inner(state):
        ranges = default.copy() # aaaa references (copy so `default` isn't modified when `ranges` is modified).
        
        for k in kwargs.keys():
            if state.has_flag(Flags[k]):
                ranges.update(kwargs[k])

        return list(ranges)

    return inner

def range_from_category(cat):
    return map(lambda r: CharacterRange(r[0], r[1]-1), cat)

# Represents the different escape sequence based character ranges.
class Ranges:
    DOT = crange(
        {
            CharacterRange(0, 9),
            CharacterRange(11, 255), # 10 is newline.
        },
        DOTALL={CharacterRange(10, 10)},
        UNICODE={CharacterRange(255, 0x10FFFF)},
    )

    WORD = crange(
        {
            CharacterRange(48, 57), # 0-9
            CharacterRange(65, 90), # A-z
            CharacterRange(97, 122), # a-z
            CharacterRange(95, 95), # _
        },
        UNICODE={
            # `\w` with unicode enabled matches `[\p{L}\p{N}_]` where `L` (letter) and `N` (number) are the unicode categories as shown below.
            *range_from_category(unc.categories["L"]),
            *range_from_category(unc.categories["N"]),
        }
    )

    DIGIT = crange(
        {CharacterRange(48, 57)}, # 0-9
        UNICODE={
            # `Nd` = decimal digit.
            *range_from_category(unc.categories["Nd"]),
        }
    )

    WHITESPACE = crange(
        {
            CharacterRange(13, 13), # \r
            CharacterRange(10, 10), # \n
            CharacterRange(9, 9), # \t
            CharacterRange(11, 11), # \v
            CharacterRange(32, 32), # ` ` (literal space)
        },
        UNICODE={
            # `Z` = separator.
            *range_from_category(unc.categories["Z"]),
        }
    )


@dataclass
class CharacterClass(Token):
    """
    Represents a range of characters.
    - `hir(r"[az]")` -> `CharacterClass(ranges=[CharacterRange(start=97, end=97), CharacterRange(start=122, end=122)], negate=False, ignore_case=False)`
    - `hir(r"[^a-z]")` -> `CharacterClass(ranges=[CharacterRange(start=97, end=122)], negate=True, ignore_case=False)`

    All meta sequences like `\w`, `\d`, etc. (including `.`) are represented as characters classes.
    By default, it will return all ASCII and Unicode characters the sequences represent. If Unicode is disabled (I.E. byte strings), it only returns the ASCII characters.
    """
    ranges: list[CharacterRange]
    negate: bool
    ignore_case: bool = field(repr=False, default_factory=bool)

    # Called after `__init__` automatically.
    def __post_init__(self, state):
        super().__post_init__(state)

        if self.ignore_case:
            self.case_fold_simple()

    @override
    def from_pat(pat, state):
        negated = False
        ranges = []

        ignore_case = state.has_flag(Flags.IGNORECASE)

        match pat.data:
            case [(Opcode.IN, [neg, *rest])]:
                match neg:
                    case (Opcode.NEGATE, None):
                        negated = True
                    
                    case _:
                        rest = [neg, *rest]

                ranges = rest

            # A single negated literal in a character class.
            # Only exists within a character class so putting it in the literal file doesn't make much sense.
            case [(Opcode.NOT_LITERAL, lit)]:
                return CharacterClass(CharacterRange(lit, lit), True, ignore_case, state=state)

            case [(Opcode.ANY, _)]:
                return CharacterClass(Ranges.DOT(state), negated, ignore_case, state=state) # Negated should always be `False`.

            case _:
                return
        
        for i, r in enumerate(ranges):
            match r:
                case (Opcode.RANGE, (start, end)):
                    # Replace the element in the array to save making a new array.
                    ranges[i] = CharacterRange(start, end)

                case (Opcode.LITERAL, lit):
                    ranges[i] = CharacterRange(lit, lit)

                case (Opcode.CATEGORY, cat):
                    match cat:
                        case Opcode.CATEGORY_WORD:
                            return CharacterClass(Ranges.WORD(state), False, ignore_case, state=state)

                        case Opcode.CATEGORY_NOT_WORD:
                            return CharacterClass(Ranges.WORD(state), True, ignore_case, state=state)

                        case Opcode.CATEGORY_DIGIT:
                            return CharacterClass(Ranges.DIGIT(state), False, ignore_case, state=state)

                        case Opcode.CATEGORY_NOT_DIGIT:
                            return CharacterClass(Ranges.DIGIT(state), True, ignore_case, state=state)

                        case Opcode.CATEGORY_SPACE:
                            return CharacterClass(Ranges.WHITESPACE(state), False, ignore_case, state=state)

                        case Opcode.CATEGORY_NOT_SPACE:
                            return CharacterClass(Ranges.WHITESPACE(state), True, ignore_case, state=state)

        return CharacterClass(ranges, negated, ignore_case, state=state)

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
        - `A-Z`
        
        after case folding will contain the ranges:
        - `a-z`
        - `A-Z`

        Note: If the ignore case flag is enabled, this will not add any new ranges as it already matches both cases.
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