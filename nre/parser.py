import sys

if sys.version_info >= (3, 11):
    from re._parser import *
else:
    from sre_parse import *