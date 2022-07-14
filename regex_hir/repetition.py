"""
Contains a class representing repetition operators.
"""

__all__ = ["Repetition", "RepetitionKind", "RepetitionRange"]

from dataclasses import dataclass
import typing
from enum import auto

from regex_hir.token import Token
from regex_hir.ops import Opcode
from regex_hir.utils import override, Enum
from regex_hir.nre.constants import MAXREPEAT


@dataclass
class RepetitionRange:
    """
    Start and end of a repetition range.

    Note: Matches at least `start` times, and at most `end` times
    """
    start: int
    end: int


class RepetitionKind(Enum):
    """
    The different kinds of repetition.
    - `ZeroOrOne`: `...?`
    - `ZeroOrMore`: `...*`
    - `OneOrMore`: `...+`
    - `Range`: `{...,[...]}`

    Note: A range like `{2,}` will be represented as `RepetitionKind.Range(2, MAXREPEAT)`. `MAXREPEAT` is defined in: https://github.com/python/cpython/blob/main/Modules/_sre/sre.h
    """
    ZeroOrOne = auto()
    ZeroOrMore = auto()
    OneOrMore = auto()
    Range = RepetitionRange


@dataclass
class Repetition(Token):
    """
    Represents forms of repetition.
    - `hir(r"a+")` -> `Repetition(pat=Literal(lit=97), greedy=True, kind=RepetitionKind.OneOrMore)`
    - `hir(r"a{2,3}?")` -> `Repetition(pat=Literal(lit=97), greedy=False, kind=RepetitionKind.RepetitionRange(start=2, end=3))`

    ...
    """
    pat: typing.Any
    greedy: bool
    kind: RepetitionKind

    @override
    def from_pat(pat, state):
        greedy = False
        hpat = None

        lower, upper = None, None

        match pat.data:
            case [(Opcode.MAX_REPEAT, (lower, upper, pat))]:
                hpat = pat.to_hir(state)
                greedy = True

            case [(Opcode.MIN_REPEAT, (lower, upper, pat))]:
                hpat = pat.to_hir(state)

            case _:
                return

        match (lower, upper):
            case (0, u) if u == MAXREPEAT:
                return Repetition(hpat, greedy, RepetitionKind.ZeroOrMore, state=state)

            case (0, 1):
                return Repetition(hpat, greedy, RepetitionKind.ZeroOrOne, state=state)

            case (1, u) if u == MAXREPEAT:
                return Repetition(hpat, greedy, RepetitionKind.OneOrMore, state=state)

            case (l, u):
                return Repetition(hpat, greedy, RepetitionKind.Range(l, u), state=state)
