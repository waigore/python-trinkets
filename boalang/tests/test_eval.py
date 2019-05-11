import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from boa.parse import Parser
from boa.evaluator import boaEval
from boa.environment import Environment
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
            ("-254", OBJECT_TYPES.OBJECT_TYPE_INT, -254),
            ("not true", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, False),
        ]

        for code, expectedType, expectedValue in exprs:
            p = Parser(code)
            prog = p.parseProgram()

            result = boaEval(prog)
            self.assertEqual(result.objectType, expectedType)
            self.assertEqual(result.value, expectedValue)

    def test_infixExpressions(self):
        exprs = [
            ("1 + 1", OBJECT_TYPES.OBJECT_TYPE_INT, 2),
            ("1 - 1", OBJECT_TYPES.OBJECT_TYPE_INT, 0),
            ("1 * 1", OBJECT_TYPES.OBJECT_TYPE_INT, 1),
            ("1 / 1", OBJECT_TYPES.OBJECT_TYPE_INT, 1),
            ("1 == 1", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("1 != 1", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, False),
            ("1 > 1", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, False),
            ("1 > 0", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("1 < 1", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, False),
            ("1 < 2", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("1 <= 2", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("1 >= -1", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("1 + 1 == 2", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("6 * 7 - 1 == 41", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("true == true", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("true == false", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, False),
            ("true != true", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, False),
            ("true != false", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
        ]

        for code, expectedType, expectedValue in exprs:
            p = Parser(code)
            prog = p.parseProgram()

            result = boaEval(prog)
            self.assertEqual(result.objectType, expectedType)
            self.assertEqual(result.value, expectedValue)

    def test_ifExpressions(self):
        exprs = [
            ("if (5 * 5 + 10 > 34) { 99 } else { 100 }", OBJECT_TYPES.OBJECT_TYPE_INT, 99),
        ]

        for code, expectedType, expectedValue in exprs:
            p = Parser(code)
            prog = p.parseProgram()

            result = boaEval(prog)
            self.assertEqual(result.objectType, expectedType)
            self.assertEqual(result.value, expectedValue)

    def test_returnStatements(self):
        exprs = [
            ("""
                if (10 > 1) {
                    if (10 > 1) {
                        return 10;
                    }
                    return 1;
                }
            """, OBJECT_TYPES.OBJECT_TYPE_INT, 10)
        ]

        for code, expectedType, expectedValue in exprs:
            p = Parser(code)
            prog = p.parseProgram()

            result = boaEval(prog)
            self.assertEqual(result.objectType, expectedType)
            self.assertEqual(result.value, expectedValue)

    def test_evalErrors(self):
        exprs = [
            ("true + false", OBJECT_TYPES.OBJECT_TYPE_ERROR),
        ]

        for code, expectedType in exprs:
            p = Parser(code)
            prog = p.parseProgram()

            result = boaEval(prog)
            self.assertEqual(result.objectType, expectedType)

if __name__ == '__main__':
    unittest.main()
