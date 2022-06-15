"""
Vlass of available modifier flags for the regex. (Both inline and local).
"""

__all__ = ["Flags"]

from regex_hir.nre.parser import FLAGS


class Flags:
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

    _flags = [IGNORECASE, LOCALE, MULTILINE, DOTALL, VERBOSE, ASCII, TEMPLATE, UNICODE]

    # Works backwards to find which flags were bitwise or-ed toegether to get the current flag.
    def _find_flags(flag: int):
        found = []
        # A flag can only be used once. or-ing together the same flag twice does not change the value.
        used = [0] * len(Flags._flags)

        def find(flag):
            if flag == 0:
                return
                
            for i, f in enumerate(Flags._flags):
                if f & flag and used[i] != 1:
                    used[i] = 1

                    found.append(f)
                    find(flag - (f & flag))
                
        find(flag)

        return found
