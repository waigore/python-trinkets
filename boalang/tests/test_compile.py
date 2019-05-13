import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from boa.code import (
    OPCONSTANT,
    OPADD,
    OPPOP,
    OPGT,
    OPTRUE,
    OPFALSE,
    OPMINUS,
    OPNOT,
    makeInstr,
)
from boa.compile import Compiler
from boa.parse import Parser

class CompileHelper(object):
    def __init__(self, testCase, code):
        self.code = code
        self.testCase = testCase

        self.parser = Parser(code)
        program = self.parser.parseProgram()

        self.compiler = Compiler()
        self.compiler.compile(program)
        self.bytecode = self.compiler.bytecode()

    def checkInstructionsExpected(self, instructions):
        self.testCase.assertEqual(self.bytecode.instructions, instructions)

    def checkConstantsExpected(self, constants):
        cVals = [c.value for c in self.bytecode.constants]
        self.testCase.assertEqual(len(cVals), len(constants))
        for c, expectedC in zip(cVals, constants):
            self.testCase.assertEqual(c, expectedC)


class TestCompilation(unittest.TestCase):
    def test_opconstant(self):
        helper = CompileHelper(self, '3 + 5')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0),
            makeInstr(OPCONSTANT, 1),
            makeInstr(OPADD),
            makeInstr(OPPOP),
        ])
        helper.checkConstantsExpected([3, 5])

    def test_expressions(self):
        helper = CompileHelper(self, '3 + 5; 2; true; false')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0),
            makeInstr(OPCONSTANT, 1),
            makeInstr(OPADD),
            makeInstr(OPPOP),
            makeInstr(OPCONSTANT, 2),
            makeInstr(OPPOP),
            makeInstr(OPTRUE),
            makeInstr(OPPOP),
            makeInstr(OPFALSE),
            makeInstr(OPPOP),
        ])
        helper.checkConstantsExpected([3, 5, 2])

        helper = CompileHelper(self, '1 < 2')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0),
            makeInstr(OPCONSTANT, 1),
            makeInstr(OPGT),
            makeInstr(OPPOP),
        ])

        helper = CompileHelper(self, '-5')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0),
            makeInstr(OPMINUS),
            makeInstr(OPPOP),
        ])

if __name__ == '__main__':
    unittest.main()
