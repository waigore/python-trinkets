
from .util import DictLikeStruct

OBJECT_TYPE_OBJECT = 'OBJECT_TYPE_OBJECT'
OBJECT_TYPE_INT = 'OBJECT_TYPE_INT'
OBJECT_TYPE_BOOLEAN = 'OBJECT_TYPE_BOOLEAN'
OBJECT_TYPE_STRING = 'OBJECT_TYPE_STRING'
OBJECT_TYPE_ARRAY = 'OBJECT_TYPE_ARRAY'
OBJECT_TYPE_ITERATOR = 'OBJECT_TYPE_ITERATOR'
OBJECT_TYPE_HASH = 'OBJECT_TYPE_HASH'
OBJECT_TYPE_HASH_PAIR = 'OBJECT_TYPE_HASH_PAIR'
OBJECT_TYPE_HASH_ITERATOR = 'OBJECT_TYPE_HASH_ITERATOR'
OBJECT_TYPE_NULL = 'OBJECT_TYPE_NULL'
OBJECT_TYPE_FUNCTION = 'OBJECT_TYPE_FUNCTION'
OBJECT_TYPE_METHOD = 'OBJECT_TYPE_METHOD'
OBJECT_TYPE_CLOSURE = 'OBJECT_TYPE_CLOSURE'
OBJECT_TYPE_COMPILED_FUNCTION = 'OBJECT_TYPE_COMPILED_FUNCTION'
OBJECT_TYPE_BUILTIN_FUNCTION = 'OBJECT_TYPE_BUILTIN_FUNCTION'
OBJECT_TYPE_BUILTIN_METHOD = 'OBJECT_TYPE_BUILTIN_METHOD'
OBJECT_TYPE_RETURN_VALUE = 'OBJECT_TYPE_RETURN_VALUE'
OBJECT_TYPE_CONTINUE = 'OBJECT_TYPE_CONTINUE'
OBJECT_TYPE_BREAK = 'OBJECT_TYPE_BREAK'
OBJECT_TYPE_ERROR = 'OBJECT_TYPE_ERROR'
OBJECT_TYPE_CLASS = 'OBJECT_TYPE_CLASS'
OBJECT_TYPE_CLASS_INSTANCE = 'OBJECT_TYPE_CLASS_INSTANCE'
OBJECT_TYPE_COMPILED_CLASS = 'OBJECT_TYPE_COMPILED_CLASS'

class NoSuchObjectTypeError(Exception): pass

class ObjectInstantiationError(Exception): pass

class CannotGetAttributeError(Exception): pass

class CannotSetAttributeError(Exception): pass

class BoaObjectType(object):
    def __init__(self, name, shortName, isHashable=False, isIterable=False):
        self.name = name
        self.shortName = shortName
        self.isHashable = isHashable
        self.isIterable = isIterable

    def __repr__(self):
        return '[%s]' % self.shortName

