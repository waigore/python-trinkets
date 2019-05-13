from .util import DictLikeStruct
from .code import (
    DEFINITIONS,
    OPCONSTANT,
    OPADD,
    readUint16,
)
from .object import (
    newInteger,
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
            elif op == OPADD:
                right = self.pop()
                left = self.pop()
                leftValue = left.value
                rightValue = right.value
                result = leftValue + rightValue
                self.push(newInteger(result))
            ip += 1
