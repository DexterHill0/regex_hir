"""
Contains a class representing a branch of alternate matches.
"""

__all__ = ["Branch"]

from dataclasses import dataclass
import typing

from regex_hir.token import Token
from regex_hir.ops import Opcode
from regex_hir.utils import override


@dataclass
class Branch(Token):
    """
    Represents a branch of matches.
    - `hir(r"(a)|(b)")` -> `Branch(branches=[Group(pat=Literal(lit=97), kind=GroupKind.CaptureGroup(index=1)), Group(pat=Literal(lit=98), kind=GroupKind.CaptureGroup(index=2))])`

    ...

    Note: Certain branches may be optimised into character classes by `re`. For example: `a|b` will become `[ab]`, or `ab|ad|ac` will become `a[bdc]`.
    """
    branches: list[typing.Any]

    @override
    def from_pat(pat, state):
        match pat.data:
            case [(Opcode.BRANCH, (_, branches))]:
                return Branch(
                    [*map(lambda b: b.to_hir(state), branches)],
                    state=state,
                )