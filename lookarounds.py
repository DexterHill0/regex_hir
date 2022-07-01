"""
Contains classes representing the different lookarounds in regex.
"""

__all__ = ["Lookaround", "LookaroundKind"]

from dataclasses import dataclass
from enum import auto
import typing

from regex_hir.token import Token
from regex_hir.ops import Opcode
from regex_hir.utils import override, Enum


# Lookaround directions (indicates if they are lookahead / lookbehind).
class Dir:
    FORWARD = 1
    BACKWARD = -1


class LookaroundKind(Enum):
    """
    The different kinds of lookarounds:
    - `PositiveLookahead`: `(?=...)`
    - `NegativeLookahead`: `(?!...)`
    - `PositiveLookbehind`: `(?<=...)`
    - `NegativeLookbehind`: `(?<!...)`

    """
    PositiveLookahead = auto()
    NegativeLookahead = auto()
    PositiveLookbehind = auto()
    NegativeLookbehind = auto()


@dataclass
class Lookaround(Token):
    """
    Represents lookaround tokens.
    - `hir(r"(?=a)")` -> `Lookaround(pat=Literal(lit=97), kind=LookaroundKind.PositiveLookahead)`
    - `hir(r"(?<!a)")` -> `Lookaround(pat=Literal(lit=97), kind=LookaroundKind.NegativeLookbehind)`

    ...
    """
    pat: typing.Any
    kind: LookaroundKind

    @override
    def from_pat(pat, state):
        match pat.data:
            case [(Opcode.ASSERT, (dir, pat))]:
                hpat = pat.to_hir(state)

                if dir == Dir.FORWARD:
                    return Lookaround(hpat, kind=LookaroundKind.PositiveLookahead, state=state)

                if dir == Dir.BACKWARD:
                    return Lookaround(hpat, kind=LookaroundKind.PositiveLookbehind, state=state)

            case [(Opcode.ASSERT_NOT, (dir, pat))]:
                hpat = pat.to_hir(state)

                if dir == Dir.FORWARD:
                    return Lookaround(hpat, kind=LookaroundKind.NegativeLookahead, state=state)

                if dir == Dir.BACKWARD:
                    return Lookaround(hpat, kind=LookaroundKind.NegativeLookbehind, state=state)
