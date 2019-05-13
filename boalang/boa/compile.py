from .util import DictLikeStruct

from .ast import (
    NODE_TYPE_PROGRAM,
    NODE_TYPE_STATEMENT,
    NODE_TYPE_EXPRESSION,
    STATEMENT_TYPE_EXPRESSION,
    EXPRESSION_TYPE_INT_LIT,
    EXPRESSION_TYPE_INFIX,
)
from .object import (
    newInteger,
)
from .code import (
    makeInstr,
    OPCONSTANT,
)

class Bytecode(object):
    def __init__(self, instructions, constants):
        self.instructions = instructions #bytecode instructions
        self.constants = constants #BoaObjects

class Compiler(object):
    def __init__(self):
        self.instructions = [] #bytecode instructions
        self.constants = [] #BoaObjects

    def compile(self, node):
        nodeType = node.nodeType
        if nodeType == NODE_TYPE_PROGRAM:
            for s in node.statements:
                self.compile(s)
        elif nodeType == NODE_TYPE_STATEMENT:
            stmtType = node.statementType
            if stmtType == STATEMENT_TYPE_EXPRESSION:
                self.compile(node.expression)
        elif nodeType == NODE_TYPE_EXPRESSION:
            exprType = node.expressionType
            if exprType == EXPRESSION_TYPE_INT_LIT:
                intObj = newInteger(node.value)
                self.emit(OPCONSTANT, self.addConstant(intObj))
            elif exprType == EXPRESSION_TYPE_INFIX:
                self.compile(node.left)
                self.compile(node.right)

    def addConstant(self, c):
        self.constants.append(c)
        return len(self.constants) - 1

    def emit(self, opcode, *operands):
        instr = makeInstr(opcode, *operands)
        pos = self.addInstruction(instr)
        return pos

    def addInstruction(self, instr):
        posNewInstruction = len(self.instructions)
        self.instructions.append(instr)
        return posNewInstruction

    def bytecode(self):
        return Bytecode(list(self.instructions), list(self.constants))
