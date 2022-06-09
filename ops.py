from regex_hir.nre.constants import OPCODES, MIN_REPEAT, MAX_REPEAT, _NamedIntConstant

RE_OPCODES = {
    o.name: o for o in OPCODES
}
# Min and max repeat are not included in the `OPCODES` list.
RE_OPCODES = {
    **RE_OPCODES,
    "MIN_REPEAT": MIN_REPEAT,
    "MAX_REPEAT": MAX_REPEAT,
}

# Puts the opcodes into a class that can be used to match agains re's opcodes.
# Acts as an alternative to having to do `_NamedIntConstant(<opcode>)`.
class Opcode:
    pass

# Apply the opcodes to the class so they can be accessed as a member.
for (name, v) in RE_OPCODES.items():
    setattr(Opcode, name, v)
