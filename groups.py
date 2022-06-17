"""
Contains classes representing the different groups in regex.
"""

__all__ = ["Group", "Backreference", "ConditionalBackreference", "GroupKind"]

import typing
from dataclasses import dataclass, field
from enum import auto

from regex_hir.token import Token
from regex_hir.ops import Opcode
from regex_hir.flags import Flags
from regex_hir.utils import override, Enum


@dataclass
class CaptureGroup:
    index: int

@dataclass
class NamedCaptureGroup:
    index: int
    name: str


class GroupKind(Enum):
    """
    The different kinds of regex groups.
    - `Group`: `(...)`
    - `Atomic`: `(?>...)`
    - `Named`: `(?P<foo>...)`

    - `NonCapturing`: `(?:...)`
        - Note: A non-capture group without modifier flags is unpacked during parsing.
    """
    Group = CaptureGroup
    Named = NamedCaptureGroup
    NonCapturing = auto()
    Atomic = auto()


@dataclass
class Backreference:
    """
    Backreference to a capture group. (`\\1`, `\\2`, ...)

    - `hir(r"(a)\\1")` -> `Patterns(pats=[Group(pat=Literal(lit='a'), kind=GroupKind.CaptureGroup(index=1), flags=[]), Backreference(index=1)])`
    """
    index: int

@dataclass
class ConditionalBackreference:
    """
    Conditional capture group. (`(a)(?(1)b|c)`)
    - `hir(r"(a)(?(1)b|c)")` -> `Patterns(pats=[Group(pat=Literal(lit='a'), kind=GroupKind.CaptureGroup(index=1), flags=[]), ConditionalBackreference(index=1, true=Literal(lit='b'), false=Literal(lit='c'))])`
    """
    index: int
    # Represents the two branches the group can take.
    true: typing.Any
    false: typing.Any


# Returns the name of the capture group if it is a named capture group.
def get_named_group(state, index):
    vals = list(state.groupdict.values())
    if index in vals:
        return list(state.groupdict.keys())[vals.index(index)]


@dataclass
class Group(Token):
    """
    Represents any form of regex group.
    - `hir(r"(a)")` -> `Group(pat=Literal(lit='a'), kind=GroupKind.CaptureGroup(index=1))`
    - `hir(r"(?P<foo>a)")` -> `Group(pat=Literal(lit='a'), kind=GroupKind.NamedCaptureGroup(index=1, name="foo"))`
    
    ...
    """
    pat: typing.Any
    kind: GroupKind
    
    flags: list[Flags] = field(default_factory=list)

    @override
    def from_pat(pat):
        match pat.data:
            case [(Opcode.SUBPATTERN, (index, add_flags, del_flags, pat))]:
                hpat = pat.to_hir()

                # Non-capturing group (only "visible" if local modifier flags are set)
                if index is None:
                    add = Flags._find_flags(add_flags)
                    # Negate the del flags as they are techincally deleting the flag.
                    _del = list(map(lambda x: -x, Flags._find_flags(del_flags)))
                    add.extend(_del)

                    return Group(hpat, GroupKind.NonCapturing, flags=add)

                if name := get_named_group(pat.state, index):
                    return Group(hpat, GroupKind.Named(index, name))

                return Group(hpat, GroupKind.Group(index))

            case [(Opcode.ATOMIC_GROUP, pat)]:
                return Group(pat.to_hir(), GroupKind.Atomic)

            case [(Opcode.GROUPREF, index)]:
                return Backreference(index)

            case [(Opcode.GROUPREF_EXISTS, (index, true, false))]:
                return ConditionalBackreference(index, true.to_hir(), false.to_hir())