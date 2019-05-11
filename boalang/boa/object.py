
from .util import DictLikeStruct

OBJECT_TYPE_INT = 'OBJECT_TYPE_INT'
OBJECT_TYPE_BOOLEAN = 'OBJECT_TYPE_BOOLEAN'
OBJECT_TYPE_NULL = 'OBJECT_TYPE_NULL'
OBJECT_TYPE_RETURN_VALUE = 'OBJECT_TYPE_RETURN_VALUE'

class NoSuchObjectTypeError(Exception): pass

class ObjectInstantiationError(Exception): pass

class BoaObjectType(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '[%s]' % self.name

OBJECT_TYPES = DictLikeStruct({
    OBJECT_TYPE_INT: BoaObjectType(OBJECT_TYPE_INT),
    OBJECT_TYPE_BOOLEAN: BoaObjectType(OBJECT_TYPE_BOOLEAN),
    OBJECT_TYPE_NULL: BoaObjectType(OBJECT_TYPE_NULL),
    OBJECT_TYPE_RETURN_VALUE: BoaObjectType(OBJECT_TYPE_RETURN_VALUE),
})

def newObject(typName, *args):
    if typName not in OBJECT_TYPES:
        raise NoSuchObjectTypeError("No such object: %s" % typName)
    if typName not in OBJECT_CONSTRUCTORS:
        raise ObjectInstantiationError("Not allowed: %s" % typName)

    return OBJECT_CONSTRUCTORS[typName](*args)

def newInteger(i):
    return newObject(OBJECT_TYPE_INT, i)

def newReturnValue(obj):
    return newObject(OBJECT_TYPE_RETURN_VALUE, obj)

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

class BoaBoolean(BoaObject):
    def __init__(self, value):
        super(BoaBoolean, self).__init__(OBJECT_TYPES.OBJECT_TYPE_BOOLEAN)
        self.value = value

    def inspect(self):
        return "%s" % ("true" if self.value else "false")

class BoaNull(BoaObject):
    def __init__(self):
        super(BoaNull, self).__init__(OBJECT_TYPES.OBJECT_TYPE_NULL)

    def inspect(self):
        return "null"

class BoaReturnValue(BoaObject):
    def __init__(self, value):
        super(BoaReturnValue, self).__init__(OBJECT_TYPES.OBJECT_TYPE_RETURN_VALUE)
        self.value = value

    def inspect(self):
        return self.value.inspect()

NULL = BoaNull()
TRUE = BoaBoolean(True)
FALSE = BoaBoolean(False)

OBJECT_CONSTRUCTORS = DictLikeStruct({
    OBJECT_TYPE_INT: BoaInteger,
    OBJECT_TYPE_RETURN_VALUE: BoaReturnValue,
})
