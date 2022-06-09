"""
Contains a class representing character classes
"""

__all__ = ["Literal"]


from dataclasses import dataclass

from regex_hir.token import Token
from regex_hir.ops import Opcode
from regex_hir.utils import override


@dataclass(init=False)
class CharacterClass(Token):
    """
    Represents a single literal character.
    - `hir(r"a")` -> `Literal("a")`
    """

    lit: str

    def __init__(self, char: int):
        # Convert the given character int to a string.
        self.lit = chr(char)

    @override
    def from_pat(pat):
        pass