
from .object import (
    newBuiltinFunction,
    newError,
    newInteger,
    OBJECT_TYPES,
)

def builtin_len(args):
    if len(args) != 1:
        return newError("Wrong number of arguments to len. Got %d, want 1" % len(args))
    arg = args[0]
    if arg.objectType == OBJECT_TYPES.OBJECT_TYPE_STRING:
        return newInteger(len(arg.value))
    else:
        return newError("Argument to len not supported. Got %s" % arg.objectType)

def builtin_print(args):
    if len(args) == 0:
        return newError("print expected at least 1 argument.")
    inspected = [arg.inspect() for arg in args]
    print(*inspected)

BUILTIN_FUNCTIONS = {
    'len': newBuiltinFunction('len', builtin_len),
    'print': newBuiltinFunction('print', builtin_print),
}
