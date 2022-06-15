# Basic override decorator to indicate the function is an override and not a plain function.
def override(f):
    return f

# Unicode `ord()`.
def uord(char):
    if len(char) > 1:
        return (ord(char[0]), ord(char[1]))
    
    return (ord(char), None)