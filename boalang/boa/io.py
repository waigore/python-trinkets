from .util import (
    DictLikeStruct,
    readUint16,
    readUint8,
    readUint,
    readInt,
)
from .object import (
    OBJECT_TYPE_INT,
    OBJECT_TYPE_BOOLEAN,
    OBJECT_TYPE_STRING,
    OBJECT_TYPE_NULL,
    OBJECT_TYPE_COMPILED_FUNCTION,
    newInteger,
    newString,
    newCompiledFunction,
    TRUE,
    FALSE,
    NULL,
)
from .version import VERSION_STRING, BUILD_NUMBER

HDRVERS = b'\xF0'
HDRCONS = b'\xF1'
HDRGLOB = b'\xF2'
HDRCODE = b'\xF3'

DEFINT = b'\xA0'
DEFBOOL = b'\xA1'
DEFSTR = b'\xA2'
DEFNULL = b'\xA3'
DEFFUNC = b'\xA4'

#DEFINT 4 x'00FFFFFF'
#DEFBOOL 1 x'01'
#DEFSTR 5 x'0011223344'
#DEFCF 4 4 5 <numLocals> <numParams> <byteinstr>

class BoaDeflateError(Exception): pass

class BoaInflateError(Exception): pass

class BoaBytecodeReadError(Exception): pass

class BytecodeReader(object):
    def __init__(self, instr):
        self.instr = instr

    def incrPointer(self, n):
        self.pointer += n

    def readHeaderOperand(self):
        operand = readUint16(self.instr[self.pointer:])
        self.incrPointer(2)
        return operand

    def read(self):
        self.pointer = 0
        while self.pointer < len(self.instr):
            hdr = self.instr[self.pointer:self.pointer+1]
            self.incrPointer(1)
            if hdr == HDRVERS:
                buildNumber = self.readHeaderOperand()
                versionStringLen = self.readHeaderOperand()
                versionString = self.instr[self.pointer:self.pointer+versionStringLen]
                self.incrPointer(versionStringLen)
                self.checkVersion(buildNumber, versionString)
            elif hdr == HDRCONS:
                constNum = self.readHeaderOperand()
                self.readConstants(constNum)
            elif hdr == HDRCODE:
                codeLen = self.readHeaderOperand()
                self.readCode(codeLen)

    def checkVersion(self, buildNumber, versionString):
        self.readBuildNumber = buildNumber
        self.readVersionString = versionString.decode('ascii')
        if buildNumber > BUILD_NUMBER:
            raise BoaBytecodeReadError("Incompatible version: %d > mine (%d)" % (buildNumber, BUILD_NUMBER))

    def readConstants(self, constNum):
        constants = []
        for i in range(constNum):
            obj, bytesRead = inflate(self.instr[self.pointer:])
            constants.append(obj)
            self.incrPointer(bytesRead)
        self.constants = constants

    def readCode(self, codeLen):
        self.codeInstr = self.instr[self.pointer:self.pointer+codeLen]
        self.incrPointer(codeLen)

class BytecodeWriter(object):
    def __init__(self, bytecode):
        self.bytecode = bytecode

    def write(self):
        versionHdr = self.writeVersion()
        constSection = self.writeConstants()
        codeSection = self.writeCode()
        return versionHdr + constSection + codeSection

    def writeHeaderOperand(self, operand):
        return operand.to_bytes(2, byteorder='big')

    def writeVersion(self):
        bn = self.writeHeaderOperand(BUILD_NUMBER)
        vslen = self.writeHeaderOperand(len(VERSION_STRING))
        vs = VERSION_STRING.encode('ascii')
        return HDRVERS + bn + vslen + vs

    def writeConstants(self):
        b = b''
        for constant in self.bytecode.constants:
            b += deflate(constant)
        constNum = len(self.bytecode.constants)
        return HDRCONS + self.writeHeaderOperand(constNum) + b

    def writeCode(self):
        instr = self.bytecode.instr
        codeLen = len(instr)
        return HDRCODE + self.writeHeaderOperand(codeLen) + instr


