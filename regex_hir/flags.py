"""
Class of available modifier flags for the regex. (Both inline and local).
"""

__all__ = ["Flags", "State"]

from enum import IntFlag
from dataclasses import dataclass, field

from regex_hir.nre.parser import FLAGS


class Flags(IntFlag):
    """
    Available modifier flags.
    """
    IGNORECASE = FLAGS["i"]
    LOCALE = FLAGS["L"]
    MULTILINE = FLAGS["m"]
    DOTALL = FLAGS["s"]
    VERBOSE = FLAGS["x"]
    ASCII = FLAGS["a"]
    TEMPLATE = FLAGS["t"]
    UNICODE = FLAGS["u"]

    # Works backwards to find which flags were bitwise or-ed toegether to get the current flag.
    def _find_flags(flag: int):
        flags = Flags._member_map_.values()

        found = []
        # A flag can only be used once. or-ing together the same flag twice does not change the value.
        used = [0] * len(flags)

        def find(flag):
            if flag == 0:
                return []
                
            for i, f in enumerate(flags):
                if f & flag and used[i] != 1:
                    used[i] = 1

                    found.append(f)
                    find(flag - (f & flag))
                
        find(flag)

        return found

# Holds the current state (flags) of the different HIR token.
# Really only important for groups and tokens the rely on different flags, like char classes.
@dataclass
class State:
    flags: set[Flags] = field(default_factory=set)

    def has_flag(self, flag: int) -> bool:
        """
        Returns true if the current state includes the given flag.
        """
        return flag in self.flags

    def _set_flags(self, flags):
        self.flags = flags

    def _clone(self):
        # `copy()` creates a real copy of the set (no reference oddity)
        return State(flags=self.flags.copy())

    def _update_flags(self, ad, dl):
        if ad is None and dl is None:
            return self
            
        # Update flags on a new class so it doesn't change the current class.
        new = self._clone()
        curr = new.flags

        # Add the enabled flags to the current state.
        # Ignores any duplicate flags (hence sets).
        curr.update(Flags._find_flags(ad))
        # Relative complement of both sets to remove any flags that are in `del`. 
        curr = curr - set(Flags._find_flags(dl))

        new._set_flags(curr)

        return new