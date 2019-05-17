from .util import DictLikeStruct
from .code import (
    DEFINITIONS,
    OPCONSTANT,
    OPADD,
    OPSUB,
    OPMUL,
    OPDIV,
    OPPOP,
    OPTRUE,
    OPFALSE,
    OPEQ,
    OPNEQ,
    OPGT,
    OPGTEQ,
    OPMINUS,
    OPNOT,
    OPJUMP,
    OPJUMPNOTTRUE,
    OPNULL,
    OPSETGLOBAL,
    OPGETGLOBAL,
    OPARRAY,
    OPHASH,
    OPINDEX,
    OPCALL,
    OPRETURNVALUE,
    OPSETLOCAL,
    OPGETLOCAL,
    OPSETINDEX,
    OPBLOCKCALL,
    OPBLOCKRETURN,
    OPLOOPCALL,
    OPBREAK,
    OPCONTINUE,
    OPITER,
    OPITERHASNEXT,
    OPITERNEXT,
    OPGETBUILTIN,
    readUint16,
    readUint8,
)
from .object import (
    newInteger,
    newString,
    newArray,
    newHash,
    newCompiledFunction,
    OBJECT_TYPES,
    TRUE,
    FALSE,
    NULL,
)
from .builtins import (
    getBuiltinByIndex,
)
from .evaluator import (
    isTruthy,
)

STACK_SIZE = 2048
GLOBALS_SIZE = 65536
MAX_FRAMES = 1024

FRAME_TYPE_FUNCTION = "FUNCTION_FRAME"
FRAME_TYPE_BLOCK = "BLOCK_FRAME"
FRAME_TYPE_LOOP = "LOOP_FRAME"

class BoaVMError(Exception): pass

class Frame(object):
    def __init__(self, frameType, compiledFunction, basePointer):
        self.frameType = frameType
        self.compiledFunction = compiledFunction
        self.ip = 0
        self.basePointer = basePointer

    @property
    def instr(self):
        return self.compiledFunction.value

