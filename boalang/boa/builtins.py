
from .object import (
    newBuiltinFunction,
    newError,
    newInteger,
    newArray,
    newString,
    BoaObject,
    OBJECT_TYPES,
    OBJECT_TYPE_OBJECT,
    NULL,
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

def builtin_pop(args):
    if len(args) != 1:
        return newError("Wrong number of arguments to pop. Got %d, want 1" % len(args))
    arrObj = args[0]

    if arrObj.objectType != OBJECT_TYPES.OBJECT_TYPE_ARRAY:
        return newError("Argument 1 to pop must be array. Got %s" % arrObj.objectType)

    val = arrObj.value.pop()
    return val

def builtin_print(args):
    if len(args) == 0:
        return newError("print expected at least 1 argument.")
    argsStringified = [str(arg) for arg in args]
    print(*argsStringified)
    return NULL

def builtin_str(args):
    if len(args) != 1:
        return newError("Wrong number of arguments to str. Got %d, want 1" % len(args))
    obj = args[0]

    if obj.objectType == OBJECT_TYPES.OBJECT_TYPE_STRING:
        return newString(obj.value)

    strVal = obj.inspect()
    return newString(strVal)

def builtin_object(args):
    if len(args) != 0:
        return newError("Wrong number of arguments to str. Got %d, want 0" % len(args))
    return BoaObject(OBJECT_TYPE_OBJECT)

B_LEN = 'len'
B_FIRST = 'first'
B_LAST = 'last'
B_REST = 'rest'
B_PUSH = 'push'
B_POP = 'pop'
B_PRINT = 'print'
B_STR = 'str'
B_OBJECT = 'object'

BUILTIN_FUNCTIONS = {
    B_LEN: newBuiltinFunction(B_LEN, builtin_len),
    B_FIRST: newBuiltinFunction(B_FIRST, builtin_first),
    B_LAST: newBuiltinFunction(B_LAST, builtin_last),
    B_REST: newBuiltinFunction(B_REST, builtin_rest),
    B_PUSH: newBuiltinFunction(B_PUSH, builtin_push),
    B_POP: newBuiltinFunction(B_POP, builtin_pop),
    B_PRINT: newBuiltinFunction(B_PRINT, builtin_print),
    B_STR: newBuiltinFunction(B_STR, builtin_str),
    B_OBJECT: newBuiltinFunction(B_OBJECT, builtin_object),
}

BUILTIN_FUNCTION_LIST = [
    B_LEN,
    B_FIRST,
    B_LAST,
    B_REST,
    B_PUSH,
    B_POP,
    B_PRINT,
    B_STR,
    B_OBJECT,
]

def getBuiltinByIndex(index):
    return BUILTIN_FUNCTIONS[BUILTIN_FUNCTION_LIST[index]]
