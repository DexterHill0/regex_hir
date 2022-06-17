"""
Contains a class for regex anchors.
"""

__all__ = ["Anchor", "AnchorKind"]

from dataclasses import dataclass
from enum import auto

from regex_hir.token import Token
from regex_hir.ops import Opcode
from regex_hir.utils import override, Enum


class AnchorKind(Enum):
    """
    The different kinds of anchors.
    - Beginning``: `^a`
    - `End`: `a$`
    """
    Beginning = auto()
    End = auto()


@dataclass
class Anchor(Token):
    """
    Represents an anchor.
    - `hir(r"^a")` -> ``
    - `hir(r"a$")` -> ``
    """
    kind: AnchorKind

    @override
    def from_pat(pat):
        match pat.data:
            case [(Opcode.AT, Opcode.AT_BEGINNING)]:
                return Anchor(AnchorKind.Beginning)

            case [(Opcode.AT, Opcode.AT_END)]:
                return Anchor(AnchorKind.End)