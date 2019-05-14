from .util import DictLikeStruct

from .ast import (
    NODE_TYPE_PROGRAM,
    NODE_TYPE_STATEMENT,
    NODE_TYPE_EXPRESSION,
    STATEMENT_TYPE_EXPRESSION,
    STATEMENT_TYPE_LET,
    EXPRESSION_TYPE_INT_LIT,
    EXPRESSION_TYPE_NULL_LIT,
    EXPRESSION_TYPE_STR_LIT,
    EXPRESSION_TYPE_BOOLEAN,
    EXPRESSION_TYPE_IDENT,
    EXPRESSION_TYPE_INFIX,
    EXPRESSION_TYPE_PREFIX,
    EXPRESSION_TYPE_IF,
    STATEMENT_TYPE_BLOCK,
)
from .token import (
    TOKEN_TYPES,
)
from .object import (
    newInteger,
    newString,
)
from .code import (
    makeInstr,
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
)
from .symbol import (
    SymbolTable,
    SymbolNotFoundError,
)

class BoaCompilerError(Exception): pass

class Bytecode(object):
    def __init__(self, instructions, constants):
        self.instructions = instructions #bytecode instructions
        self.constants = constants #BoaObjects

    @property
    def instr(self):
        return b''.join(self.instructions)

class EmittedInstruction(object):
    def __init__(self, opcode, position):
        self.opcode = opcode
        self.position = position

