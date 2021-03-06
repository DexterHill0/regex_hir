"""
Contains a class representing a literal character.
"""

__all__ = ["Literal"]

from typing import Union
from dataclasses import dataclass, field

from regex_hir.token import Token
from regex_hir.ops import Opcode
from regex_hir.utils import override, uord
from regex_hir.patterns import Patterns


@dataclass
class Literal(Token):
    """
    Represents a single literal character.
    - `hir(r"a")` -> `Literal(lit=97)`

    ...
    """
    lit: int

    @override
    def from_pat(pat, state):
        match pat.data:
            case [(Opcode.LITERAL, lit)]:
                return Literal(lit, state=state)

    def char(char: str) -> Union['Literal', Patterns]:
        """
        Creates a literal from the given char. If the char has a variant selector, it returns a `Patterns` of both the literals.
        """
        o, v = uord(char)

        if v is not None:
            return Patterns([Literal(o), Literal(v)])
        
        return Literal(o)

    def __eq__(self, other):
        match other:
            case Literal(lit):
                return lit == self.lit
                
            case c:
                return c == self.lit
