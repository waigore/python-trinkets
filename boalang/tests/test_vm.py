import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from boa.code import OPCONSTANT, makeInstr
from boa.compile import Compiler
from boa.object import OBJECT_TYPES
from boa.parse import Parser
from boa.vm import VM

class VMHelper(object):
    def __init__(self, testCase, code):
        self.code = code
        self.testCase = testCase

        self.parser = Parser(code)
        program = self.parser.parseProgram()

        self.compiler = Compiler()
        self.compiler.compile(program)
        self.bytecode = self.compiler.bytecode()

        self.vm = VM(self.bytecode)
        self.vm.run()

    def checkStackExpected(self, expectedPairs):
        inspectedStack = self.vm.inspectStack()
        self.testCase.assertEqual(len(expectedPairs), len(inspectedStack))
        for stackEl, expectedPair in zip(inspectedStack, expectedPairs):
            expectedType, expectedVal = expectedPair
            self.testCase.assertEqual(stackEl.objectType, expectedType)
            self.testCase.assertEqual(stackEl.inspect(), expectedVal)

    def checkStackTopExpected(self, expectedType, expectedValue):
        obj = self.vm.stackTop()
        self.testCase.assertEqual(obj.objectType, expectedType)
        self.testCase.assertEqual(obj.inspect(), expectedValue)

class TestVM(unittest.TestCase):
    def test_opconstant(self):
        helper = VMHelper(self, '3 + 5')
        helper.checkStackTopExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '8')

        helper = VMHelper(self, '1 + 2 + 3 + 4')
        helper.checkStackTopExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '10')