class Compiler(object):
    def __init__(self):
        self.instructions = [] #bytecode instructions
        self.constants = [] #BoaObjects
        self.lastInstruction = None
        self.previousInstruction = None
        self.symbolTable = SymbolTable()

    @staticmethod
    def withNewState(symbolTable, constants):
        compiler = Compiler()
        compiler.symbolTable = symbolTable
        compiler.constants = constants
        return compiler

    def compile(self, node):
        nodeType = node.nodeType
        if nodeType == NODE_TYPE_PROGRAM:
            for s in node.statements:
                self.compile(s)
        elif nodeType == NODE_TYPE_STATEMENT:
            stmtType = node.statementType
            if stmtType == STATEMENT_TYPE_EXPRESSION:
                self.compile(node.expression)
                self.emit(OPPOP)
            elif stmtType == STATEMENT_TYPE_BLOCK:
                for statement in node.statements:
                    self.compile(statement)
            elif stmtType == STATEMENT_TYPE_LET:
                self.compile(node.value)
                symbol = self.symbolTable.define(node.identifier.value)
                self.emit(OPSETGLOBAL, symbol.index)
        elif nodeType == NODE_TYPE_EXPRESSION:
            exprType = node.expressionType
            if exprType == EXPRESSION_TYPE_INT_LIT:
                intObj = newInteger(node.value)
                self.emit(OPCONSTANT, self.addConstant(intObj))
            elif exprType == EXPRESSION_TYPE_STR_LIT:
                strObj = newString(node.value)
                self.emit(OPCONSTANT, self.addConstant(strObj))
            elif exprType == EXPRESSION_TYPE_BOOLEAN:
                if node.value:
                    self.emit(OPTRUE)
                else:
                    self.emit(OPFALSE)
            elif exprType == EXPRESSION_TYPE_NULL_LIT:
                self.emit(OPNULL)
            elif exprType == EXPRESSION_TYPE_IDENT:
                try:
                    symbol = self.symbolTable.resolve(node.value)
                except SymbolNotFoundError as e:
                    raise BoaCompilerError("Identifier not defined: %s" % node.value)
                self.emit(OPGETGLOBAL, symbol.index)
            elif exprType == EXPRESSION_TYPE_IF:
                jumpPositions = []
                for i, conditionalBlock in enumerate(node.conditionalBlocks):
                    condition, consequence = conditionalBlock
                    self.compile(condition)
                    jumpNotTruePos = self.emit(OPJUMPNOTTRUE, 9999)

                    posPreCompilation = len(self.instructions)-1
                    self.compile(consequence)
                    if self.lastInstructionIs(OPPOP):
                        self.removeLast()
                    if len(self.instructions)-1 == posPreCompilation:
                        self.emit(OPNULL)

                    jumpPos = self.emit(OPJUMP, 9999)
                    jumpPositions.append(jumpPos)
                    afterConsequencePos = self.getInstrBytecodePos(len(self.instructions))
                    self.changeOperand(jumpNotTruePos, afterConsequencePos)

                if not node.alternative:
                    self.emit(OPNULL)
                else:
                    posPreCompilation = len(self.instructions)-1
                    self.compile(node.alternative)
                    if self.lastInstructionIs(OPPOP):
                        self.removeLast()
                    if len(self.instructions)-1 == posPreCompilation:
                        self.emit(OPNULL)

                afterAlternativePos = self.getInstrBytecodePos(len(self.instructions))
                for jumpPos in jumpPositions:
                    self.changeOperand(jumpPos, afterAlternativePos)
            elif exprType == EXPRESSION_TYPE_PREFIX:
                self.compile(node.right)
                if node.operator == TOKEN_TYPES.TOKEN_TYPE_MINUS.value:
                    self.emit(OPMINUS)
                elif node.operator in [TOKEN_TYPES.TOKEN_TYPE_NOT.value, TOKEN_TYPES.TOKEN_TYPE_EXCLAMATION.value]:
                    self.emit(OPNOT)
                else:
                    raise BoaCompilerError("Unknown prefix operator: %s" % node.operator)
            elif exprType == EXPRESSION_TYPE_INFIX:
                if node.operator == TOKEN_TYPES.TOKEN_TYPE_LT.value:
                    self.compile(node.right)
                    self.compile(node.left)
                    self.emit(OPGT)
                    return
                elif node.operator == TOKEN_TYPES.TOKEN_TYPE_LTEQ.value:
                    self.compile(node.right)
                    self.compile(node.left)
                    self.emit(OPGTEQ)
                    return
                self.compile(node.left)
                self.compile(node.right)
                if node.operator == TOKEN_TYPES.TOKEN_TYPE_PLUS.value:
                    self.emit(OPADD)
                elif node.operator == TOKEN_TYPES.TOKEN_TYPE_MINUS.value:
                    self.emit(OPSUB)
                elif node.operator == TOKEN_TYPES.TOKEN_TYPE_ASTERISK.value:
                    self.emit(OPMUL)
                elif node.operator == TOKEN_TYPES.TOKEN_TYPE_SLASH.value:
                    self.emit(OPDIV)
                elif node.operator == TOKEN_TYPES.TOKEN_TYPE_EQ.value:
                    self.emit(OPEQ)
                elif node.operator == TOKEN_TYPES.TOKEN_TYPE_NEQ.value:
                    self.emit(OPNEQ)
                elif node.operator == TOKEN_TYPES.TOKEN_TYPE_GT.value:
                    self.emit(OPGT)
                elif node.operator == TOKEN_TYPES.TOKEN_TYPE_GTEQ.value:
                    self.emit(OPGTEQ)
                else:
                    raise BoaCompilerError("Unknown infix operator: %s" % node.operator)

    def addConstant(self, c):
        self.constants.append(c)
        return len(self.constants) - 1

    def emit(self, opcode, *operands):
        instr = makeInstr(opcode, *operands)
        pos = self.addInstruction(instr)
        self.setLastInstruction(opcode, pos)
        return pos

    def getInstrBytecodePos(self, pos):
        instructionsUpTo = self.instructions[:pos]
        instrBytes = b''.join(instructionsUpTo)
        return len(instrBytes)

    def setLastInstruction(self, opcode, pos):
        prev = self.lastInstruction
        last = EmittedInstruction(opcode, pos)
        self.previousInstruction = prev
        self.lastInstruction = last

    def replaceInstruction(self, pos, newInstruction):
        self.instructions[pos] = newInstruction

    def changeOperand(self, opPos, operand):
        opcode = self.instructions[opPos][0:1]
        newInstr = makeInstr(opcode, operand)
        self.replaceInstruction(opPos, newInstr)

    def lastInstructionIs(self, opcode):
        return self.lastInstruction.opcode == opcode

    def removeLast(self):
        self.instructions = self.instructions[:self.lastInstruction.position]
        self.lastInstruction = self.previousInstruction

    def addInstruction(self, instr):
        posNewInstruction = len(self.instructions)
        self.instructions.append(instr)
        return posNewInstruction

    def bytecode(self):
        return Bytecode(list(self.instructions), list(self.constants))