class BoaIntInflater(object):
    def __init__(self):
        self.defcode = DEFINT
        self.numOperands = 1

    def inflate(self, bytechunks):
        iRaw = bytechunks[0]
        i = readInt(iRaw, 4)
        return newInteger(i)

    def deflate(self, i):
        iRaw = (i.value).to_bytes(4, byteorder='big', signed=True)
        return [iRaw]

class BoaStringInflater(object):
    def __init__(self):
        self.defcode = DEFSTR
        self.numOperands = 1

    def inflate(self, bytechunks):
        sRaw = bytechunks[0]
        s = sRaw.decode('utf-8')
        return newString(s)

    def deflate(self, s):
        sRaw = s.value.encode('utf-8')
        return [sRaw]

class BoaFunctionInflater(object):
    def __init__(self):
        self.defcode = DEFFUNC
        self.numOperands = 3

    def inflate(self, bytechunks):
        numLocalsRaw = bytechunks[0]
        numParametersRaw = bytechunks[1]
        instr = bytechunks[2]

        numLocals = readInt(numLocalsRaw, 4)
        numParameters = readInt(numParametersRaw, 4)
        return newCompiledFunction(instr, numLocals, numParameters)

    def deflate(self, f):
        numLocalsRaw = (f.numLocals).to_bytes(4, byteorder='big', signed=True)
        numParametersRaw = (f.numParameters).to_bytes(4, byteorder='big', signed=True)
        return [numLocalsRaw, numParametersRaw, f.instr]

class BoaBooleanInflater(object):
    def __init__(self):
        self.defcode = DEFBOOL
        self.numOperands = 1

    def inflate(self, bytechunks):
        boolRaw = bytechunks[0]
        i = readInt(boolRaw, 1)
        return FALSE if i == 0 else TRUE

    def deflate(self, bool):
        i = 1 if bool.value else 0
        iRaw = (i).to_bytes(1, byteorder='big', signed=True)
        return [iRaw]

class BoaNullInflater(object):
    def __init__(self):
        self.defcode = DEFNULL
        self.numOperands = 0

    def deflate(self, n):
        return []

    def inflate(self, bytechunks):
        return NULL

def makeDef(defcode, operands, dataList):
    byteArr = bytearray(defcode)
    for operand in operands:
        oBytes = (operand).to_bytes(2, byteorder='big')
        byteArr += oBytes
    for data in dataList:
        byteArr += data
    return bytes(byteArr)

def deflate(obj):
    if obj.objectType.name not in DEFLATERS:
        raise BoaDeflateError("Cannot deflate: %s" % obj.objectType)

    deflater = DEFLATERS[obj.objectType.name]
    bytesList = deflater.deflate(obj)
    if len(bytesList) != deflater.numOperands:
        raise BoaDeflateError("Number of operands does not match deflated: got %d, want %d" % (len(bytesList), deflater.numOperands))

    operands = [len(b) for b in bytesList]
    return makeDef(deflater.defcode, operands, bytesList)

def inflate(b):
    defcode = bytes(b[0:1])
    if defcode not in INFLATERS:
        raise BoaInflateError("Cannot inflate: %s" % defcode)

    inflater = INFLATERS[defcode]
    operands = []
    for i in range(inflater.numOperands):
        offset = 1 + i*2
        operand = readUint16(b[offset:])
        operands.append(operand)

    dataOffset = 1 + inflater.numOperands*2
    bytechunks = []
    for i in range(inflater.numOperands):
        to = dataOffset + operands[i]
        bytechunks.append(b[dataOffset:to])
        dataOffset += operands[i]

    return inflater.inflate(bytechunks), dataOffset

DEFLATERS = DictLikeStruct({
    OBJECT_TYPE_INT: BoaIntInflater(),
    OBJECT_TYPE_BOOLEAN: BoaBooleanInflater(),
    OBJECT_TYPE_NULL: BoaNullInflater(),
    OBJECT_TYPE_STRING: BoaStringInflater(),
    OBJECT_TYPE_COMPILED_FUNCTION : BoaFunctionInflater(),
})

INFLATERS = DictLikeStruct({
    DEFINT: BoaIntInflater(),
    DEFBOOL: BoaBooleanInflater(),
    DEFNULL: BoaNullInflater(),
    DEFSTR: BoaStringInflater(),
    DEFFUNC: BoaFunctionInflater(),
})
