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
    readUint16,
)
from .object import (
    newInteger,
    OBJECT_TYPES,
    TRUE,
    FALSE,
)

STACK_SIZE = 2048

class BoaVMError(Exception): pass

class VM(object):
    def __init__(self, bytecode):
        self.constants = bytecode.constants
        self.instr = bytecode.instr
        self.stack = [None]*STACK_SIZE #stack of BoaObjects
        self.sp = 0

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
            elif op == OPPOP:
                self.pop()
            ip += 1

    def executeComparison(self, op):
        right = self.pop()
        left = self.pop()

        if left.objectType == OBJECT_TYPES.OBJECT_TYPE_INT and \
                right.objectType == OBJECT_TYPES.OBJECT_TYPE_INT:
            return self.executeIntegerComparison(op, left, right)
        if op == OPEQ:
            return self.push(self.nativeBooleanToBooleanObject(right == left))
        elif op == OPNEQ:
            return self.push(self.nativeBooleanToBooleanObject(right != left))
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
            return self.push(self.nativeBooleanToBooleanObject(leftValue > rightValue))
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
