
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

BUILTIN_FUNCTIONS = {
    'len': newBuiltinFunction('len', builtin_len),
}
