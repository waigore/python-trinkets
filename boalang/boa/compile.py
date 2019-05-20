from .util import DictLikeStruct

from .ast import (
    NODE_TYPE_PROGRAM,
    NODE_TYPE_STATEMENT,
    NODE_TYPE_EXPRESSION,
    STATEMENT_TYPE_EXPRESSION,
    STATEMENT_TYPE_LET,
    STATEMENT_TYPE_ASSIGN,
    STATEMENT_TYPE_RETURN,
    STATEMENT_TYPE_BLOCK,
    STATEMENT_TYPE_WHILE,
    STATEMENT_TYPE_FOR,
    STATEMENT_TYPE_BREAK,
    STATEMENT_TYPE_CONTINUE,
    EXPRESSION_TYPE_INT_LIT,
    EXPRESSION_TYPE_NULL_LIT,
    EXPRESSION_TYPE_STR_LIT,
    EXPRESSION_TYPE_ARRAY_LIT,
    EXPRESSION_TYPE_HASH_LIT,
    EXPRESSION_TYPE_BOOLEAN,
    EXPRESSION_TYPE_IDENT,
    EXPRESSION_TYPE_INFIX,
    EXPRESSION_TYPE_PREFIX,
    EXPRESSION_TYPE_INDEX,
    EXPRESSION_TYPE_GET,
    EXPRESSION_TYPE_FUNC_LIT,
    EXPRESSION_TYPE_IF,
    EXPRESSION_TYPE_CALL,
)
from .token import (
    TOKEN_TYPES,
)
from .object import (
    newInteger,
    newString,
    newCompiledFunction,
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
    OPCONTINUE,
    OPBREAK,
    OPITER,
    OPITERNEXT,
    OPITERHASNEXT,
    OPGETBUILTIN,
    OPCLOSURE,
    OPGETFREE,
    OPCURRENTCLOSURE,
    OPGETBLOCK,
    OPSETBLOCK,
    OPGETATTR,
    OPSETATTR,
)
from .symbol import (
    SymbolTable,
    SymbolNotFoundError,
    GLOBAL_SCOPE,
    LOCAL_SCOPE,
    BUILTIN_SCOPE,
    FREE_SCOPE,
    FUNCTION_SCOPE,
    BLOCK_SCOPE,
)
from .builtins import (
    BUILTIN_FUNCTION_LIST,
    BUILTIN_FUNCTIONS,
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

class CompilationScope(object):
    def __init__(self, instructions, lastInstruction, previousInstruction):
        self.instructions = instructions #bytecode instructions
        self.lastInstruction = lastInstruction #EmittedInstruction
        self.previousInstruction = previousInstruction #EmittedInstruction

class Compiler(object):
    def __init__(self):
        self.constants = [] #BoaObjects
        self.symbolTable = SymbolTable()
        self.scopes = [CompilationScope([], None, None)] #CompilationScopes
        self.scopeIndex = 0

        for index, fname in enumerate(BUILTIN_FUNCTION_LIST):
            self.symbolTable.defineBuiltin(index, fname)

    @staticmethod
    def withNewState(symbolTable, constants):
        compiler = Compiler()
        compiler.symbolTable = symbolTable
        compiler.constants = constants
        return compiler

    def loadSymbol(self, s):
        if s.scope == GLOBAL_SCOPE:
            self.emit(OPGETGLOBAL, s.index)
        elif s.scope == LOCAL_SCOPE:
            self.emit(OPGETLOCAL, s.index)
        elif s.scope == FREE_SCOPE:
            self.emit(OPGETFREE, s.index)
        elif s.scope == FUNCTION_SCOPE:
            self.emit(OPCURRENTCLOSURE)
        elif s.scope == BLOCK_SCOPE:
            self.emit(OPGETBLOCK, s.scopeDiff, s.index)
        else:
            self.emit(OPGETBUILTIN, s.index)

    def assignSymbol(self, s):
        if s.scope == GLOBAL_SCOPE:
            self.emit(OPSETGLOBAL, s.index)
        elif s.scope == LOCAL_SCOPE:
            self.emit(OPSETLOCAL, s.index)
        elif s.scope == BLOCK_SCOPE:
            self.emit(OPSETBLOCK, s.scopeDiff, s.index)
        else:
            raise BoaCompilerError("Cannot assign symbol at current scope: %s" % s.name)

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
                symbol = self.symbolTable.define(node.identifier.value)
                self.compile(node.value)
                self.assignSymbol(symbol)
                #if symbol.scope == GLOBAL_SCOPE:
                #    self.emit(OPSETGLOBAL, symbol.index)
                #else:
                #    self.emit(OPSETLOCAL, symbol.index)
            elif stmtType == STATEMENT_TYPE_ASSIGN:
                if node.identifier.expressionType == EXPRESSION_TYPE_INDEX:
                    self.compile(node.identifier.left)
                    self.compile(node.identifier.index)
                    self.compile(node.value)
                    self.emit(OPSETINDEX)
                elif node.identifier.expressionType == EXPRESSION_TYPE_GET:
                    self.compile(node.identifier.object)
                    self.compileSetProperty(node.identfier.property, node.value)
                else:
                    self.compile(node.value)
                    try:
                        symbol = self.symbolTable.resolve(node.identifier.value)
                    except SymbolNotFoundError as e:
                        raise BoaCompilerError("Identifier not defined: %s" % node.value)
                    self.assignSymbol(symbol)
                    #if symbol.scope == GLOBAL_SCOPE:
                    #    self.emit(OPSETGLOBAL, symbol.index)
                    #else:
                    #    self.emit(OPSETLOCAL, symbol.index)
            elif stmtType == STATEMENT_TYPE_FOR:
                self.compile(node.iterable)
                self.emit(OPITER)
                tmpIteratorSymbol = self.symbolTable.define("__temp__%02d" % self.symbolTable.numDefinitions)
                self.assignSymbol(tmpIteratorSymbol)
                #if tmpIteratorSymbol.scope == GLOBAL_SCOPE:
                #    self.emit(OPSETGLOBAL, tmpIteratorSymbol.index)
                #else:
                #    self.emit(OPSETLOCAL, tmpIteratorSymbol.index)

                startPos = self.getInstrBytecodePos(len(self.currentInstructions()))

                self.loadSymbol(tmpIteratorSymbol)
                #if tmpIteratorSymbol.scope == GLOBAL_SCOPE:
                #    self.emit(OPGETGLOBAL, tmpIteratorSymbol.index)
                #else:
                #    self.emit(OPGETLOCAL, tmpIteratorSymbol.index)
                self.emit(OPITERHASNEXT)
                jumpNotTruePos = self.emit(OPJUMPNOTTRUE, 9999)

                self.enterScope()
                self.symbolTable.define(node.iterator.value)
                self.compile(node.blockStatement)
                self.emit(OPCONTINUE)

                freeSymbols = self.symbolTable.freeSymbols
                numLocals = self.symbolTable.numDefinitions
                instructions = self.leaveScope()
                for freeSymbol in freeSymbols:
                    self.loadSymbol(freeSymbol)

                compiledInstructions = b''.join(instructions)
                compiledFn = newCompiledFunction(compiledInstructions, numLocals, 1)
                self.emit(OPCLOSURE, self.addConstant(compiledFn), len(freeSymbols))

                self.loadSymbol(tmpIteratorSymbol)
                #if tmpIteratorSymbol.scope == GLOBAL_SCOPE:
                #    self.emit(OPGETGLOBAL, tmpIteratorSymbol.index)
                #else:
                #    self.emit(OPGETLOCAL, tmpIteratorSymbol.index)
                self.emit(OPITERNEXT)

                self.emit(OPLOOPCALL, 1)
                self.emit(OPJUMP, startPos)

                afterLoopCallPos = self.getInstrBytecodePos(len(self.currentInstructions()))
                self.changeOperand(jumpNotTruePos, afterLoopCallPos)
            elif stmtType == STATEMENT_TYPE_WHILE:
                startPos = self.getInstrBytecodePos(len(self.currentInstructions()))
                condition = node.condition
                self.compile(condition)
                jumpNotTruePos = self.emit(OPJUMPNOTTRUE, 9999)

                self.enterScope()
                self.compile(node.blockStatement)
                self.emit(OPCONTINUE)

                freeSymbols = self.symbolTable.freeSymbols
                numLocals = self.symbolTable.numDefinitions
                instructions = self.leaveScope()
                for freeSymbol in freeSymbols:
                    self.loadSymbol(freeSymbol)

                compiledInstructions = b''.join(instructions)
                compiledFn = newCompiledFunction(compiledInstructions, numLocals, 0)
                self.emit(OPCLOSURE, self.addConstant(compiledFn), len(freeSymbols))
                self.emit(OPLOOPCALL, 0)
                self.emit(OPJUMP, startPos)

                afterLoopCallPos = self.getInstrBytecodePos(len(self.currentInstructions()))
                self.changeOperand(jumpNotTruePos, afterLoopCallPos)
            elif stmtType == STATEMENT_TYPE_CONTINUE:
                self.emit(OPCONTINUE)
            elif stmtType == STATEMENT_TYPE_BREAK:
                self.emit(OPBREAK)
            elif stmtType == STATEMENT_TYPE_RETURN:
                self.compile(node.value)
                self.emit(OPRETURNVALUE)
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
            elif exprType == EXPRESSION_TYPE_ARRAY_LIT:
                for el in node.elements:
                    self.compile(el)
                self.emit(OPARRAY, len(node.elements))
            elif exprType == EXPRESSION_TYPE_HASH_LIT:
                keys = []
                vals = []
                keyVals = {}
                for el in node.elements:
                    key, val = el
                    keys.append(key)
                    vals.append(val)
                    keyVals[str(key)] = val
                keys.sort(key=lambda e: str(e))

                for key in keys:
                    self.compile(key)
                    self.compile(keyVals[str(key)])
                self.emit(OPHASH, len(node.elements)*2)
            elif exprType == EXPRESSION_TYPE_NULL_LIT:
                self.emit(OPNULL)
            elif exprType == EXPRESSION_TYPE_FUNC_LIT:
                self.enterScope(isFunction=True)
                if node.name is not None:
                    self.symbolTable.defineFunctionName(node.name)
                for param in node.parameters:
                    self.symbolTable.define(param.value)

                self.compile(node.body)

                if self.lastInstructionIs(OPPOP):
                    lastPos = self.currentScope().lastInstruction.position
                    self.replaceInstruction(lastPos, makeInstr(OPRETURNVALUE))
                    self.currentScope().lastInstruction.opcode = OPRETURNVALUE

                if not self.lastInstructionIs(OPRETURNVALUE):
                    self.emit(OPNULL)
                    self.emit(OPRETURNVALUE)

                freeSymbols = self.symbolTable.freeSymbols
                numLocals = self.symbolTable.numDefinitions
                instructions = self.leaveScope()
                for freeSymbol in freeSymbols:
                    self.loadSymbol(freeSymbol)
                compiledInstructions = b''.join(instructions)
                compiledFn = newCompiledFunction(compiledInstructions, numLocals, len(node.parameters))
                self.emit(OPCLOSURE, self.addConstant(compiledFn), len(freeSymbols))
            elif exprType == EXPRESSION_TYPE_CALL:
                self.compile(node.function)
                for arg in node.arguments:
                    self.compile(arg)
                self.emit(OPCALL, len(node.arguments))
            elif exprType == EXPRESSION_TYPE_IDENT:
                try:
                    symbol = self.symbolTable.resolve(node.value)
                except SymbolNotFoundError as e:
                    raise BoaCompilerError("Identifier not defined: %s" % node.value)
                self.loadSymbol(symbol)
                #if symbol.scope == GLOBAL_SCOPE:
                #    self.emit(OPGETGLOBAL, symbol.index)
                #else:
                #    self.emit(OPGETLOCAL, symbol.index)
            elif exprType == EXPRESSION_TYPE_INDEX:
                self.compile(node.left)
                self.compile(node.index)
                self.emit(OPINDEX)
            elif exprType == EXPRESSION_TYPE_GET:
                self.compile(node.object)
                self.compileGetProperty(node.property)
            elif exprType == EXPRESSION_TYPE_IF:
                jumpPositions = []
                for i, conditionalBlock in enumerate(node.conditionalBlocks):
                    condition, consequence = conditionalBlock
                    self.compile(condition)
                    jumpNotTruePos = self.emit(OPJUMPNOTTRUE, 9999)

                    self.enterScope()
                    #posPreCompilation = len(self.currentInstructions())-1
                    self.compile(consequence)
                    if self.lastInstructionIs(OPPOP):
                        #lastPos = self.currentScope().lastInstruction.position
                        #self.replaceInstruction(lastPos, makeInstr(OPBLOCKRETURN))
                        #self.currentScope().lastInstruction.opcode = OPBLOCKRETURN
                        self.removeLast()
                        self.emit(OPBLOCKRETURN)

                    if not self.lastInstructionIs(OPBLOCKRETURN):
                        self.emit(OPNULL)
                        self.emit(OPBLOCKRETURN)

                    freeSymbols = self.symbolTable.freeSymbols
                    numLocals = self.symbolTable.numDefinitions
                    instructions = self.leaveScope()
                    for freeSymbol in freeSymbols:
                        self.loadSymbol(freeSymbol)

                    compiledInstructions = b''.join(instructions)
                    compiledFn = newCompiledFunction(compiledInstructions, numLocals, 0)
                    self.emit(OPCLOSURE, self.addConstant(compiledFn), len(freeSymbols))
                    self.emit(OPBLOCKCALL)

                    jumpPos = self.emit(OPJUMP, 9999)
                    jumpPositions.append(jumpPos)
                    afterConsequencePos = self.getInstrBytecodePos(len(self.currentInstructions()))
                    self.changeOperand(jumpNotTruePos, afterConsequencePos)

                if not node.alternative:
                    self.emit(OPNULL)
                else:
                    #posPreCompilation = len(self.currentInstructions())-1
                    #self.compile(node.alternative)
                    #if self.lastInstructionIs(OPPOP):
                    #    self.removeLast()
                    #if len(self.currentInstructions())-1 == posPreCompilation:
                    #    self.emit(OPNULL)
                    self.enterScope()
                    self.compile(node.alternative)
                    if self.lastInstructionIs(OPPOP):
                        self.removeLast()
                        self.emit(OPBLOCKRETURN)

                    if not self.lastInstructionIs(OPBLOCKRETURN):
                        self.emit(OPNULL)
                        self.emit(OPBLOCKRETURN)

                    freeSymbols = self.symbolTable.freeSymbols
                    numLocals = self.symbolTable.numDefinitions
                    instructions = self.leaveScope()
                    for freeSymbol in freeSymbols:
                        self.loadSymbol(freeSymbol)

                    compiledInstructions = b''.join(instructions)
                    compiledFn = newCompiledFunction(compiledInstructions, numLocals, 0)
                    self.emit(OPCLOSURE, self.addConstant(compiledFn), len(freeSymbols))
                    self.emit(OPBLOCKCALL)

                afterAlternativePos = self.getInstrBytecodePos(len(self.currentInstructions()))
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

    def compileSetProperty(self, property, val):
        if property.expressionType == EXPRESSION_TYPE_IDENT:
            self.compileSetIdentProperty(property, val)
        elif property.expressionType == EXPRESSION_TYPE_INDEX:
            self.compileSetIndexProperty(property, val)
        elif property.expressionType == EXPRESSION_TYPE_GET:
            self.compileGetProperty(property.object)
            self.compileSetProperty(property.property, val)
        else:
            raise BoaCompilerError("Property not settable: %s" % (property))

    def compileSetIdentProperty(self, property, val):
        attributeName = newString(property.value)
        self.emit(OPCONSTANT, self.addConstant(attributeName))
        self.compile(val)
        self.emit(OPSETATTR)

    def compileSetIndexProperty(self, property, val):
        if property.left.expressionType == EXPRESSION_TYPE_IDENT:
            self.compileGetIdentProperty(property.left)
        elif property.left.expressionType == EXPRESSION_TYPE_INDEX:
            self.compileGetIndexProperty(property.left)
        else:
            raise BoaCompilerError("Property not settable: %s" % (property))
        self.compile(property.index)
        self.compile(val)
        self.emit(OPSETINDEX)

    def compileGetProperty(self, property):
        if property.expressionType == EXPRESSION_TYPE_IDENT:
            self.compileGetIdentProperty(property)
            return
        elif property.expressionType == EXPRESSION_TYPE_INDEX:
            self.compileGetIndexProperty(property)
            return
        elif property.expressionType == EXPRESSION_TYPE_GET:
            self.compileGetProperty(property.object)
            self.compileGetProperty(property.property)
            return
        else:
            raise BoaCompilerError("Property not gettable: %s.%s" % (object, property))

    def compileGetIdentProperty(self, property):
        attributeName = newString(property.value)
        self.emit(OPCONSTANT, self.addConstant(attributeName))
        self.emit(OPGETATTR)

    def compileGetIndexProperty(self, property):
        if property.left.expressionType == EXPRESSION_TYPE_IDENT:
            self.compileGetIdentProperty(property.left)
        elif property.left.expressionType == EXPRESSION_TYPE_INDEX:
            self.compileGetIndexProperty(property.left)
        elif property.left.expressionType == EXPRESSION_TYPE_GET:
            self.compileGetProperty(property.left)
        else:
            raise BoaCompilerError("Property not gettable: %s" % (property))
        self.compile(property.index)
        self.emit(OPINDEX)

    def enterScope(self, isFunction=False):
        newScope = CompilationScope([], None, None)
        currST = self.symbolTable
        self.symbolTable = SymbolTable(outer=currST, isFunction=isFunction)
        self.scopes.append(newScope)
        self.scopeIndex += 1

    def leaveScope(self):
        instructions = self.currentInstructions()
        currScope = self.scopes.pop()
        self.symbolTable = self.symbolTable.outer
        self.scopeIndex -= 1
        return instructions

    def addConstant(self, c):
        self.constants.append(c)
        return len(self.constants) - 1

    def emit(self, opcode, *operands):
        instr = makeInstr(opcode, *operands)
        pos = self.addInstruction(instr)
        self.setLastInstruction(opcode, pos)
        return pos

    def currentInstructions(self):
        return self.scopes[self.scopeIndex].instructions

    def currentScope(self):
        return self.scopes[self.scopeIndex]

    def getInstrBytecodePos(self, pos):
        instructionsUpTo = self.currentInstructions()[:pos]
        instrBytes = b''.join(instructionsUpTo)
        return len(instrBytes)

    def setLastInstruction(self, opcode, pos):
        prev = self.currentScope().lastInstruction
        last = EmittedInstruction(opcode, pos)
        self.currentScope().previousInstruction = prev
        self.currentScope().lastInstruction = last

    def replaceInstruction(self, pos, newInstruction):
        self.currentInstructions()[pos] = newInstruction

    def changeOperand(self, opPos, operand):
        opcode = self.currentInstructions()[opPos][0:1]
        newInstr = makeInstr(opcode, operand)
        self.replaceInstruction(opPos, newInstr)

    def lastInstructionIs(self, opcode):
        if len(self.currentInstructions()) == 0:
            return False
        return self.currentScope().lastInstruction.opcode == opcode

    def removeLast(self):
        last = self.currentScope().lastInstruction
        prev = self.currentScope().previousInstruction
        old = self.currentInstructions()
        new = old[:last.position]

        self.currentScope().instructions = new
        self.currentScope().lastInstruction = prev

    def addInstruction(self, instr):
        posNewInstruction = len(self.currentInstructions())
        self.currentInstructions().append(instr)
        return posNewInstruction

    def bytecode(self):
        return Bytecode(list(self.currentInstructions()), list(self.constants))
