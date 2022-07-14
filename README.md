# regex_hir
A high-level intermediate representation of regex in Python.

[PyPi](https://pypi.org/project/regex-hir/) | [Github Source](https://github.com/DexterHill0/regex_hir)

## Installation
Requires Python >=3.10. Also requires the [`unicategories`](https://gitlab.com/ergoithz/unicategories) library for easy access to categorised Unicode characters.

## Description
This library constructs an intermediate representation of the regex AST created by the built-in `re` module. This functions similary to the Rust [`regex_syntax`](https://docs.rs/regex-syntax/latest/regex_syntax/index.html) crate, which was completely the inspiration for this module.  
All of the syntax supported by `re` is supported by this module.

## Usage
```py
import regex_hir

hir = regex_hir.hir(r"[abc]")
hir.dumps()
# CharacterClass(
#     [
#         CharacterRange(start=97, end=97)
#         CharacterRange(start=98, end=98)
#         CharacterRange(start=99, end=99)
#     ]
#     negate=False
#     ignore_case=False
# )
```