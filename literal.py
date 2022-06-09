"""
Contains a class representing a literal character.
"""

__all__ = ["Literal"]


from dataclasses import dataclass

from regex_hir.token import Token
from regex_hir.ops import Opcode
from regex_hir.utils import override


@dataclass(init=False)
class Literal(Token):
    """
    Represents a single literal character.
    - `hir(r"a")` -> `Literal("a")`
    """

    lit: str

    def __init__(self, char: int):
        # Convert the given character int to a string.
        self.lit = chr(char)

    def char(char: str) -> 'Literal':
        """
        Creates a literal from a char.
        """
        return Literal(ord(char))

    @override
    def from_pat(pat):
        match pat.data:
            case [(Opcode.LITERAL, lit)]:
                return Literal(lit)