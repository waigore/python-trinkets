import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from boa.ast import STATEMENT_TYPE_RETURN
from boa.parse import Parser
from boa.token import TOKEN_TYPES

class TestParsing(unittest.TestCase):
    def test_parseBasicAssignments(self):
        code = """let five = 5; let ten = 10;"""
        p = Parser(code)
        prog = p.parseProgram()
        self.assertEqual(len(prog.statements), 2)

        idents = list(map(lambda s: s.identifier.value, prog.statements))
        self.assertEqual(idents, ['five', 'ten'])

    def test_parseReturns(self):
        code = """return 1; """
        p = Parser(code)
        prog = p.parseProgram()
        self.assertEqual(len(prog.statements), 1)

        statementTypes = list(map(lambda s: s.statementType, prog.statements))
        self.assertEqual(statementTypes, [STATEMENT_TYPE_RETURN])


    def test_parseWithErrors(self):
        code = """let = 5;"""
        p = Parser(code)
        prog = p.parseProgram()
        self.assertEqual(len(prog.statements), 0)
        self.assertEqual(len(p.errors), 1)


if __name__ == '__main__':
    unittest.main()
