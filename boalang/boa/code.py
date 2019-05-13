from .util import DictLikeStruct

OPCONSTANT = b'\x00'
OPADD = b'\x01'
OPPUSH = b'\x01'

class NoSuchOpcodeError(Exception): pass

class OperandError(Exception): pass

class Definition(object):
    def __init__(self, name, operandWidths):
        self.name = name
        self.operandWidths = operandWidths

DEFINITIONS = DictLikeStruct({
    OPCONSTANT: Definition("OpConstant", [2]),
})

def lookupOpcode(b):
    if not b in DEFINITIONS:
        raise NoSuchOpcodeError(b)
    return DEFINITIONS[b]

def makeInstr(opcode, *operands):
    definition = lookupOpcode(opcode)
    if len(operands) != len(definition.operandWidths):
        raise OperandError("Operand number mismatch. Got %d, want %d" % (len(operands), len(definition.operandWidths)))
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
        raise OperandError("Operand number mismatch. Got %d, want %d" % (len(operands), len(definition.operandWidths)))
    return "%s %s" % (definition.name, ''.join(['%d' % operand for operand in operands]))

def readUint16(instr):
    return int.from_bytes(instr, byteorder='big')

def readOperands(definition, instr):
    operands = []
    offset = 0
    for i, w in enumerate(definition.operandWidths):
        val = readUint16(instr[offset:offset+w])
        offset += w
        operands.append(val)
    return operands, offset
