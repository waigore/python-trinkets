import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from boa.code import OPCONSTANT, makeInstr, formatInstrs

class TestCode(unittest.TestCase):
    def test_instrFormatting(self):
        instructions = [
            makeInstr(OPCONSTANT, 0),
            makeInstr(OPCONSTANT, 1),
            makeInstr(OPCONSTANT, 65534),
        ]

        instr = formatInstrs(b''.join(instructions))
        self.assertEqual(instr, "0000 OpConstant 0\n0003 OpConstant 1\n0006 OpConstant 65534\n")

    def test_opconstant(self):
        instr = makeInstr(OPCONSTANT, 65534)
        self.assertEqual(instr, OPCONSTANT + b'\xff\xfe')

if __name__ == '__main__':
    unittest.main()
