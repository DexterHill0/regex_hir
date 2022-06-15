from regex_hir.nre.parser import SubPattern

# Base class for all the tokens.
class Token:

    # Takes the data from a `SubPattern` from the parsed regex and tries to convert it to the parent class.
    def from_pat(pat: SubPattern):
        raise NotImplementedError