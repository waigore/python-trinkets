import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from boa.io import (
    inflate,
    deflate,
    BytecodeReader,
    BytecodeWriter,
)
from boa.code import (
    makeInstr,
)
from boa.object import (
    OBJECT_TYPES,
    newInteger,
    newString,
    TRUE,
    FALSE,
    NULL,
)
from boa.version import (
    BUILD_NUMBER,
    VERSION_STRING,
)

from helpers import CompileHelper

class TestIO(unittest.TestCase):
    def test_literalIO(self):
        vals = [
            newInteger(5),
            newInteger(10),
            newInteger(-10000),
            TRUE,
            FALSE,
            NULL,
            newString("abc def"),
            newString("this is a \nstring"),
        ]

        for val in vals:
            deflated = deflate(val)
            inflated, bytesRead = inflate(deflated)
            self.assertEqual(bytesRead, len(deflated))
            self.assertEqual(val.objectType, inflated.objectType)
            self.assertEqual(val.inspect(), inflated.inspect())

    def test_functionIO(self):
        fndefs = [
            ('fn() { let a = 55; let b = 77; a + b }', 2),
            ('fn() { return 5 + 10 }', 2),
        ]

        for fndef, constantIndex in fndefs:
            helper = CompileHelper(self, fndef)
            fn = helper.bytecode.constants[2]
            deflatedFn = deflate(fn)
            inflatedFn, bytesRead = inflate(deflatedFn)
            self.assertEqual(bytesRead, len(deflatedFn))
            self.assertEqual(fn.objectType, inflatedFn.objectType)
            self.assertEqual(fn.objectType, OBJECT_TYPES.OBJECT_TYPE_COMPILED_FUNCTION)
            self.assertEqual(fn.instr, inflatedFn.instr)
            self.assertEqual(fn.numLocals, inflatedFn.numLocals)
            self.assertEqual(fn.numParameters, inflatedFn.numParameters)
            self.assertEqual(fn.inspect(), inflatedFn.inspect())

    def test_codeGenConstantIO(self):
        codeBlocks = [
            'let g = 10; let s = fn(a, b){ let c = a+b; c + g;}; let outer = fn() { s(1, 2)+ s(3, 4)+g;};'
        ]

        for code in codeBlocks:
            helper = CompileHelper(self, code)
            constants = helper.bytecode.constants
            deflatedConstants = [deflate(c) for c in constants]
            inflatedConstantPairs = [inflate(c) for c in deflatedConstants]

            for origConstant, inflatedConstantPair in zip(constants, inflatedConstantPairs):
                inflatedConstant, bytesInflated = inflatedConstantPair
                self.assertEqual(origConstant.objectType, inflatedConstant.objectType)
                self.assertEqual(origConstant.inspect(), inflatedConstant.inspect())

    def test_codeIO(self):
        codeBlocks = [
            'let g = 10; let s = fn(a, b){ let c = a+b; c + g;}; let outer = fn() { s(1, 2)+ s(3, 4)+g;};',
            'let c = 0; let a  = [1, 2, 3, 4, 5]; for (i in a) { c = c + i; if (i > 3) { break;} }; c', 
        ]
        for code in codeBlocks:
            helper = CompileHelper(self, code)
            writer = BytecodeWriter(helper.bytecode)
            instr = writer.write()
            reader = BytecodeReader(instr)
            reader.read()
            self.assertEqual(BUILD_NUMBER, reader.readBuildNumber)
            self.assertEqual(VERSION_STRING, reader.readVersionString)
            self.assertEqual(len(helper.bytecode.constants), len(reader.constants))
            for origConstant, inflatedConstant in zip(helper.bytecode.constants, reader.constants):
                self.assertEqual(origConstant.objectType, inflatedConstant.objectType)
                self.assertEqual(origConstant.inspect(), inflatedConstant.inspect())
            self.assertEqual(helper.bytecode.instr, reader.codeInstr)



if __name__ == '__main__':
    unittest.main()
