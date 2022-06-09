"""
Contains a class representing character classes.
"""

__all__ = ["CharacterClass"]


from dataclasses import dataclass

from regex_hir.token import Token
from regex_hir.ops import Opcode
from regex_hir.utils import override


@dataclass(init=False)
class CharacterClass(Token):
    """
    """

    def __init__(self, char: int):
        pass

    @override
    def from_pat(pat):
        pass