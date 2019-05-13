from .util import DictLikeStruct

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
    return "%s%s%s" % (definition.name, ' ' if operands else '', ''.join(['%d' % operand for operand in operands]))

def readUint16(instr):
    return int.from_bytes(instr[0:2], byteorder='big')

def readOperands(definition, instr):
    operands = []
    offset = 0
    for i, w in enumerate(definition.operandWidths):
        val = readUint16(instr[offset:offset+w])
        offset += w
        operands.append(val)
    return operands, offset
