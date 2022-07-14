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
    - `LineBeginning`: `^...`
    - `LineEnd`: `...$`
    - `StringBeginning`: `\A...`
    - `StringEnd`: `...\Z`
    - `Word`: `\\b...`
    - `NonWord`: `\B...`
    """
    LineBeginning = auto()
    LineEnd = auto()
    StringBeginning = auto()
    StringEnd = auto()

    Word = auto()
    NonWord = auto()


@dataclass
class Anchor(Token):
    """
    Represents an anchor.
    - `hir(r"^a")` -> `Patterns(pats=[Anchor(kind=AnchorKind.LineBeginning), Literal(lit=97)])`
    - `hir(r"\\ba")` -> `Patterns(pats=[Anchor(kind=AnchorKind.Word), Literal(lit=97)])`

    ...
    """
    kind: AnchorKind

    @override
    def from_pat(pat, state):
        match pat.data:
            case [(Opcode.AT, Opcode.AT_BEGINNING)]:
                return Anchor(AnchorKind.LineBeginning, state=state)

            case [(Opcode.AT, Opcode.AT_END)]:
                return Anchor(AnchorKind.LineEnd, state=state)

            case [(Opcode.AT, Opcode.AT_BEGINNING_STRING)]:
                return Anchor(AnchorKind.StringBeginning, state=state)

            case [(Opcode.AT, Opcode.AT_END_STRING)]:
                return Anchor(AnchorKind.StringEnd, state=state)

            case [(Opcode.AT, Opcode.AT_BOUNDARY)]:
                return Anchor(AnchorKind.Word, state=state)

            case [(Opcode.AT, Opcode.AT_NON_BOUNDARY)]:
                return Anchor(AnchorKind.NonWord, state=state)