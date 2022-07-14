from dataclasses import dataclass, InitVar, KW_ONLY

from regex_hir.nre.parser import SubPattern
from regex_hir.flags import State


# Base class for all the tokens.
@dataclass
class Token:
    _: KW_ONLY # Make `state` be a keyword argument (also making it last)
    state: InitVar[State] = State()

    # The `__post_init__` function is used to clone the state of the "parent" token to the current token.
    def __post_init__(self, state):
        self.state = state

    # Takes the data from a `SubPattern` from the parsed regex and tries to convert it to the parent class.
    def from_pat(pat: SubPattern, state: State):
        raise NotImplementedError

    # Pretty print the HIR tokens.
    def dumps(self, indent=0):
        ignore = ["state"]
        tind = indent

        tind += 4

        def dump_list(lst, tind):
            print(" " * tind, "[", sep="")

            for v in lst:
                if isinstance(v, Token):
                    v.dumps(tind + 4)
                elif isinstance(v, list):
                    dump_list(v, tind + 4)
                else:
                    print(" " * (tind + 4), f"{v}", sep="")

            print(" " * tind, "]", sep="")

        print(" " * indent, f"{self.__class__.__name__}(", sep="")

        # Loop over all the fields, ignore the ones to exclude from printing.
        for k in self.__dataclass_fields__.keys():
            if k in ignore:
                continue

            val = getattr(self, k)

            # `isinstance` also checks subclasses.
            if isinstance(val, Token):
                val.dumps(tind)
            elif isinstance(val, list):
                dump_list(val, tind)
            else:
                print(" " * tind, f"{k}={val}", sep="")

        print(" " * indent, ")", sep="")
