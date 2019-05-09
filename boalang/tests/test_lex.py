import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from boa.lex import Lexer
from boa.token import TOKEN_TYPES

class TestLexing(unittest.TestCase):
    def test_lexBasicAssignment(self):
        code = """let five = 5; let ten = 10;"""
        l = Lexer(code)
        tokens = l.lex()
        tokenTypes = list(map(lambda t: t.tokenType, tokens))

        self.assertEqual(tokenTypes, [
            TOKEN_TYPES.TOKEN_TYPE_LET,
            TOKEN_TYPES.TOKEN_TYPE_IDENT,
            TOKEN_TYPES.TOKEN_TYPE_ASSIGN,
            TOKEN_TYPES.TOKEN_TYPE_INT,
            TOKEN_TYPES.TOKEN_TYPE_SEMICOLON,
            TOKEN_TYPES.TOKEN_TYPE_LET,
            TOKEN_TYPES.TOKEN_TYPE_IDENT,
            TOKEN_TYPES.TOKEN_TYPE_ASSIGN,
            TOKEN_TYPES.TOKEN_TYPE_INT,
            TOKEN_TYPES.TOKEN_TYPE_SEMICOLON,
            TOKEN_TYPES.TOKEN_TYPE_EOF,
        ])

    def test_lexEqNeq(self):
        code = """let equals = 1 == 1; let notEquals = 1 != 1;"""
        l = Lexer(code)
        tokens = l.lex()
        tokenTypes = list(map(lambda t: t.tokenType, tokens))

        self.assertEqual(tokenTypes, [
            TOKEN_TYPES.TOKEN_TYPE_LET,
            TOKEN_TYPES.TOKEN_TYPE_IDENT,
            TOKEN_TYPES.TOKEN_TYPE_ASSIGN,
            TOKEN_TYPES.TOKEN_TYPE_INT,
            TOKEN_TYPES.TOKEN_TYPE_EQ,
            TOKEN_TYPES.TOKEN_TYPE_INT,
            TOKEN_TYPES.TOKEN_TYPE_SEMICOLON,
            TOKEN_TYPES.TOKEN_TYPE_LET,
            TOKEN_TYPES.TOKEN_TYPE_IDENT,
            TOKEN_TYPES.TOKEN_TYPE_ASSIGN,
            TOKEN_TYPES.TOKEN_TYPE_INT,
            TOKEN_TYPES.TOKEN_TYPE_NEQ,
            TOKEN_TYPES.TOKEN_TYPE_INT,
            TOKEN_TYPES.TOKEN_TYPE_SEMICOLON,
            TOKEN_TYPES.TOKEN_TYPE_EOF,
        ])

    def test_lexArithExpression(self):
        code = """let x = (1 + 2) * (3 - (4 * 2));"""
        l = Lexer(code)
        tokens = l.lex()
        tokenTypes = list(map(lambda t: t.tokenType, tokens))

        self.assertEqual(tokenTypes, [
            TOKEN_TYPES.TOKEN_TYPE_LET,
            TOKEN_TYPES.TOKEN_TYPE_IDENT,
            TOKEN_TYPES.TOKEN_TYPE_ASSIGN,
            TOKEN_TYPES.TOKEN_TYPE_LPAREN,
            TOKEN_TYPES.TOKEN_TYPE_INT,
            TOKEN_TYPES.TOKEN_TYPE_PLUS,
            TOKEN_TYPES.TOKEN_TYPE_INT,
            TOKEN_TYPES.TOKEN_TYPE_RPAREN,
            TOKEN_TYPES.TOKEN_TYPE_ASTERISK,
            TOKEN_TYPES.TOKEN_TYPE_LPAREN,
            TOKEN_TYPES.TOKEN_TYPE_INT,
            TOKEN_TYPES.TOKEN_TYPE_MINUS,
            TOKEN_TYPES.TOKEN_TYPE_LPAREN,
            TOKEN_TYPES.TOKEN_TYPE_INT,
            TOKEN_TYPES.TOKEN_TYPE_ASTERISK,
            TOKEN_TYPES.TOKEN_TYPE_INT,
            TOKEN_TYPES.TOKEN_TYPE_RPAREN,
            TOKEN_TYPES.TOKEN_TYPE_RPAREN,
            TOKEN_TYPES.TOKEN_TYPE_SEMICOLON,
            TOKEN_TYPES.TOKEN_TYPE_EOF,
        ])

    def test_lexIdentifiers(self):
        code = """yyyy = x + 1 + x2;"""

        l = Lexer(code)
        tokens = l.lex()
        self.assertEqual(tokens[0].tokenType, TOKEN_TYPES.TOKEN_TYPE_IDENT)

        yyyy = tokens[0]
        self.assertEqual(yyyy.literal, 'yyyy')

        x = tokens[2]
        self.assertEqual(x.literal, 'x')

        x2 = tokens[6]
        self.assertEqual(x2.literal, 'x2')

if __name__ == '__main__':
    unittest.main()
