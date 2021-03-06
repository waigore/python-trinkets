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
    OPLOOPCALL,
    OPCONTINUE,
    OPBREAK,
    OPITER,
    OPITERNEXT,
    OPITERHASNEXT,
    OPCLOSURE,
    OPGETATTR,
    OPSETATTR,
    OPDEFCLASS,
    OPGETCLASS,
    makeInstr,
    formatInstrs,
)

from helpers import CompileHelper

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
            makeInstr(OPJUMPNOTTRUE, 12), #0001
            makeInstr(OPCLOSURE, 1, 0), #0004
            makeInstr(OPBLOCKCALL), #0007
            makeInstr(OPJUMP, 13), #0008
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
            makeInstr(OPJUMPNOTTRUE, 12), #0001
            makeInstr(OPCLOSURE, 0, 0), #0004
            makeInstr(OPBLOCKCALL),
            makeInstr(OPJUMP, 13), #0005
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
            makeInstr(OPJUMPNOTTRUE, 12), #0001
            makeInstr(OPCLOSURE, 1, 0), #0004
            makeInstr(OPBLOCKCALL),
            makeInstr(OPJUMP, 29), #0007
            makeInstr(OPFALSE), #0010
            makeInstr(OPJUMPNOTTRUE, 24), #0011
            makeInstr(OPCLOSURE, 3, 0), #0014
            makeInstr(OPBLOCKCALL),
            makeInstr(OPJUMP, 29), #0017
            makeInstr(OPCLOSURE, 5, 0),#0020
            makeInstr(OPBLOCKCALL),
            makeInstr(OPPOP), #0023
        ])

        helper = CompileHelper(self, 'if (true) { 10 } elif (false) {  } else { 30 }')
        helper.checkInstructionsExpected([
            makeInstr(OPTRUE), #0000
            makeInstr(OPJUMPNOTTRUE, 12), #0001
            makeInstr(OPCLOSURE, 1, 0), #0004
            makeInstr(OPBLOCKCALL), #0007
            makeInstr(OPJUMP, 29), #0007
            makeInstr(OPFALSE), #0010
            makeInstr(OPJUMPNOTTRUE, 24), #0011
            makeInstr(OPCLOSURE, 2, 0),#0018
            makeInstr(OPBLOCKCALL), #0007
            makeInstr(OPJUMP, 29), #0015
            makeInstr(OPCLOSURE, 4, 0),#0018
            makeInstr(OPBLOCKCALL), #0007
            makeInstr(OPPOP), #0021
        ])

        helper = CompileHelper(self, 'if (true) { 10 } elif (false) { 20 } else { }')
        helper.checkInstructionsExpected([
            makeInstr(OPTRUE), #0000
            makeInstr(OPJUMPNOTTRUE, 12), #0001
            makeInstr(OPCLOSURE, 1, 0), #0004
            makeInstr(OPBLOCKCALL), #0007
            makeInstr(OPJUMP, 29), #0008
            makeInstr(OPFALSE), #0011
            makeInstr(OPJUMPNOTTRUE, 24), #0012
            makeInstr(OPCLOSURE, 3, 0),#0015
            makeInstr(OPBLOCKCALL), #0018
            makeInstr(OPJUMP, 29), #0019
            makeInstr(OPCLOSURE, 4, 0), #0022
            makeInstr(OPBLOCKCALL), #0025
            makeInstr(OPPOP), #0026
        ])

    def test_loops(self):
        helper = CompileHelper(self, 'let a = 1; while (a < 10) { a = a + 1; }; a')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0), #0000
            makeInstr(OPSETGLOBAL, 0), #0003
            makeInstr(OPCONSTANT, 1), #0006
            makeInstr(OPGETGLOBAL, 0), #0009
            makeInstr(OPGT), #0012
            makeInstr(OPJUMPNOTTRUE, 25), #0013
            makeInstr(OPCLOSURE, 3, 0), #0016
            makeInstr(OPLOOPCALL, 0), #0019
            makeInstr(OPJUMP, 6), #0021
            makeInstr(OPGETGLOBAL, 0), #0024
            makeInstr(OPPOP),
        ])
        helper.checkConstantsExpected([
            1,
            10,
            1,
            b''.join([
                makeInstr(OPGETGLOBAL, 0), #0009
                makeInstr(OPCONSTANT, 2), #0016
                makeInstr(OPADD), #0016
                makeInstr(OPSETGLOBAL, 0), #0016
                makeInstr(OPCONTINUE), #0000
            ])
        ])

        helper = CompileHelper(self, 'let c = 0; let a = [1, 2, 3]; for (i in a) { c = c + i; }')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0), #let c = 0;
            makeInstr(OPSETGLOBAL, 0),
            makeInstr(OPCONSTANT, 1), #let a = [1, 2, 3];
            makeInstr(OPCONSTANT, 2),
            makeInstr(OPCONSTANT, 3),
            makeInstr(OPARRAY, 3),
            makeInstr(OPSETGLOBAL, 1),
            makeInstr(OPGETGLOBAL, 1), #let <iter> = iter(a);
            makeInstr(OPITER),
            makeInstr(OPSETGLOBAL, 2),
            makeInstr(OPGETGLOBAL, 2), #0028 if <iter>.hasNext()
            makeInstr(OPITERHASNEXT),
            makeInstr(OPJUMPNOTTRUE, 48),
            makeInstr(OPCLOSURE, 4, 0), #<for block>
            makeInstr(OPGETGLOBAL, 2), #iter.next()
            makeInstr(OPITERNEXT),
            makeInstr(OPLOOPCALL, 1), #<for block>()
            makeInstr(OPJUMP, 28),
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

    def test_attributes(self):
        helper = CompileHelper(self, 'let a = "abc"; a.length')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0),
            makeInstr(OPSETGLOBAL, 0),
            makeInstr(OPGETGLOBAL, 0),
            makeInstr(OPCONSTANT, 1),
            makeInstr(OPGETATTR),
            makeInstr(OPPOP),
        ])

        helper = CompileHelper(self, 'let a = "abc"; a.length.length')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0),
            makeInstr(OPSETGLOBAL, 0),
            makeInstr(OPGETGLOBAL, 0),
            makeInstr(OPCONSTANT, 1),
            makeInstr(OPGETATTR),
            makeInstr(OPCONSTANT, 2),
            makeInstr(OPGETATTR),
            makeInstr(OPPOP),
        ])

        helper = CompileHelper(self, 'let a = "abc"; a[0].length[0]')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0),
            makeInstr(OPSETGLOBAL, 0),
            makeInstr(OPGETGLOBAL, 0),
            makeInstr(OPCONSTANT, 1),
            makeInstr(OPINDEX),
            makeInstr(OPCONSTANT, 2),
            makeInstr(OPGETATTR),
            makeInstr(OPCONSTANT, 3),
            makeInstr(OPINDEX),
            makeInstr(OPPOP),
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

    def test_classes(self):
        helper = CompileHelper(self, 'class A {}')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0),
            makeInstr(OPDEFCLASS, 0, 0, 0),
        ])

        helper = CompileHelper(self, 'class A { m1(x) {}; m2(y, z) {}; m3(a) {} }')
        helper.checkInstructionsExpected([
            makeInstr(OPCONSTANT, 0),
            makeInstr(OPCLOSURE, 1, 0),
            makeInstr(OPCONSTANT, 2),
            makeInstr(OPCLOSURE, 3, 0),
            makeInstr(OPCONSTANT, 4),
            makeInstr(OPCLOSURE, 5, 0),
            makeInstr(OPCONSTANT, 6),
            makeInstr(OPDEFCLASS, 0, 0, 6),
        ])

        #helper = CompileHelper(self, 'class A { m1(x) {}; m2(y, z) {}; m3(a) {} }; let a = A()')

if __name__ == '__main__':
    unittest.main()
