from .util import (
    DictLikeStruct,
    readUint16,
    readUint8,
    readUint,
)

OPCONSTANT = b'\x00'
OPADD = b'\x01'
OPPOP = b'\x02'
OPSUB = b'\x03'
OPMUL = b'\x04'
OPDIV = b'\x05'
OPTRUE = b'\x06'
OPFALSE = b'\x07'
OPEQ = b'\x08'
OPNEQ = b'\x09'
OPGT = b'\x0A'
OPGTEQ = b'\x0B'
OPMINUS = b'\x0C'
OPNOT = b'\x0D'
OPJUMPNOTTRUE = b'\x0E'
OPJUMP = b'\x0F'
OPNULL = b'\x10'
OPGETGLOBAL = b'\x11'
OPSETGLOBAL = b'\x12'
OPARRAY = b'\x13'
OPHASH = b'\x14'
OPINDEX = b'\x15'
OPCALL = b'\x16'
OPRETURNVALUE = b'\x17'
OPRETURN = b'\x18' #reserved
OPGETLOCAL = b'\x19'
OPSETLOCAL = b'\x1A'
OPSETINDEX = b'\x1B'
OPBLOCKCALL = b'\x1C'
OPBLOCKRETURN = b'\x1D'
OPLOOPCALL = b'\x1E'
OPBREAK = b'\x1F'
OPCONTINUE = b'\x20'
OPGETTEMP = b'\x21' #reserved
OPSETTEMP = b'\x22' #reserved
OPGETGLOBALTEMP = b'\x23' #reserved
OPSETGLOBALTEMP = b'\x24' #reserved
OPITER = b'\x25'
OPITERNEXT = b'\x26'
OPITERHASNEXT = b'\x27'
OPGETBUILTIN = b'\x28'
OPCLOSURE = b'\x29'
OPGETFREE = b'\x2A'
OPCURRENTCLOSURE = b'\x2B'
OPGETBLOCK = b'\x2C'
OPSETBLOCK = b'\x2D'
OPGETATTR = b'\x2E'
OPSETATTR = b'\x2F'
OPGETINSTANCE = b'\x30'
OPDEFCLASS = b'\x31'
OPGETCLASS = b'\x32'

class BoaNoSuchOpcodeError(Exception): pass

class BoaOperandError(Exception): pass

class Definition(object):
    def __init__(self, name, operandWidths):
        self.name = name
        self.operandWidths = operandWidths

DEFINITIONS = DictLikeStruct({
    OPCONSTANT: Definition("OpConstant", [2]),
    OPADD: Definition("OpAdd", []),
    OPPOP: Definition("OpPop", []),
    OPSUB: Definition("OpSub", []),
    OPMUL: Definition("OpMul", []),
    OPDIV: Definition("OpDiv", []),
    OPTRUE: Definition("OpTrue", []),
    OPFALSE: Definition("OpFalse", []),
    OPEQ: Definition("OpEq", []),
    OPNEQ: Definition("OpNeq", []),
    OPGT: Definition("OpGt", []),
    OPGTEQ: Definition("OpGtEq", []),
    OPMINUS: Definition("OpMinus", []),
    OPNOT: Definition("OpNot", []),
    OPJUMPNOTTRUE: Definition("OpJumpNotTrue", [2]),
    OPJUMP: Definition("OpJump", [2]),
    OPNULL: Definition("OpNull", []),
    OPGETGLOBAL: Definition("OpGetGlobal", [2]),
    OPSETGLOBAL: Definition("OpSetGlobal", [2]),
    OPARRAY: Definition("OpArray", [2]),
    OPHASH: Definition("OpHash", [2]),
    OPINDEX: Definition("OpIndex", []),
    OPCALL: Definition("OpCall", [1]),
    OPRETURNVALUE: Definition("OpReturnValue", []),
    OPRETURN: Definition("OpReturn", []),
    OPGETLOCAL: Definition("OpGetLocal", [1]),
    OPSETLOCAL: Definition("OpSetLocal", [1]),
    OPSETINDEX: Definition("OpSetIndex", []),
    OPBLOCKCALL: Definition("OpBlockCall", []),
    OPBLOCKRETURN: Definition("OpBlockReturn", []),
    OPLOOPCALL: Definition("OpLoopCall", [1]),
    OPBREAK: Definition("OpBreak", []),
    OPCONTINUE: Definition("OpContinue", []),
    OPITER: Definition("OpIter", []),
    OPITERNEXT: Definition("OpIterNext", []),
    OPITERHASNEXT: Definition("OpIterHasNext", []),
    OPGETBUILTIN: Definition("OpGetBuiltin", [1]),
    OPCLOSURE: Definition("OpClosure", [2, 1]),
    OPGETFREE: Definition("OpGetFree", [1]),
    OPCURRENTCLOSURE: Definition("OpCurrentClosure", []),
    OPGETBLOCK: Definition("OpGetBlock", [2, 2]),
    OPSETBLOCK: Definition("OpSetBlock", [2, 2]),
    OPGETATTR: Definition("OpGetAttr", []),
    OPSETATTR: Definition("OpSetAttr", []),
    OPGETINSTANCE: Definition("OpGetInstance", []),
    OPDEFCLASS: Definition("OpDefClass", [2, 2, 2]),
    OPGETCLASS: Definition("OpGetClass", [2]),
})

def lookupOpcode(b):
    if not b in DEFINITIONS:
        raise BoaNoSuchOpcodeError(b)
    return DEFINITIONS[b]

def makeInstr(opcode, *operands):
    definition = lookupOpcode(opcode)
    if len(operands) != len(definition.operandWidths):
        raise BoaOperandError("Operand number mismatch. Got %d, want %d" % (len(operands), len(definition.operandWidths)))
    instructionLen = 1
    for w in definition.operandWidths:
        instructionLen += w
    offset = 1
    byteArr = bytearray(opcode)
    for i, o in enumerate(operands):
        w = definition.operandWidths[i]
        oBytes = (o).to_bytes(w, byteorder='big')
        byteArr += oBytes
        offset += w
    return bytes(byteArr)

def formatInstrs(instr):
    i = 0
    formatted = []
    while i < len(instr):
        definition = lookupOpcode(bytes(instr[i:i+1]))
        operands, read = readOperands(definition, instr[i+1:])
        formatted.append('%04d %s\n' % (i, formatInstr(definition, operands)))
        i = i + 1 + read
    return ''.join(formatted)

def formatInstr(definition, operands):
    operandCount = len(definition.operandWidths)
    if len(operands) != operandCount:
        raise BoaOperandError("Operand number mismatch. Got %d, want %d" % (len(operands), len(definition.operandWidths)))
    return "%s%s%s" % (definition.name, ' ' if operands else '', ' '.join(['%d' % operand for operand in operands]))

def readOperands(definition, instr):
    operands = []
    offset = 0
    for i, w in enumerate(definition.operandWidths):
        val = readUint(instr[offset:offset+w], w)
        offset += w
        operands.append(val)
    return operands, offset
