from enum import Enum as _Enum

# Basic override decorator to indicate the function is an override and not a plain function.
def override(f):
    return f

# Unicode `ord()`.
def uord(char):
    if len(char) > 1:
        return (ord(char[0]), ord(char[1]))
    
    return (ord(char), None)

# Wrapper enum class to allow for calling enum mebers.
class Enum(_Enum):
    def __call__(self, *args, **kwargs):
        return self.value(*args, **kwargs)
    
    def __repr__(self):
        return self.__str__()

    def __init__(self, *args):
        super(Enum, self).__init__(*args)

        # Constructs a new `__repr__` on instanceable enum members so it returns the name of the enum first.
        def __new__(cls):
            return f"{self.__class__.__name__}.{cls.__orepr__()}"

        try:
            self._value_.__orepr__ = self._value_.__repr__
            self._value_.__repr__ = __new__
        except AttributeError:
            pass