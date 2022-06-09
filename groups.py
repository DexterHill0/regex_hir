"""
Contains classes representing the different groups in regex.
"""

__all__ = ["Group", "Backreference", "ConditionalBackreference", "GroupKind", "GroupFlags"]

import typing
from dataclasses import dataclass, field

from regex_hir.token import Token
from regex_hir.ops import Opcode
from regex_hir.utils import override
from regex_hir.nre.parser import FLAGS


class GroupFlags:
    """
    Available modifier flags for non-capturing groups.
    """

    IGNORECASE = FLAGS["i"]
    LOCALE = FLAGS["L"]
    MULTILINE = FLAGS["m"]
    DOTALL = FLAGS["s"]
    VERBOSE = FLAGS["x"]
    ASCII = FLAGS["a"]
    TEMPLATE = FLAGS["t"]
    UNICODE = FLAGS["u"]

    _flags = [IGNORECASE, LOCALE, MULTILINE, DOTALL, VERBOSE, ASCII, TEMPLATE, UNICODE]

    # Works backwards to find which flags were bitwise or-ed toegether to get the current flag.
    def _find_flags(flag: int):
        found = []
        # A flag can only be used once. or-ing together the same flag twice does not change the value.
        used = [0] * len(GroupFlags._flags)

        def find(flag):
            if flag == 0:
                return
                
            for i, f in enumerate(GroupFlags._flags):
                if f & flag and used[i] != 1:
                    used[i] = 1

                    found.append(f)
                    find(flag - (f & flag))
                
        find(flag)

        return found


@dataclass
class CaptureGroup:
    """
    Plain capture group. Every new group is given a new index. `(...)`
    """

    index: int

@dataclass
class AtomicGroup:
    """
    A form of non-capturing group. (`(?>...)`)
    """

@dataclass
class NamedCaptureGroup:
    """
    Capture group with a specified name. (`(?P<foo>...)`) 
    """

    index: int
    name: str

@dataclass
class NonCaptureGroup:
    """
    Group that does not capture.\n
    Note: A plain non-capture group (`(?:a)`) is unpacked during parsing, but if there are group modifier flags (`(?i:a)`), it stays as a non-capture group.
    """

class GroupKind:
    """
    The different kinds of regex groups.
    """

    Group = CaptureGroup
    Atomic = AtomicGroup
    Named = NamedCaptureGroup
    NonCapturing = NonCaptureGroup


@dataclass
class Backreference:
    """
    Backreference to a capture group. (`\\1`, `\\2`, ...)

    - `hir(r"(a)\\1")` -> `Patterns(pats=[Group(pat=Literal(lit='a'), kind=CaptureGroup(index=1)), Literal(lit='\\'), Literal(lit='1')])`
    """

    index: int

@dataclass
class ConditionalBackreference:
    """
    Conditional capture group. (`(a)(?(1)b|c)`)
    - `hir(r"(a)(?(1)b|c)")` -> `Patterns(pats=[Group(pat=Literal(lit='x'), kind=CaptureGroup(index=1)), ConditionalBackreference(index=1, true=Literal(lit='a'), false=Literal(lit='b'))])`
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
    - `hir(r"(a)")` -> `Group(pat=Literal(lit='a'), kind=CaptureGroup(index=1))`
    - `hir(r"(?P<foo>a)")` -> `Group(pat=Literal(lit='a'), kind=NamedCaptureGroup(index=1, name="foo"))`\n
    ...
    """

    pat: typing.Any
    kind: GroupKind
    
    flags: list[GroupFlags] = field(default_factory=list)

    @override
    def from_pat(pat):
        match pat.data:
            case [(Opcode.SUBPATTERN, (index, add_flags, del_flags, pat))]:
                hpat = pat.to_hir()

                add = GroupFlags._find_flags(add_flags)
                # Negate the del flags as they are techincally deleting the flag.
                _del = list(map(lambda x: -x, GroupFlags._find_flags(del_flags)))
                add.extend(_del)

                if index is None:
                    return Group(hpat, GroupKind.NonCapturing(), flags=add)

                if name := get_named_group(pat.state, index):
                    return Group(hpat, GroupKind.Named(index, name))

                return Group(hpat, GroupKind.Group(index))

            case [(Opcode.ATOMIC_GROUP, pat)]:
                return Group(pat.to_hir(), GroupKind.Atomic())

            case [(Opcode.GROUPREF, index)]:
                return Backreference(index)

            case [(Opcode.GROUPREF_EXISTS, (index, true, false))]:
                return ConditionalBackreference(index, true.to_hir(), false.to_hir())