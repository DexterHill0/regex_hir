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