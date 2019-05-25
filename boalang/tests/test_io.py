import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from boa.io import (
    inflate,
    deflate,
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
            inflated = inflate(deflated)
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
            inflatedFn = inflate(deflatedFn)
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
            inflatedConstants = [inflate(c) for c in deflatedConstants]

            for origConstant, inflatedConstant in zip(constants, inflatedConstants):
                self.assertEqual(origConstant.objectType, inflatedConstant.objectType)
                self.assertEqual(origConstant.inspect(), inflatedConstant.inspect())


if __name__ == '__main__':
    unittest.main()
