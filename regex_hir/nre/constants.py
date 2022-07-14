import sys

if sys.version_info >= (3, 11):
    # `_NamedIntConstant` not included in wildcard import.
    from re._constants import _NamedIntConstant
    from re._constants import *
else:
    from sre_constants import _NamedIntConstant
    from sre_constants import *