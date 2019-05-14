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
    readUint16,
)
from .object import (
    newInteger,
    newString,
    newArray,
    newHash,
    OBJECT_TYPES,
    TRUE,
    FALSE,
    NULL,
)
from .evaluator import (
    isTruthy,
)

STACK_SIZE = 2048
GLOBALS_SIZE = 65536

class BoaVMError(Exception): pass

class VM(object):
    def __init__(self, bytecode):
        self.constants = bytecode.constants
        self.instr = bytecode.instr
        self.stack = [None]*STACK_SIZE #stack of BoaObjects
        self.globals = [None]*GLOBALS_SIZE
        self.sp = 0

    @staticmethod
    def newWithGlobalsStore(bytecode, globals):
        vm = VM(bytecode)
        vm.globals = globals
        return vm

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
        ip = 0
        while ip < len(self.instr):
            op = self.instr[ip:ip+1]
            if op == OPCONSTANT:
                constIndex = readUint16(self.instr[ip+1:])
                ip += 2
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
                numElements = readUint16(self.instr[ip+1:])
                ip += 2
                arr = self.buildArray(self.sp-numElements, self.sp)
                self.sp = self.sp - numElements
                self.push(arr)
            elif op == OPHASH:
                numElements = readUint16(self.instr[ip+1:])
                ip += 2
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
                globalIndex = readUint16(self.instr[ip+1:])
                ip += 2
                self.globals[globalIndex] = self.pop()
            elif op == OPGETGLOBAL:
                globalIndex = readUint16(self.instr[ip+1:])
                ip += 2
                self.push(self.globals[globalIndex])
            elif op == OPJUMP:
                pos = readUint16(self.instr[ip+1:])
                ip = pos - 1
            elif op == OPJUMPNOTTRUE:
                pos = readUint16(self.instr[ip+1:])
                ip += 2
                condition = self.pop()
                if not isTruthy(condition):
                    ip = pos - 1

            ip += 1

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
