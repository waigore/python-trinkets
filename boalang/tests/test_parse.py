import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from boa.ast import (
    STATEMENT_TYPE_RETURN,
    STATEMENT_TYPE_EXPRESSION,
    EXPRESSION_TYPE_INT_LIT,
    EXPRESSION_TYPE_IDENT,
    EXPRESSION_TYPE_PREFIX,
    EXPRESSION_TYPE_INFIX
)
from boa.parse import Parser
from boa.lex import Lexer
from boa.token import TOKEN_TYPES

class TestParsing(unittest.TestCase):
    def test_lets(self):
        code = """let five = 5; let ten = 10; let foobar = y;"""
        p = Parser(code)
        prog = p.parseProgram()
        self.assertEqual(len(prog.statements), 3)

        idents = list(map(lambda s: s.identifier.value, prog.statements))
        valueTypes = list(map(lambda s: s.value.expressionType, prog.statements))
        valueLiterals = list(map(lambda s: s.value.value, prog.statements))
        self.assertEqual(idents, ['five', 'ten', 'foobar'])
        self.assertEqual(valueTypes, [EXPRESSION_TYPE_INT_LIT, EXPRESSION_TYPE_INT_LIT, EXPRESSION_TYPE_IDENT])
        self.assertEqual(valueLiterals, [5, 10, "y"])

    def test_returns(self):
        code = """return 1; return 5; return 999321; """
        p = Parser(code)
        prog = p.parseProgram()
        self.assertEqual(len(prog.statements), 3)

        statementTypes = list(map(lambda s: s.statementType, prog.statements))
        returnValues = list(map(lambda s: s.value, prog.statements))
        self.assertEqual(statementTypes, [STATEMENT_TYPE_RETURN, STATEMENT_TYPE_RETURN, STATEMENT_TYPE_RETURN])
        self.assertEqual(returnValues[0].expressionType, EXPRESSION_TYPE_INT_LIT)
        self.assertEqual(returnValues[1].expressionType, EXPRESSION_TYPE_INT_LIT)
        self.assertEqual(returnValues[2].expressionType, EXPRESSION_TYPE_INT_LIT)

    def test_identsAndLiterals(self):
        code = """foobar; 5;"""
        p = Parser(code)
        prog = p.parseProgram()
        self.assertEqual(len(prog.statements), 2)

        statement1 = prog.statements[0]
        self.assertEqual(statement1.statementType, STATEMENT_TYPE_EXPRESSION)
        self.assertEqual(statement1.expression.expressionType, EXPRESSION_TYPE_IDENT)
        self.assertEqual(statement1.expression.value, "foobar")

        statement2 = prog.statements[1]
        self.assertEqual(statement2.statementType, STATEMENT_TYPE_EXPRESSION)
        self.assertEqual(statement2.expression.expressionType, EXPRESSION_TYPE_INT_LIT)
        self.assertEqual(statement2.expression.value, 5)

    def test_prefixExpressions(self):
        code = """-5; !15;"""
        p = Parser(code)
        prog = p.parseProgram()
        self.assertEqual(len(prog.statements), 2)

        statement1 = prog.statements[0]
        self.assertEqual(statement1.statementType, STATEMENT_TYPE_EXPRESSION)
        self.assertEqual(statement1.expression.expressionType, EXPRESSION_TYPE_PREFIX)
        self.assertEqual(statement1.expression.operator, '-')
        self.assertEqual(statement1.expression.right.value, 5)

        statement2 = prog.statements[1]
        self.assertEqual(statement2.statementType, STATEMENT_TYPE_EXPRESSION)
        self.assertEqual(statement2.expression.expressionType, EXPRESSION_TYPE_PREFIX)
        self.assertEqual(statement2.expression.operator, '!')
        self.assertEqual(statement2.expression.right.value, 15)

    def test_infixExpressions(self):
        code = """5 + 6; 7 * 5;"""
        p = Parser(code)
        prog = p.parseProgram()
        self.assertEqual(len(prog.statements), 2)

        statement1 = prog.statements[0]
        self.assertEqual(statement1.statementType, STATEMENT_TYPE_EXPRESSION)
        self.assertEqual(statement1.expression.expressionType, EXPRESSION_TYPE_INFIX)
        self.assertEqual(statement1.expression.operator, '+')
        self.assertEqual(statement1.expression.left.value, 5)
        self.assertEqual(statement1.expression.right.value, 6)

        statement2 = prog.statements[1]
        self.assertEqual(statement2.statementType, STATEMENT_TYPE_EXPRESSION)
        self.assertEqual(statement2.expression.expressionType, EXPRESSION_TYPE_INFIX)
        self.assertEqual(statement2.expression.operator, '*')
        self.assertEqual(statement2.expression.left.value, 7)
        self.assertEqual(statement2.expression.right.value, 5)

    def test_operatorPrecedence(self):
        exprs = [
            ("-a * b", "((-a) * b)"),
            ("-a - b", "((-a) - b)"),
            ("!-a", "(!(-a))"),
            ("- a", "(-a)"),
            ("a + b + c", "((a + b) + c)"),
            ("a + b - c", "((a + b) - c)"),
            ("a * b * c", "((a * b) * c)"),
            ("a * b / c", "((a * b) / c)"),
            ("a + b / c", "(a + (b / c))"),
            ("a + b * c + d / e - f", "(((a + (b * c)) + (d / e)) - f)"),
            ("5 > 4 == 3 < 4", "((5 > 4) == (3 < 4))"),
            ("5 < 4 != 3 > 4", "((5 < 4) != (3 > 4))"),
            ("5 >= 4 == 3 <= 4", "((5 >= 4) == (3 <= 4))"),
            ("3 + 4 * 5 == 3 * 1 + 4 * 5", "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))"),
            ("not a", "(not a)"),
            ("not not a", "(not (not a))"),
            ("a and b", "(a and b)"),
            ("not a and b", "((not a) and b)"),
        ]

        for pair in exprs:
            code, expected = pair
            p = Parser(code)
            prog = p.parseProgram()
            self.assertEqual(len(prog.statements), 1)

            statement = prog.statements[0]
            self.assertEqual(statement.statementType, STATEMENT_TYPE_EXPRESSION)
            self.assertEqual(str(statement.expression), expected)

    def test_parseWithErrors(self):
        code = """let = 5;"""

        l = Lexer(code)
        tokens = l.lex()
        self.assertEqual(tokens[1].tokenType, TOKEN_TYPES.TOKEN_TYPE_ASSIGN)

        p = Parser(code)
        prog = p.parseProgram()
        self.assertTrue(len(p.errors)> 0)


if __name__ == '__main__':
    unittest.main()
