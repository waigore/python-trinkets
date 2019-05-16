import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from boa.code import (
    OPCONSTANT,
    OPADD,
    OPMUL,
    OPPOP,
    OPGT,
    OPTRUE,
    OPFALSE,
    OPMINUS,
    OPNOT,
    OPJUMP,
    OPJUMPNOTTRUE,
    OPNULL,
    OPGETGLOBAL,
    OPSETGLOBAL,
    OPARRAY,
    OPHASH,
    OPINDEX,
    OPRETURNVALUE,
    OPSETLOCAL,
    OPGETLOCAL,
    OPSETINDEX,
    OPBLOCKCALL,
    OPBLOCKRETURN,
    makeInstr,
    formatInstrs,
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
        helper = CompileHelper(self, '"abcd"')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0),
            makeInstr(OPPOP),
        ])

        helper = CompileHelper(self, '"abcd" + "defg"')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0),
            makeInstr(OPCONSTANT, 1),
            makeInstr(OPADD),
            makeInstr(OPPOP),
        ])

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
        helper = CompileHelper(self, 'if (true) { 10 }')
        helper.checkInstructionsExpected([
            makeInstr(OPTRUE), #0000
            makeInstr(OPJUMPNOTTRUE, 11), #0001
            makeInstr(OPCONSTANT, 1), #0004
            makeInstr(OPBLOCKCALL), #0007
            makeInstr(OPJUMP, 12), #0008
            makeInstr(OPNULL),#0011
            makeInstr(OPPOP), #0012
        ])
        helper.checkConstantsExpected([
            10,
            b''.join([
                makeInstr(OPCONSTANT, 0),
                makeInstr(OPBLOCKRETURN), #0000
            ])
        ])

        helper = CompileHelper(self, 'if (true) { }')
        helper.checkInstructionsExpected([
            makeInstr(OPTRUE), #0000
            makeInstr(OPJUMPNOTTRUE, 11), #0001
            makeInstr(OPCONSTANT, 0), #0004
            makeInstr(OPBLOCKCALL),
            makeInstr(OPJUMP, 12), #0005
            makeInstr(OPNULL),
            makeInstr(OPPOP), #0009
        ])
        helper.checkConstantsExpected([
            b''.join([
                makeInstr(OPNULL),
                makeInstr(OPBLOCKRETURN), #0000
            ])
        ])

        helper = CompileHelper(self, 'if (true) { 10 } elif (false) { 20 } else { 30 }')
        helper.checkInstructionsExpected([
            makeInstr(OPTRUE), #0000
            makeInstr(OPJUMPNOTTRUE, 11), #0001
            makeInstr(OPCONSTANT, 1), #0004
            makeInstr(OPBLOCKCALL),
            makeInstr(OPJUMP, 26), #0007
            makeInstr(OPFALSE), #0010
            makeInstr(OPJUMPNOTTRUE, 22), #0011
            makeInstr(OPCONSTANT, 3), #0014
            makeInstr(OPBLOCKCALL),
            makeInstr(OPJUMP, 26), #0017
            makeInstr(OPCONSTANT, 5),#0020
            makeInstr(OPBLOCKCALL),
            makeInstr(OPPOP), #0023
        ])

        helper = CompileHelper(self, 'if (true) { 10 } elif (false) {  } else { 30 }')
        helper.checkInstructionsExpected([
            makeInstr(OPTRUE), #0000
            makeInstr(OPJUMPNOTTRUE, 11), #0001
            makeInstr(OPCONSTANT, 1), #0004
            makeInstr(OPBLOCKCALL), #0007
            makeInstr(OPJUMP, 26), #0007
            makeInstr(OPFALSE), #0010
            makeInstr(OPJUMPNOTTRUE, 22), #0011
            makeInstr(OPCONSTANT, 2),#0018
            makeInstr(OPBLOCKCALL), #0007
            makeInstr(OPJUMP, 26), #0015
            makeInstr(OPCONSTANT, 4),#0018
            makeInstr(OPBLOCKCALL), #0007
            makeInstr(OPPOP), #0021
        ])

        helper = CompileHelper(self, 'if (true) { 10 } elif (false) { 20 } else { }')
        helper.checkInstructionsExpected([
            makeInstr(OPTRUE), #0000
            makeInstr(OPJUMPNOTTRUE, 11), #0001
            makeInstr(OPCONSTANT, 1), #0004
            makeInstr(OPBLOCKCALL), #0007
            makeInstr(OPJUMP, 26), #0008
            makeInstr(OPFALSE), #0011
            makeInstr(OPJUMPNOTTRUE, 22), #0012
            makeInstr(OPCONSTANT, 3),#0015
            makeInstr(OPBLOCKCALL), #0018
            makeInstr(OPJUMP, 26), #0019
            makeInstr(OPCONSTANT, 4), #0022
            makeInstr(OPBLOCKCALL), #0025
            makeInstr(OPPOP), #0026
        ])

    def test_letsAndIdents(self):
        helper = CompileHelper(self, 'let a = 1; let b = 2;')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0), #0000
            makeInstr(OPSETGLOBAL, 0), #0003
            makeInstr(OPCONSTANT, 1), #0006
            makeInstr(OPSETGLOBAL, 1), #0009
        ])

        helper = CompileHelper(self, 'let a = 1; a + 1')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0), #0000
            makeInstr(OPSETGLOBAL, 0), #0003
            makeInstr(OPGETGLOBAL, 0), #0006
            makeInstr(OPCONSTANT, 1), #0009
            makeInstr(OPADD), #0012
            makeInstr(OPPOP), #0013
        ])

        helper = CompileHelper(self, 'let a = 1; let b = a; b = a + 1')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0), #0000
            makeInstr(OPSETGLOBAL, 0), #0003
            makeInstr(OPGETGLOBAL, 0), #0006
            makeInstr(OPSETGLOBAL, 1), #0003
            makeInstr(OPGETGLOBAL, 0), #0006
            makeInstr(OPCONSTANT, 1), #0000
            makeInstr(OPADD), #0012
            makeInstr(OPSETGLOBAL, 1), #0003
        ])

    def test_arrays(self):
        helper = CompileHelper(self, '[]')
        helper.checkInstructionsExpected([
            makeInstr(OPARRAY, 0), #0009
            makeInstr(OPPOP), #0012
        ])

        helper = CompileHelper(self, '[1, 2, 3]')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0), #0000
            makeInstr(OPCONSTANT, 1), #0003
            makeInstr(OPCONSTANT, 2), #0006
            makeInstr(OPARRAY, 3), #0009
            makeInstr(OPPOP), #0012
        ])

        helper = CompileHelper(self, '[1, 1 + 2]')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0), #0000
            makeInstr(OPCONSTANT, 1), #0003
            makeInstr(OPCONSTANT, 2), #0006
            makeInstr(OPADD),
            makeInstr(OPARRAY, 2), #0009
            makeInstr(OPPOP), #0012
        ])

        helper = CompileHelper(self, '[1, 1 + 2][0]')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0), #0000
            makeInstr(OPCONSTANT, 1), #0003
            makeInstr(OPCONSTANT, 2), #0006
            makeInstr(OPADD),
            makeInstr(OPARRAY, 2), #0009
            makeInstr(OPCONSTANT, 3),
            makeInstr(OPINDEX),
            makeInstr(OPPOP), #0012
        ])

        helper = CompileHelper(self, 'let a = [1, 2]; a[0] = 3;')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0), #0000
            makeInstr(OPCONSTANT, 1), #0000
            makeInstr(OPARRAY, 2), #0009
            makeInstr(OPSETGLOBAL, 0),
            makeInstr(OPGETGLOBAL, 0),
            makeInstr(OPCONSTANT, 2), #0000
            makeInstr(OPCONSTANT, 3), #0000
            makeInstr(OPSETINDEX),
        ])

    def test_hashes(self):
        helper = CompileHelper(self, '{1:2+3, 4:5*6}[0]')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0), #0000
            makeInstr(OPCONSTANT, 1), #0000
            makeInstr(OPCONSTANT, 2), #0000
            makeInstr(OPADD), #0000
            makeInstr(OPCONSTANT, 3), #0000
            makeInstr(OPCONSTANT, 4), #0000
            makeInstr(OPCONSTANT, 5), #0000
            makeInstr(OPMUL), #0000
            makeInstr(OPHASH, 4),
            makeInstr(OPCONSTANT, 6),
            makeInstr(OPINDEX),
            makeInstr(OPPOP), #0012
        ])

    def test_functions(self):
        helper = CompileHelper(self, 'fn() { return 5 + 10 }')
        helper.checkConstantsExpected([
            5,
            10,
            b''.join([
                makeInstr(OPCONSTANT, 0), #0000
                makeInstr(OPCONSTANT, 1), #0000
                makeInstr(OPADD), #0000
                makeInstr(OPRETURNVALUE), #0000
            ])
        ])

        helper = CompileHelper(self, 'fn() { 5 + 10 }')
        helper.checkConstantsExpected([
            5,
            10,
            b''.join([
                makeInstr(OPCONSTANT, 0), #0000
                makeInstr(OPCONSTANT, 1), #0000
                makeInstr(OPADD), #0000
                makeInstr(OPRETURNVALUE), #0000
            ])
        ])

        helper = CompileHelper(self, 'fn() {  }')
        helper.checkConstantsExpected([
            b''.join([
                makeInstr(OPNULL), #0000
                makeInstr(OPRETURNVALUE), #0000
            ])
        ])

        helper = CompileHelper(self, 'let num = 55; fn() { num }')
        helper.checkConstantsExpected([
            55,
            b''.join([
                makeInstr(OPGETGLOBAL, 0), #0000
                makeInstr(OPRETURNVALUE), #0000
            ])
        ])

        helper = CompileHelper(self, 'fn() { let num = 55; num }')
        helper.checkConstantsExpected([
            55,
            b''.join([
                makeInstr(OPCONSTANT, 0),
                makeInstr(OPSETLOCAL, 0), #0000
                makeInstr(OPGETLOCAL, 0), #0000
                makeInstr(OPRETURNVALUE), #0000
            ])
        ])

        helper = CompileHelper(self, 'fn() { let a = 55; let b = 77; a + b }')
        helper.checkConstantsExpected([
            55,
            77,
            b''.join([
                makeInstr(OPCONSTANT, 0),
                makeInstr(OPSETLOCAL, 0), #0000
                makeInstr(OPCONSTANT, 1),
                makeInstr(OPSETLOCAL, 1), #0000
                makeInstr(OPGETLOCAL, 0), #0000
                makeInstr(OPGETLOCAL, 1), #0000
                makeInstr(OPADD), #0000
                makeInstr(OPRETURNVALUE), #0000
            ])
        ])

if __name__ == '__main__':
    unittest.main()
