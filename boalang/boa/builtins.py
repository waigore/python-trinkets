
from .object import (
    newBuiltinFunction,
    newError,
    newInteger,
    newArray,
    newString,
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

def builtin_rest(args):
    if len(args) != 1:
        return newError("Wrong number of arguments to rest. Got %d, want 1" % len(args))
    arg = args[0]

    if arg.objectType == OBJECT_TYPES.OBJECT_TYPE_STRING:
        return newString(arg.value[1:])
    elif arg.objectType == OBJECT_TYPES.OBJECT_TYPE_ARRAY:
        return newArray(arg.value[1:])
    else:
        return newError("Argument to last not supported. Got %s" % arg.objectType)

def builtin_push(args):
    if len(args) < 2:
        return newError("Wrong number of arguments to push. Got %d, want >=2" % len(args))
    arrObj = args[0]
    objs = args[1:]

    if arrObj.objectType != OBJECT_TYPES.OBJECT_TYPE_ARRAY:
        return newError("Argument 1 to push must be array. Got %s" % arrObj.objectType)

    #newArrVal = arrObj.value + objs
    #return newArray(newArrVal)
    arrObj.value.extend(objs)
    return arrObj

def builtin_print(args):
    if len(args) == 0:
        return newError("print expected at least 1 argument.")
    argsStringified = [str(arg) for arg in args]
    print(*argsStringified)
    return NULL

BUILTIN_FUNCTIONS = {
    'len': newBuiltinFunction('len', builtin_len),
    'first': newBuiltinFunction('first', builtin_first),
    'last': newBuiltinFunction('last', builtin_last),
    'rest': newBuiltinFunction('rest', builtin_rest),
    'push': newBuiltinFunction('push', builtin_push),
    'print': newBuiltinFunction('print', builtin_print),
}
