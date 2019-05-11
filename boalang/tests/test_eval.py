import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from boa.parse import Parser
from boa.evaluator import boaEval
from boa.object import OBJECT_TYPES

class TestEval(unittest.TestCase):
    def test_intLiteral(self):
        code = """5"""
        p = Parser(code)
        prog = p.parseProgram()

        result = boaEval(prog)
        self.assertEqual(result.objectType, OBJECT_TYPES.OBJECT_TYPE_INT)
        self.assertEqual(result.value, 5)

    def test_boolLiteral(self):
        code = """true"""
        p = Parser(code)
        prog = p.parseProgram()

        result = boaEval(prog)
        self.assertEqual(result.objectType, OBJECT_TYPES.OBJECT_TYPE_BOOLEAN)
        self.assertEqual(result.value, True)

    def test_prefixExpressions(self):
        exprs = [
            ("!true", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, False),
            ("!false", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("!5", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, False),
            ("-254", OBJECT_TYPES.OBJECT_TYPE_INT, -254)
        ]

        for code, expectedType, expectedValue in exprs:
            p = Parser(code)
            prog = p.parseProgram()

            result = boaEval(prog)
            self.assertEqual(result.objectType, expectedType)
            self.assertEqual(result.value, expectedValue)


if __name__ == '__main__':
    unittest.main()
