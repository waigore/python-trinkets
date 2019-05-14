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
    OPJUMP,
    OPJUMPNOTTRUE,
    OPNULL,
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

    def test_simpleExpressions(self):
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

    def test_conditionals(self):
        helper = CompileHelper(self, 'if (true) { 10 } else { 20 }; 3333;')
        helper.checkInstructionsExpected([
            makeInstr(OPTRUE), #0000
            makeInstr(OPJUMPNOTTRUE, 10), #0001
            makeInstr(OPCONSTANT, 0), #0004
            makeInstr(OPJUMP, 13), #0007
            makeInstr(OPCONSTANT, 1),#0010
            makeInstr(OPPOP), #0013
            makeInstr(OPCONSTANT, 2), #0014
            makeInstr(OPPOP), #0017
        ])

        helper = CompileHelper(self, 'if (true) { 10 }')
        helper.checkInstructionsExpected([
            makeInstr(OPTRUE), #0000
            makeInstr(OPJUMPNOTTRUE, 10), #0001
            makeInstr(OPCONSTANT, 0), #0004
            makeInstr(OPJUMP, 11), #0007
            makeInstr(OPNULL),#0010
            makeInstr(OPPOP), #0011
        ])

        helper = CompileHelper(self, 'if (true) { }')
        helper.checkInstructionsExpected([
            makeInstr(OPTRUE), #0000
            makeInstr(OPJUMPNOTTRUE, 8), #0001
            makeInstr(OPNULL), #0004
            makeInstr(OPJUMP, 9), #0005
            makeInstr(OPNULL),#0008
            makeInstr(OPPOP), #0009
        ])

        helper = CompileHelper(self, 'if (true) { 10 } elif (false) { 20 } else { 30 }')
        helper.checkInstructionsExpected([
            makeInstr(OPTRUE), #0000
            makeInstr(OPJUMPNOTTRUE, 10), #0001
            makeInstr(OPCONSTANT, 0), #0004
            makeInstr(OPJUMP, 23), #0007
            makeInstr(OPFALSE), #0010
            makeInstr(OPJUMPNOTTRUE, 20), #0011
            makeInstr(OPCONSTANT, 1), #0014
            makeInstr(OPJUMP, 23), #0017
            makeInstr(OPCONSTANT, 2),#0020
            makeInstr(OPPOP), #0023
        ])

        helper = CompileHelper(self, 'if (true) { 10 } elif (false) {  } else { 30 }')
        helper.checkInstructionsExpected([
            makeInstr(OPTRUE), #0000
            makeInstr(OPJUMPNOTTRUE, 10), #0001
            makeInstr(OPCONSTANT, 0), #0004
            makeInstr(OPJUMP, 21), #0007
            makeInstr(OPFALSE), #0010
            makeInstr(OPJUMPNOTTRUE, 18), #0011
            makeInstr(OPNULL), #0014
            makeInstr(OPJUMP, 21), #0015
            makeInstr(OPCONSTANT, 1),#0018
            makeInstr(OPPOP), #0021
        ])

        helper = CompileHelper(self, 'if (true) { 10 } elif (false) { 20 } else { }')
        helper.checkInstructionsExpected([
            makeInstr(OPTRUE), #0000
            makeInstr(OPJUMPNOTTRUE, 10), #0001
            makeInstr(OPCONSTANT, 0), #0004
            makeInstr(OPJUMP, 21), #0007
            makeInstr(OPFALSE), #0010
            makeInstr(OPJUMPNOTTRUE, 20), #0011
            makeInstr(OPCONSTANT, 1),#0014
            makeInstr(OPJUMP, 21), #0017
            makeInstr(OPNULL), #0020
            makeInstr(OPPOP), #0021
        ])

if __name__ == '__main__':
    unittest.main()
