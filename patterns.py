"""
Contains a class representing a regex with multiple consecutive patterns.
"""

__all__ = ["Patterns"]

import typing
from dataclasses import dataclass

from regex_hir.token import Token
from regex_hir.utils import override


@dataclass
class Patterns(Token):
    """
    Represents multiple consecutive patterns.
    - `hir(r"ab")` -> `Patterns(pats=[Literal(lit=97), Literal(lit=98)])`

    ...
    """
    pats: list[typing.Any]
    
    @override
    def from_pat(pat, state):
        # If there is only 1 pattern then it returns `None` so the `to_hir()` loop moves on to the next token.
        # Otherwise if there's more than 1 consecutive pattern then it maps all of them to HIR tokens and constructs a `Patterns`.
        if len(pat.data) <= 1:
            return
        else:
            return Patterns(
                [pat.get(i).to_hir(state) for i in range(len(pat.data))],
                state=state,
            )

    def __getitem__(self, index: int) -> typing.Any:
        return self.pats[index]