class VM(object):
    def __init__(self, bytecode):
        self.constants = bytecode.constants
        self.stack = [None]*STACK_SIZE #stack of BoaObjects
        self.globals = [None]*GLOBALS_SIZE
        self.sp = 0
        self.frames = [None]*MAX_FRAMES #stack of Frames
        self.frameIndex = 0

        mainFrame = Frame(FRAME_TYPE_BLOCK, newCompiledFunction(bytecode.instr), 0)
        self.pushFrame(mainFrame)


    @staticmethod
    def newWithGlobalsStore(bytecode, globals):
        vm = VM(bytecode)
        vm.globals = globals
        return vm

    def currentFrame(self):
        return self.frames[self.frameIndex - 1]

    def currentFrameIp(self):
        return self.currentFrame().ip

    def currentFrameType(self):
        return self.currentFrame().frameType

    def currentInstr(self):
        return self.currentFrame().instr

    def incrCurrentFrameIp(self, incr):
        self.currentFrame().ip = self.currentFrame().ip + incr

    def setCurrentFrameIp(self, val):
        self.currentFrame().ip = val

    def pushFrame(self, frame):
        self.frames[self.frameIndex] = frame
        self.frameIndex += 1

    def popLastFrameOfType(self, frameType):
        i = self.frameIndex-1
        currFrameType = self.frames[i].frameType
        while i > 0 and currFrameType != frameType:
            i -= 1
            currFrameType = self.frames[i].frameType
        if currFrameType != frameType:
            return None
        frame = self.frames[i]
        self.frameIndex = i
        return frame

    def popFrame(self):
        self.frameIndex -= 1
        return self.frames[self.frameIndex]

    def stackTop(self):
        if self.sp == 0:
            return None
        return self.stack[self.sp-1]

    def lastPoppedStackEl(self):
        return self.stack[self.sp]

    def inspectStack(self):
        if self.sp == 0:
            return []
        return list(self.stack[0:self.sp])

    def push(self, obj):
        if self.sp >= STACK_SIZE:
            raise BoaVMError("Stack overflow")

        self.stack[self.sp] = obj
        self.sp += 1

    def pop(self):
        obj = self.stack[self.sp-1]
        self.sp -= 1
        return obj

    def run(self):
        #ip = 0
        while self.currentFrameIp() < len(self.currentInstr()):
            incrFrameIp = True
            op = self.currentInstr()[self.currentFrameIp():self.currentFrameIp()+1]
            if op == OPCONSTANT:
                constIndex = readUint16(self.currentInstr()[self.currentFrameIp()+1:])
                self.incrCurrentFrameIp(2)
                #print(constIndex, self.constants, len(self.constants))
                #print(instr[self.currentFrameIp():])
                #print(self.constants)
                self.push(self.constants[constIndex])
            elif op in (OPEQ, OPNEQ, OPGT, OPGTEQ):
                self.executeComparison(op)
            elif op in (OPADD, OPSUB, OPMUL, OPDIV):
                self.executeBinaryOperation(op)
            elif op == OPNOT:
                self.executeNotOperator()
            elif op == OPMINUS:
                self.executeMinusOperator()
            elif op == OPTRUE:
                self.push(TRUE)
            elif op == OPFALSE:
                self.push(FALSE)
            elif op == OPNULL:
                self.push(NULL)
            elif op == OPARRAY:
                numElements = readUint16(self.currentInstr()[self.currentFrameIp()+1:])
                self.incrCurrentFrameIp(2)
                arr = self.buildArray(self.sp-numElements, self.sp)
                self.sp = self.sp - numElements
                self.push(arr)
            elif op == OPHASH:
                numElements = readUint16(self.currentInstr()[self.currentFrameIp()+1:])
                self.incrCurrentFrameIp(2)
                hash = self.buildHash(self.sp-numElements, self.sp)
                self.sp = self.sp - numElements
                self.push(hash)
            elif op == OPINDEX:
                index = self.pop()
                left = self.pop()
                self.executeIndexOperation(left, index)
            elif op == OPPOP:
                self.pop()
            elif op == OPSETGLOBAL:
                globalIndex = readUint16(self.currentInstr()[self.currentFrameIp()+1:])
                self.incrCurrentFrameIp(2)
                self.globals[globalIndex] = self.pop()
            elif op == OPGETGLOBAL:
                globalIndex = readUint16(self.currentInstr()[self.currentFrameIp()+1:])
                self.incrCurrentFrameIp(2)
                self.push(self.globals[globalIndex])
            elif op == OPGETBUILTIN:
                builtinIndex = readUint8(self.currentInstr()[self.currentFrameIp()+1:])
                self.incrCurrentFrameIp(1)
                self.push(getBuiltinByIndex(builtinIndex))
            elif op == OPSETINDEX:
                value = self.pop()
                index = self.pop()
                left = self.pop()
                left[index] = value
            elif op == OPJUMP:
                pos = readUint16(self.currentInstr()[self.currentFrameIp()+1:])
                self.setCurrentFrameIp(pos - 1)
            elif op == OPJUMPNOTTRUE:
                pos = readUint16(self.currentInstr()[self.currentFrameIp()+1:])
                self.incrCurrentFrameIp(2)
                condition = self.pop()
                if not isTruthy(condition):
                    self.setCurrentFrameIp(pos - 1)
            elif op == OPCALL:
                numArgs = readUint8(self.currentInstr()[self.currentFrameIp()+1:])
                self.incrCurrentFrameIp(1)
                self.executeCall(numArgs)
                incrFrameIp = False
            elif op == OPBLOCKCALL:
                self.callBlock()
                incrFrameIp = False
            elif op == OPLOOPCALL:
                numArgs = readUint8(self.currentInstr()[self.currentFrameIp()+1:])
                self.incrCurrentFrameIp(1)
                self.callLoop(numArgs)
                incrFrameIp = False
            elif op == OPSETLOCAL:
                localIndex = readUint8(self.currentInstr()[self.currentFrameIp()+1:])
                self.incrCurrentFrameIp(1)
                frame = self.currentFrame()
                self.stack[frame.basePointer+localIndex] = self.pop()
            elif op == OPGETLOCAL:
                localIndex = readUint8(self.currentInstr()[self.currentFrameIp()+1:])
                self.incrCurrentFrameIp(1)
                frame = self.currentFrame()
                self.push(self.stack[frame.basePointer+localIndex])
            elif op == OPITER:
                iterable = self.pop()
                iterator = iter(iterable)
                self.push(iterator)
            elif op == OPITERHASNEXT:
                iterator = self.pop()
                self.push(TRUE if iterator.hasNext() else FALSE)
            elif op == OPITERNEXT:
                iterator = self.pop()
                try:
                    val = next(iterator)
                    self.push(val)
                except StopIteration:
                    raise BoaVMError("Iterator has no more elements")
            elif op == OPRETURNVALUE:
                returnValue = self.pop()
                frame = self.popLastFrameOfType(FRAME_TYPE_FUNCTION)
                if frame is not None: #if frame is None then the effect is the same as a NOP
                    self.sp = frame.basePointer - 1
                    self.push(returnValue)
            elif op == OPBLOCKRETURN:
                returnValue = self.pop()
                frame = self.popFrame()
                self.sp = frame.basePointer - 1
                self.push(returnValue)
            elif op == OPCONTINUE:
                frame = self.popLastFrameOfType(FRAME_TYPE_LOOP)
                if frame is not None:
                    self.sp = frame.basePointer - 1
            elif op == OPBREAK:
                frame = self.popLastFrameOfType(FRAME_TYPE_LOOP)
                if frame is not None:
                    self.sp = frame.basePointer - 1
                    self.incrCurrentFrameIp(3) #to go past the jump to start of loop
            if incrFrameIp:
                self.incrCurrentFrameIp(1)

    def executeCall(self, numArgs):
        callee = self.stack[self.sp-1-numArgs]
        if callee.objectType == OBJECT_TYPES.OBJECT_TYPE_COMPILED_FUNCTION:
            self.callFunction(callee, numArgs)
        elif callee.objectType == OBJECT_TYPES.OBJECT_TYPE_BUILTIN_FUNCTION:
            self.callBuiltin(callee, numArgs)
        else:
            raise BoaVMError("Calling non-function/builtin")

    def callFunction(self, fn, numArgs):
        if numArgs != fn.numParameters:
            raise BoaVMError("Wrong number of arguments: got %d, wanted %d" % (numArgs, fn.numParameters))
        frame = Frame(FRAME_TYPE_FUNCTION, fn, self.sp-numArgs)
        self.pushFrame(frame)
        self.sp = frame.basePointer + fn.numLocals

    def callBuiltin(self, fn, numArgs):
        args = self.stack[self.sp-numArgs:self.sp]
        result = fn.func(args)
        self.sp = self.sp - 1 - numArgs
        self.push(result)
        self.incrCurrentFrameIp(1) #increment needs to happen here because the ip is not updated in the outer while loop

    def callBlock(self):
        fn = self.stack[self.sp-1]
        frame = Frame(FRAME_TYPE_BLOCK, fn, self.sp)
        self.pushFrame(frame)
        self.sp = frame.basePointer + fn.numLocals

    def callLoop(self, numArgs):
        fn = self.stack[self.sp-1-numArgs]
        if numArgs != fn.numParameters:
            raise BoaVMError("Wrong number of arguments: got %d, wanted %d" % (numArgs, fn.numParameters))
        frame = Frame(FRAME_TYPE_LOOP, fn, self.sp-numArgs)
        self.pushFrame(frame)
        self.sp = frame.basePointer + fn.numLocals

    def buildArray(self, startIndex, endIndex):
        elements = self.stack[startIndex:endIndex]
        return newArray(elements)

    def buildHash(self, startIndex, endIndex):
        pairs = []
        for i in range(startIndex, endIndex, 2):
            key = self.stack[i]
            val = self.stack[i+1]
            pairs.append((key, val))
        return newHash(pairs)

    def executeIndexOperation(self, left, index):
        if left.objectType == OBJECT_TYPES.OBJECT_TYPE_ARRAY and \
                index.objectType == OBJECT_TYPES.OBJECT_TYPE_INT:
            return self.executeArrayIndexOperation(left, index)
        elif left.objectType == OBJECT_TYPES.OBJECT_TYPE_HASH:
            return self.executeHashIndexOperation(left, index)
        else:
            raise BoaVMError("Unsupported for index operation: %s,%s" % (left.objectType, index.objectType))

    def executeArrayIndexOperation(self, left, index):
        try:
            self.push(left[index])
        except:
            raise BoaVMError("Array index error: %d" % index.inspect())

    def executeHashIndexOperation(self, left, index):
        try:
            self.push(left[index])
        except:
            raise BoaVMError("Hash index error: %d" % index.inspect())


    def executeComparison(self, op):
        right = self.pop()
        left = self.pop()

        if left.objectType == OBJECT_TYPES.OBJECT_TYPE_INT and \
                right.objectType == OBJECT_TYPES.OBJECT_TYPE_INT:
            return self.executeIntegerComparison(op, left, right)
        if op == OPEQ:
            return self.push(self.nativeBooleanToBooleanObject(right.value == left.value))
        elif op == OPNEQ:
            return self.push(self.nativeBooleanToBooleanObject(right.value != left.value))
        else:
            raise BoaVMError("Unsupported for boolean comparison: %d" % (op))

    def executeIntegerComparison(self, op, left, right):
        leftValue = left.value
        rightValue = right.value

        if op == OPEQ:
            return self.push(self.nativeBooleanToBooleanObject(leftValue == rightValue))
        elif op == OPNEQ:
            return self.push(self.nativeBooleanToBooleanObject(leftValue != rightValue))
        elif op == OPGT:
            return self.push(self.nativeBooleanToBooleanObject(leftValue > rightValue))
        elif op == OPGTEQ:
            return self.push(self.nativeBooleanToBooleanObject(leftValue >= rightValue))
        else:
            raise BoaVMError("Unsupported for integer comparison: %d" % (op))

    def nativeBooleanToBooleanObject(self, bool):
        if bool:
            return TRUE
        else:
            return FALSE

    def executeNotOperator(self):
        operand = self.pop()
        if operand == TRUE:
            return self.push(FALSE)
        elif operand == FALSE:
            return self.push(TRUE)
        elif operand == NULL:
            return self.push(TRUE)
        else:
            return self.push(FALSE)

    def executeMinusOperator(self):
        operand = self.pop()
        if operand.objectType != OBJECT_TYPES.OBJECT_TYPE_INT:
            raise BoaVMError("Unsupported type for negation: %s" % operand.objectType)
        return self.push(newInteger(-operand.value))

    def executeBinaryOperation(self, op):
        right = self.pop()
        left = self.pop()

        if left.objectType == OBJECT_TYPES.OBJECT_TYPE_INT and \
                right.objectType == OBJECT_TYPES.OBJECT_TYPE_INT:
            return self.executeBinaryIntegerOperation(op, left, right)
        elif left.objectType == OBJECT_TYPES.OBJECT_TYPE_STRING and \
                right.objectType == OBJECT_TYPES.OBJECT_TYPE_STRING:
            return self.executeBinaryStringOperation(op, left, right)
        raise BoaVMError("Unsupported types for binary operation: %s %s" % (left.objectType, right.objectType))

    def executeBinaryIntegerOperation(self, op, left, right):
        leftValue = left.value
        rightValue = right.value
        if op == OPADD:
            result = leftValue + rightValue
        elif op == OPSUB:
            result = leftValue - rightValue
        elif op == OPMUL:
            result = leftValue * rightValue
        elif op == OPDIV:
            result = leftValue / rightValue
        else:
            raise BoaVMError("Unknown integer operator: %d" % op)
        self.push(newInteger(result))

    def executeBinaryStringOperation(self, op, left, right):
        leftValue = left.value
        rightValue = right.value
        if op == OPADD:
            result = leftValue + rightValue
        else:
            raise BoaVMError("Unknown integer operator: %d" % op)
        self.push(newString(result))