OBJECT_TYPES = DictLikeStruct({
    OBJECT_TYPE_OBJECT: BoaObjectType(OBJECT_TYPE_OBJECT, "object"),
    OBJECT_TYPE_INT: BoaObjectType(OBJECT_TYPE_INT, "int", isHashable=True),
    OBJECT_TYPE_BOOLEAN: BoaObjectType(OBJECT_TYPE_BOOLEAN, "boolean", isHashable=True),
    OBJECT_TYPE_STRING: BoaObjectType(OBJECT_TYPE_STRING, "string", isHashable=True, isIterable=True),
    OBJECT_TYPE_ARRAY: BoaObjectType(OBJECT_TYPE_ARRAY, "array", isIterable=True),
    OBJECT_TYPE_HASH: BoaObjectType(OBJECT_TYPE_HASH, "hash", isIterable=True),
    OBJECT_TYPE_HASH_PAIR: BoaObjectType(OBJECT_TYPE_HASH_PAIR, "hashPair"),
    OBJECT_TYPE_ITERATOR: BoaObjectType(OBJECT_TYPE_ITERATOR, "iterator"),
    OBJECT_TYPE_HASH_ITERATOR: BoaObjectType(OBJECT_TYPE_HASH_ITERATOR, "hashIterator"),
    OBJECT_TYPE_NULL: BoaObjectType(OBJECT_TYPE_NULL, "null"),
    OBJECT_TYPE_RETURN_VALUE: BoaObjectType(OBJECT_TYPE_RETURN_VALUE, "returnValue"),
    OBJECT_TYPE_BREAK: BoaObjectType(OBJECT_TYPE_BREAK, "break"),
    OBJECT_TYPE_CONTINUE: BoaObjectType(OBJECT_TYPE_CONTINUE, "continue"),
    OBJECT_TYPE_ERROR: BoaObjectType(OBJECT_TYPE_ERROR, "error"),
    OBJECT_TYPE_FUNCTION: BoaObjectType(OBJECT_TYPE_FUNCTION, "function"),
    OBJECT_TYPE_METHOD: BoaObjectType(OBJECT_TYPE_METHOD, "method"),
    OBJECT_TYPE_COMPILED_FUNCTION: BoaObjectType(OBJECT_TYPE_COMPILED_FUNCTION, "compiledFunction"),
    OBJECT_TYPE_BUILTIN_FUNCTION: BoaObjectType(OBJECT_TYPE_BUILTIN_FUNCTION, "builtinFunction"),
    OBJECT_TYPE_BUILTIN_METHOD: BoaObjectType(OBJECT_TYPE_BUILTIN_METHOD, "builtinMethod"),
    OBJECT_TYPE_CLOSURE: BoaObjectType(OBJECT_TYPE_CLOSURE, "closure"),
    OBJECT_TYPE_CLASS: BoaObjectType(OBJECT_TYPE_CLASS, "class"),
    OBJECT_TYPE_COMPILED_CLASS: BoaObjectType(OBJECT_TYPE_COMPILED_CLASS, "compiledClass"),
    OBJECT_TYPE_CLASS_INSTANCE: BoaObjectType(OBJECT_TYPE_CLASS_INSTANCE, "classInstance"),
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

def newArray(els):
    return newObject(OBJECT_TYPE_ARRAY, els)

def newHash(pairs):
    return newObject(OBJECT_TYPE_HASH, pairs)

def newReturnValue(obj):
    return newObject(OBJECT_TYPE_RETURN_VALUE, obj)

def newError(msg):
    return newObject(OBJECT_TYPE_ERROR, msg)

def newFunction(params, body, env):
    return newObject(OBJECT_TYPE_FUNCTION, params, body, env)

def newMethod(instance, params, body, env):
    return newObject(OBJECT_TYPE_METHOD, instance, params, body, env)

def newClass(name, constructor, methods, env):
    return newObject(OBJECT_TYPE_CLASS, name, constructor, methods, env)

def newClassInstance(clazz):
    return newObject(OBJECT_TYPE_CLASS_INSTANCE, clazz)

def newCompiledFunction(instr, numLocals=0, numParameters=0):
    return newObject(OBJECT_TYPE_COMPILED_FUNCTION, instr, numLocals, numParameters)

def newCompiledClass(name, constructor, methods):
    return newObject(OBJECT_TYPE_COMPILED_CLASS, name, constructor, methods)

def newBuiltinFunction(name, func):
    return newObject(OBJECT_TYPE_BUILTIN_FUNCTION, name, func)

def newClosure(compiledFunction, freeVariables, instance=None, isConstructor=False):
    return newObject(OBJECT_TYPE_CLOSURE, compiledFunction, freeVariables, instance, isConstructor)

class BoaObject(object):
    def __init__(self, typ):
        self.objectType = typ
        self.builtinAttributeGetters = {}
        self.builtinAttributeSetters = {}
        self.attributes = {}

    def inspect(self):
        return '<BoaObject typ=%s>' % (self.objectType)

    def __repr__(self):
        return '<BoaObject typ=%s>' % (self.objectType)

    def defineBuiltinAttribute(self, name, getter=None, setter=None):
        if getter:
            self.builtinAttributeGetters[name] = getter
        if setter:
            self.builtinAttributeSetters[name] = setter

    def defineBuiltinMethod(self, name, func):
        builtinMethod = BoaBuiltinMethod(name, self, func)
        self.defineBuiltinAttribute(name, getter=lambda: builtinMethod)

    def defineAttribute(self, name, val):
        self.attributes[name] = val

    def getAttribute(self, name):
        if name in self.attributes:
            return self.attributes[name]
        elif name in self.builtinAttributeGetters:
            return self.builtinAttributeGetters[name]()
        raise CannotGetAttributeError(name)

    def setAttribute(self, name, val):
        if name in self.attributes:
            self.attributes[name] = val
        elif name in self.builtinAttributeSetters:
            return self.builtinAttributeSetters[name](val)
        else:
            self.defineAttribute(name, val)


    def hashcode(self):
        return hash(self.value)

class BoaClass(BoaObject):
    def __init__(self, name, constructor, methods, env):
        super(BoaClass, self).__init__(OBJECT_TYPES.OBJECT_TYPE_CLASS)
        self.name = name
        self.methods = methods #dict of <name, BoaFunction> entries
        #self.constructors = {0: BoaBuiltinMethod('constructor', self, self.constructor_default)}
        self.constructor = constructor
        self.env = env

    def createInstance(self):
        instance = newClassInstance(self)
        for methodName, unboundMethod in self.methods.items():
            boundMethod = newMethod(instance, unboundMethod.parameters, unboundMethod.body, self.env)
            instance.setAttribute(methodName, boundMethod)
        if self.constructor:
            boundConstructor = newMethod(instance, self.constructor.parameters, self.constructor.body, self.env)
        else:
            boundConstructor = None
        return instance, boundConstructor

    def __repr__(self):
        return "<class %s>" % (self.name)

    def inspect(self):
        return "<class %s>" % (self.name)

class BoaCompiledClass(BoaObject):
    def __init__(self, name, constructor, methods):
        super(BoaCompiledClass, self).__init__(OBJECT_TYPES.OBJECT_TYPE_COMPILED_CLASS)
        self.methods = methods #dict of <name, BoaFunction> entries
        self.constructor = constructor
        self.name = name

    def createInstance(self):
        instance = newClassInstance(self)
        for methodName, unboundMethod in self.methods.items():
            boundMethod = newClosure(unboundMethod.compiledFunction, unboundMethod.freeVariables, instance=instance)
            instance.setAttribute(methodName, boundMethod)
        if self.constructor:
            boundConstructor = newClosure(self.constructor.compiledFunction, self.constructor.freeVariables, instance=instance, isConstructor=True)
        else:
            boundConstructor = None
        return instance, boundConstructor

    def __repr__(self):
        return "<class(compiled) %s>" % (self.name)

    def inspect(self):
        return "<class(compiled) %s>" % (self.name)

class BoaClassInstance(BoaObject):
    def __init__(self, clazz):
        super(BoaClassInstance, self).__init__(OBJECT_TYPES.OBJECT_TYPE_CLASS_INSTANCE)
        self.clazz = clazz

    def __repr__(self):
        return '<classInstance of %s>' % (self.clazz.name)

    def inspect(self):
        return '<classInstance of %s>' % (self.clazz.name)

class BoaInteger(BoaObject):
    def __init__(self, value):
        super(BoaInteger, self).__init__(OBJECT_TYPES.OBJECT_TYPE_INT)
        self.value = value

    def __repr__(self):
        return "%d" % (self.value)

    def inspect(self):
        return "%d" % (self.value)

class BoaString(BoaObject):
    def __init__(self, value):
        super(BoaString, self).__init__(OBJECT_TYPES.OBJECT_TYPE_STRING)
        self.value = value
        self.defineBuiltinAttribute('length', getter=lambda: newInteger(len(self.value)))
        self.defineBuiltinMethod('toUpper', self.method_toUpper)
        self.defineBuiltinMethod('toLower', self.method_toLower)

    def method_toUpper(self, args):
        if len(args) > 0:
            return newError("Wrong number of arguments to <string>.toUpper: got %d, want 0" % (len(args)))
        return newString(self.value.upper())

    def method_toLower(self, args):
        if len(args) > 0:
            return newError("Wrong number of arguments to <string>.toLower: got %d, want 0" % (len(args)))
        return newString(self.value.lower())

    def __iter__(self):
        return BoaCountingIterator(self)

    def __contains__(self, key):
        return key.value in self.value

    def __len__(self):
        return len(self.value)

    def __getitem__(self, key):
        return newString(self.value[key.value])

    def __repr__(self):
        return "%s" % (self.value)

    def inspect(self):
        return '"%s"' % (self.value)

class BoaBoolean(BoaObject):
    def __init__(self, value):
        super(BoaBoolean, self).__init__(OBJECT_TYPES.OBJECT_TYPE_BOOLEAN)
        self.value = value

    def __repr__(self):
        return "%s" % ("true" if self.value else "false")

    def inspect(self):
        return "%s" % ("true" if self.value else "false")

class BoaNull(BoaObject):
    def __init__(self):
        super(BoaNull, self).__init__(OBJECT_TYPES.OBJECT_TYPE_NULL)
        self.value = None

    def __repr__(self):
        return "null"

    def inspect(self):
        return "null"

class BoaReturnValue(BoaObject):
    def __init__(self, value):
        super(BoaReturnValue, self).__init__(OBJECT_TYPES.OBJECT_TYPE_RETURN_VALUE)
        self.value = value

    def __repr__(self):
        return "return %s" % self.value.inspect()

    def inspect(self):
        return "return %s" % self.value.inspect()

class BoaBreak(BoaObject):
    def __init__(self):
        super(BoaBreak, self).__init__(OBJECT_TYPES.OBJECT_TYPE_BREAK)
        self.value = None

    def __repr__(self):
        return "break"

    def inspect(self):
        return "break"

class BoaContinue(BoaObject):
    def __init__(self):
        super(BoaContinue, self).__init__(OBJECT_TYPES.OBJECT_TYPE_CONTINUE)
        self.value = None

    def __repr__(self):
        return "continue"

    def inspect(self):
        return "continue"

class BoaFunction(BoaObject):
    def __init__(self, parameters, body, env):
        super(BoaFunction, self).__init__(OBJECT_TYPES.OBJECT_TYPE_FUNCTION)
        self.parameters = parameters #list of Identifiers
        self.body = body #BlockStatement
        self.env = env #Environment

    def __repr__(self):
        return 'fn(%s) {%s}' % ([str(p) for p in self.parameters], str(self.body))

    def inspect(self):
        return 'fn(%s) {%s}' % ([str(p) for p in self.parameters], str(self.body))

class BoaMethod(BoaObject):
    def __init__(self, instance, parameters, body, env):
        super(BoaMethod, self).__init__(OBJECT_TYPES.OBJECT_TYPE_METHOD)
        self.instance = instance
        self.parameters = parameters
        self.body = body
        self.env = env

    def __repr__(self):
        return '<boaMethod of %s (bound)>' % (self.instance.objectType)

    def inspect(self):
        return '<boaMethod of %s (bound)>' % (self.instance.objectType)

class BoaClosure(BoaObject):
    def __init__(self, compiledFunction, freeVariables, instance=None, isConstructor=False):
        super(BoaClosure, self).__init__(OBJECT_TYPES.OBJECT_TYPE_CLOSURE)
        self.compiledFunction = compiledFunction
        self.freeVariables = freeVariables
        self.instance = instance
        self.isConstructor = isConstructor

    def __repr__(self):
        return '<closure%s %s%s free=[%s]>' % (
            '(constructor)' if self.isConstructor else '',
            self.instance + '.' if self.instance else '',
            self.compiledFunction,
            ', '.join([free.inspect() for free in self.freeVariables])
        )

    def inspect(self):
        return '<closure %s%s free=[%s]>' % (
            self.instance + '.' if self.instance else '',
            self.compiledFunction,
            ', '.join([free.inspect() for free in self.freeVariables])
        )

class BoaBuiltinMethod(BoaObject):
    def __init__(self, name, instance, func, takesEnv=False):
        super(BoaBuiltinMethod, self).__init__(OBJECT_TYPES.OBJECT_TYPE_BUILTIN_METHOD)
        self.name = name
        self.instance = instance
        self.func = func
        self.takesEnv = takesEnv

    def __repr__(self):
        return '<builtinMethod %s of %s (bound)>' % (self.name, self.instance.objectType)

    def inspect(self):
        return '<builtinMethod %s of %s (bound)>' % (self.name, self.instance.objectType)

class BoaCompiledFunction(BoaObject):
    def __init__(self, instr, numLocals, numParameters):
        super(BoaCompiledFunction, self).__init__(OBJECT_TYPES.OBJECT_TYPE_COMPILED_FUNCTION)
        self.instr = instr
        self.value = instr
        self.numLocals = numLocals
        self.numParameters = numParameters

    def __repr__(self):
        return '<compiledFunction (len=%d)>' % (len(self.instr))

    def inspect(self):
        return '<compiledFunction (len=%d)>' % (len(self.instr))

class BoaBuiltinFunction(BoaObject):
    def __init__(self, name, func):
        super(BoaBuiltinFunction, self).__init__(OBJECT_TYPES.OBJECT_TYPE_BUILTIN_FUNCTION)
        self.name = name
        self.func = func

    def __repr__(self):
        return '[builtin]%s()' % (self.name)

    def inspect(self):
        return '[builtin]%s()' % (self.name)

class BoaArray(BoaObject):
    def __init__(self, elements):
        super(BoaArray, self).__init__(OBJECT_TYPES.OBJECT_TYPE_ARRAY)
        self.value = elements
        self.defineBuiltinAttribute('length', getter=lambda: newInteger(len(self.value)))

    def __iter__(self):
        return BoaCountingIterator(self)

    def __contains__(self, key):
        for obj in self.value:
            if obj.value == key.value:
                return True
        return False

    def __len__(self):
        return len(self.value)

    def __getitem__(self, key):
        return self.value[key.value]

    def __setitem__(self, key, val):
        self.value[key.value] = val

    def __repr__(self):
        return '[%s]' % (', '.join([val.inspect() for val in self.value]))

    def inspect(self):
        return '[%s]' % (', '.join([val.inspect() for val in self.value]))

class BoaCountingIterator(BoaObject):
    def __init__(self, iterable):
        super(BoaCountingIterator, self).__init__(OBJECT_TYPES.OBJECT_TYPE_ITERATOR)
        self.iterable = iterable
        self.counter = 0

    def hasNext(self):
        if self.counter >= len(self.iterable):
            return False
        return True

    def __iter__(self):
        return self

    def __next__(self):
        if self.counter >= len(self.iterable):
            raise StopIteration
        val = self.iterable.value[self.counter]
        self.counter += 1
        return val

    def __repr__(self):
        return '<iterator counter=%d>' % (self.counter)

    def inspect(self):
        return '<iterator counter=%d>' % (self.counter)


class BoaHashIterator(BoaObject):
    def __init__(self, hash):
        super(BoaHashIterator, self).__init__(OBJECT_TYPES.OBJECT_TYPE_HASH_ITERATOR)
        self.hash = hash
        self.counter = 0
        self.keySnapshot = list(self.hash.value.keys())

    def hasNext(self):
        if self.counter >= len(self.keySnapshot):
            return False
        return True

    def __iter__(self):
        return self

    def __next__(self):
        if self.counter >= len(self.keySnapshot):
            raise StopIteration
        val = self.hash.value[self.keySnapshot[self.counter]].value
        self.counter += 1
        return val

    def __repr__(self):
        return '<hashiterator counter=%d>' % (self.counter)

    def inspect(self):
        return '<hashiterator counter=%d>' % (self.counter)

class BoaHash(BoaObject):
    def __init__(self, pairs):
        super(BoaHash, self).__init__(OBJECT_TYPES.OBJECT_TYPE_HASH)
        self.value = {}
        for k, v in pairs:
            kHash = k.hashcode()
            self.value[kHash] = BoaHashPair(k, v)
        self.defineBuiltinAttribute('length', getter=lambda: newInteger(len(self.value.keys())))

    def __iter__(self):
        return BoaHashIterator(self)

    def __len__(self):
        return len(self.value.keys())

    def __contains__(self, key):
        keyHash = key.hashcode()
        return keyHash in self.value

    def __getitem__(self, key):
        keyHash = key.hashcode()
        return self.value[keyHash].value

    def __setitem__(self, key, val):
        keyHash = key.hashcode()
        self.value[keyHash] = BoaHashPair(key, val)

    def __repr__(self):
        return '{%s}' % (', '.join([hashPair.inspect() for hashPair in self.value.values()]))

    def inspect(self):
        return '{%s}' % (', '.join([hashPair.inspect() for hashPair in self.value.values()]))

class BoaHashPair(BoaObject):
    def __init__(self, key, val):
        super(BoaHashPair, self).__init__(OBJECT_TYPES.OBJECT_TYPE_HASH_PAIR)
        self.value = val
        self.key = key

    def __repr__(self):
        return '%s: %s' % (self.key.inspect(), self.value.inspect())

    def inspect(self):
        return '%s: %s' % (self.key.inspect(), self.value.inspect())

class BoaError(BoaObject):
    def __init__(self, value):
        super(BoaError, self).__init__(OBJECT_TYPES.OBJECT_TYPE_ERROR)
        self.value = value

    @property
    def message(self):
        return self.value

    def __repr__(self):
        return 'ERROR: ' + self.value

    def inspect(self):
        return 'ERROR: ' + self.value

NULL = BoaNull()
TRUE = BoaBoolean(True)
FALSE = BoaBoolean(False)
BREAK = BoaBreak()
CONTINUE = BoaContinue()

OBJECT_CONSTRUCTORS = DictLikeStruct({
    OBJECT_TYPE_OBJECT: BoaObject,
    OBJECT_TYPE_INT: BoaInteger,
    OBJECT_TYPE_RETURN_VALUE: BoaReturnValue,
    OBJECT_TYPE_ERROR: BoaError,
    OBJECT_TYPE_FUNCTION: BoaFunction,
    OBJECT_TYPE_METHOD: BoaMethod,
    OBJECT_TYPE_BUILTIN_FUNCTION: BoaBuiltinFunction,
    OBJECT_TYPE_STRING: BoaString,
    OBJECT_TYPE_ARRAY: BoaArray,
    OBJECT_TYPE_HASH: BoaHash,
    OBJECT_TYPE_COMPILED_FUNCTION: BoaCompiledFunction,
    OBJECT_TYPE_CLOSURE: BoaClosure,
    OBJECT_TYPE_CLASS: BoaClass,
    OBJECT_TYPE_COMPILED_CLASS: BoaCompiledClass,
    OBJECT_TYPE_CLASS_INSTANCE: BoaClassInstance,
})
