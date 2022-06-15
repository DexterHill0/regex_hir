"""High-level intermediate representation (HIR) of re's regex AST.

Provides a more readable and understandable representation of the regex AST which makes it easier to parse.

For more detailed information, see the documentation at:
- https://github.com/DexterHill0/regex_hir


Copyright 2022 Dexter Hill

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

__all__ = ["hir", "hir_from"]
__version__ = "0.0.1"
__author__ = "@dexterhill0"


import typing

from regex_hir.nre.parser import SubPattern as __SubPattern, parse as __parse
from regex_hir.literal import *
from regex_hir.groups import *
from regex_hir.patterns import *
from regex_hir.char_class import *


# All the HIR tokens (ordered in an approximate guess as to which ones are used more commonly).
__ALL_TOKENS = [
    # Not really a token, but as `Patterns` matches consecutive patterns it comes first as that is most common.
    Patterns,
    
    Group,
    CharacterClass,
    Literal,
]

# A function which can be called on a `SubPattern` to convert it to an HIR token.
def to_hir(self: __SubPattern) -> typing.Any:
    for token in __ALL_TOKENS:
        if m := token.from_pat(self):
            return m

setattr(__SubPattern, "to_hir", to_hir)

# Method that always returns a `SubPattern` when indexing.
# The default implementation of `__getitem__` in `SubPattern` only returns a `SubPattern` when indexed with a slice, and not an integer.
def get(self: __SubPattern, index: int) -> __SubPattern:
    return self[index:index+1]

setattr(__SubPattern, "get", get)


def hir(regex: str) -> typing.Any:
    """
    Takes a regex string, and converts it from re's regex AST to a higher intermediate representation using data classes.
    """

    pattern = __parse(regex)
    return pattern.to_hir()

def hir_from(pattern: __SubPattern) -> typing.Any:
    """
    Takes a parsed regex string (`SubPattern`), and converts it to a higher intermediate representation using data classes.
    """

    return pattern.to_hir()