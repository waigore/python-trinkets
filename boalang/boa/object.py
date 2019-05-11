
from .util import DictLikeStruct

OBJECT_TYPE_INT = 'OBJECT_TYPE_INT'
OBJECT_TYPE_BOOLEAN = 'OBJECT_TYPE_BOOLEAN'
OBJECT_TYPE_STRING = 'OBJECT_TYPE_STRING'
OBJECT_TYPE_NULL = 'OBJECT_TYPE_NULL'
OBJECT_TYPE_FUNCTION = 'OBJECT_TYPE_FUNCTION'
OBJECT_TYPE_BUILTIN_FUNCTION = 'OBJECT_TYPE_BUILTIN_FUNCTION'
OBJECT_TYPE_RETURN_VALUE = 'OBJECT_TYPE_RETURN_VALUE'
OBJECT_TYPE_ERROR = 'OBJECT_TYPE_ERROR'

class NoSuchObjectTypeError(Exception): pass

class ObjectInstantiationError(Exception): pass

class BoaObjectType(object):
    def __init__(self, name, shortName):
        self.name = name
        self.shortName = shortName

    def __repr__(self):
        return '[%s]' % self.shortName

OBJECT_TYPES = DictLikeStruct({
    OBJECT_TYPE_INT: BoaObjectType(OBJECT_TYPE_INT, "int"),
    OBJECT_TYPE_BOOLEAN: BoaObjectType(OBJECT_TYPE_BOOLEAN, "boolean"),
    OBJECT_TYPE_STRING: BoaObjectType(OBJECT_TYPE_STRING, "string"),
    OBJECT_TYPE_NULL: BoaObjectType(OBJECT_TYPE_NULL, "null"),
    OBJECT_TYPE_RETURN_VALUE: BoaObjectType(OBJECT_TYPE_RETURN_VALUE, "returnValue"),
    OBJECT_TYPE_ERROR: BoaObjectType(OBJECT_TYPE_ERROR, "error"),
    OBJECT_TYPE_FUNCTION: BoaObjectType(OBJECT_TYPE_FUNCTION, "function"),
    OBJECT_TYPE_BUILTIN_FUNCTION: BoaObjectType(OBJECT_TYPE_BUILTIN_FUNCTION, "builtinFunction"),
})

def newObject(typName, *args):
    if typName not in OBJECT_TYPES:
        raise NoSuchObjectTypeError("No such object: %s" % typName)
    if typName not in OBJECT_CONSTRUCTORS:
        raise ObjectInstantiationError("Not allowed: %s" % typName)

    return OBJECT_CONSTRUCTORS[typName](*args)

def newInteger(i):
    return newObject(OBJECT_TYPE_INT, i)

def newString(s):
    return newObject(OBJECT_TYPE_STRING, s)

def newReturnValue(obj):
    return newObject(OBJECT_TYPE_RETURN_VALUE, obj)

def newError(msg):
    return newObject(OBJECT_TYPE_ERROR, msg)

def newFunction(params, body, env):
    return newObject(OBJECT_TYPE_FUNCTION, params, body, env)

def newBuiltinFunction(name, func):
    return newObject(OBJECT_TYPE_BUILTIN_FUNCTION, name, func)

class BoaObject(object):
    def __init__(self, typ):
        self.objectType = typ

    def inspect(self):
        pass

class BoaInteger(BoaObject):
    def __init__(self, value):
        super(BoaInteger, self).__init__(OBJECT_TYPES.OBJECT_TYPE_INT)
        self.value = value

    def inspect(self):
        return "%d" % (self.value)

class BoaString(BoaObject):
    def __init__(self, value):
        super(BoaString, self).__init__(OBJECT_TYPES.OBJECT_TYPE_STRING)
        self.value = value

    def inspect(self):
        return '"%s"' % (self.value)

class BoaBoolean(BoaObject):
    def __init__(self, value):
        super(BoaBoolean, self).__init__(OBJECT_TYPES.OBJECT_TYPE_BOOLEAN)
        self.value = value

    def inspect(self):
        return "%s" % ("true" if self.value else "false")

class BoaNull(BoaObject):
    def __init__(self):
        super(BoaNull, self).__init__(OBJECT_TYPES.OBJECT_TYPE_NULL)
        self.value = None

    def inspect(self):
        return "null"

class BoaReturnValue(BoaObject):
    def __init__(self, value):
        super(BoaReturnValue, self).__init__(OBJECT_TYPES.OBJECT_TYPE_RETURN_VALUE)
        self.value = value

    def inspect(self):
        return self.value.inspect()

class BoaFunction(BoaObject):
    def __init__(self, parameters, body, env):
        super(BoaFunction, self).__init__(OBJECT_TYPES.OBJECT_TYPE_FUNCTION)
        self.parameters = parameters #list of Identifiers
        self.body = body #BlockStatement
        self.env = env #Environment

    def inspect(self):
        return 'fn(%s) {%s}' % ([str(p) for p in self.parameters], str(self.body))

class BoaBuiltinFunction(BoaObject):
    def __init__(self, name, func):
        super(BoaBuiltinFunction, self).__init__(OBJECT_TYPES.OBJECT_TYPE_BUILTIN_FUNCTION)
        self.name = name
        self.func = func

    def inspect(self):
        return '[builtin]%s()' % (self.name)

class BoaError(BoaObject):
    def __init__(self, value):
        super(BoaError, self).__init__(OBJECT_TYPES.OBJECT_TYPE_ERROR)
        self.value = value

    @property
    def message(self):
        return self.value

    def inspect(self):
        return 'ERROR:' + self.value

NULL = BoaNull()
TRUE = BoaBoolean(True)
FALSE = BoaBoolean(False)

OBJECT_CONSTRUCTORS = DictLikeStruct({
    OBJECT_TYPE_INT: BoaInteger,
    OBJECT_TYPE_RETURN_VALUE: BoaReturnValue,
    OBJECT_TYPE_ERROR: BoaError,
    OBJECT_TYPE_FUNCTION: BoaFunction,
    OBJECT_TYPE_BUILTIN_FUNCTION: BoaBuiltinFunction,
    OBJECT_TYPE_STRING: BoaString,
})
