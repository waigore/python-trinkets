
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
    elif arg.objectType == OBJECT_TYPES.OBJECT_TYPE_ARRAY:
        return newInteger(len(arg.value))
    else:
        return newError("Argument to len not supported. Got %s" % arg.objectType)

def builtin_first(args):
    if len(args) != 1:
        return newError("Wrong number of arguments to first. Got %d, want 1" % len(args))
    arg = args[0]
    try:
        if arg.objectType == OBJECT_TYPES.OBJECT_TYPE_STRING:
            return newString(arg.value[0])
        elif arg.objectType == OBJECT_TYPES.OBJECT_TYPE_ARRAY:
            return arg.value[0]
        else:
            return newError("Argument to first not supported. Got %s" % arg.objectType)
    except:
        return newError("Sequence index error")

def builtin_last(args):
    if len(args) != 1:
        return newError("Wrong number of arguments to last. Got %d, want 1" % len(args))
    arg = args[0]
    try:
        if arg.objectType == OBJECT_TYPES.OBJECT_TYPE_STRING:
            return newString(arg.value[-1])
        elif arg.objectType == OBJECT_TYPES.OBJECT_TYPE_ARRAY:
            return arg.value[-1]
        else:
            return newError("Argument to last not supported. Got %s" % arg.objectType)
    except:
        return newError("Sequence index error")

def builtin_print(args):
    if len(args) == 0:
        return newError("print expected at least 1 argument.")
    inspected = [arg.inspect() for arg in args]
    print(*inspected)

BUILTIN_FUNCTIONS = {
    'len': newBuiltinFunction('len', builtin_len),
    'first': newBuiltinFunction('first', builtin_first),
    'last': newBuiltinFunction('last', builtin_last),
    'print': newBuiltinFunction('print', builtin_print),
}
