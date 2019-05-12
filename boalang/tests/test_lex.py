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

        yyyy = tokens[0]
        self.assertEqual(yyyy.tokenType, TOKEN_TYPES.TOKEN_TYPE_IDENT)
        self.assertEqual(yyyy.literal, 'yyyy')

        x = tokens[2]
        self.assertEqual(x.tokenType, TOKEN_TYPES.TOKEN_TYPE_IDENT)
        self.assertEqual(x.literal, 'x')

        x2 = tokens[6]
        self.assertEqual(x2.tokenType, TOKEN_TYPES.TOKEN_TYPE_IDENT)
        self.assertEqual(x2.literal, 'x2')

    def test_lexBooleansAndNull(self):
        code = """return true; return false; null;"""
        l = Lexer(code)
        tokens = l.lex()
        tokenTypes = list(map(lambda t: t.tokenType, tokens))

        self.assertEqual(tokenTypes, [
            TOKEN_TYPES.TOKEN_TYPE_RETURN,
            TOKEN_TYPES.TOKEN_TYPE_TRUE,
            TOKEN_TYPES.TOKEN_TYPE_SEMICOLON,
            TOKEN_TYPES.TOKEN_TYPE_RETURN,
            TOKEN_TYPES.TOKEN_TYPE_FALSE,
            TOKEN_TYPES.TOKEN_TYPE_SEMICOLON,
            TOKEN_TYPES.TOKEN_TYPE_NULL,
            TOKEN_TYPES.TOKEN_TYPE_SEMICOLON,
            TOKEN_TYPES.TOKEN_TYPE_EOF,
        ])

    def test_lexNot(self):
        code = """not a; ! a; nota; """
        l = Lexer(code)
        tokens = l.lex()
        tokenTypes = list(map(lambda t: t.tokenType, tokens))

        self.assertEqual(tokenTypes, [
            TOKEN_TYPES.TOKEN_TYPE_NOT,
            TOKEN_TYPES.TOKEN_TYPE_IDENT,
            TOKEN_TYPES.TOKEN_TYPE_SEMICOLON,
            TOKEN_TYPES.TOKEN_TYPE_EXCLAMATION,
            TOKEN_TYPES.TOKEN_TYPE_IDENT,
            TOKEN_TYPES.TOKEN_TYPE_SEMICOLON,
            TOKEN_TYPES.TOKEN_TYPE_IDENT,
            TOKEN_TYPES.TOKEN_TYPE_SEMICOLON,
            TOKEN_TYPES.TOKEN_TYPE_EOF,
        ])

    def test_lexAndOr(self):
        code = """a and b; aandb; a or b; """
        l = Lexer(code)
        tokens = l.lex()
        tokenTypes = list(map(lambda t: t.tokenType, tokens))

        self.assertEqual(tokenTypes, [
            TOKEN_TYPES.TOKEN_TYPE_IDENT,
            TOKEN_TYPES.TOKEN_TYPE_AND,
            TOKEN_TYPES.TOKEN_TYPE_IDENT,
            TOKEN_TYPES.TOKEN_TYPE_SEMICOLON,
            TOKEN_TYPES.TOKEN_TYPE_IDENT,
            TOKEN_TYPES.TOKEN_TYPE_SEMICOLON,
            TOKEN_TYPES.TOKEN_TYPE_IDENT,
            TOKEN_TYPES.TOKEN_TYPE_OR,
            TOKEN_TYPES.TOKEN_TYPE_IDENT,
            TOKEN_TYPES.TOKEN_TYPE_SEMICOLON,
            TOKEN_TYPES.TOKEN_TYPE_EOF,
        ])

    def test_lexWhile(self):
        code = """ while (true) { a; } """
        l = Lexer(code)
        tokens = l.lex()
        tokenTypes = list(map(lambda t: t.tokenType, tokens))

        self.assertEqual(tokenTypes, [
            TOKEN_TYPES.TOKEN_TYPE_WHILE,
            TOKEN_TYPES.TOKEN_TYPE_LPAREN,
            TOKEN_TYPES.TOKEN_TYPE_TRUE,
            TOKEN_TYPES.TOKEN_TYPE_RPAREN,
            TOKEN_TYPES.TOKEN_TYPE_LBRACE,
            TOKEN_TYPES.TOKEN_TYPE_IDENT,
            TOKEN_TYPES.TOKEN_TYPE_SEMICOLON,
            TOKEN_TYPES.TOKEN_TYPE_RBRACE,
            TOKEN_TYPES.TOKEN_TYPE_EOF,
        ])

    def test_arraysAndHashes(self):
        code = """[1, '2']; {1: "1", 2: "2"}"""
        l = Lexer(code)
        tokens = l.lex()
        tokenTypes = list(map(lambda t: t.tokenType, tokens))

        self.assertEqual(tokenTypes, [
            TOKEN_TYPES.TOKEN_TYPE_LBRACKET,
            TOKEN_TYPES.TOKEN_TYPE_INT,
            TOKEN_TYPES.TOKEN_TYPE_COMMA,
            TOKEN_TYPES.TOKEN_TYPE_STR,
            TOKEN_TYPES.TOKEN_TYPE_RBRACKET,
            TOKEN_TYPES.TOKEN_TYPE_SEMICOLON,
            TOKEN_TYPES.TOKEN_TYPE_LBRACE,
            TOKEN_TYPES.TOKEN_TYPE_INT,
            TOKEN_TYPES.TOKEN_TYPE_COLON,
            TOKEN_TYPES.TOKEN_TYPE_STR,
            TOKEN_TYPES.TOKEN_TYPE_COMMA,
            TOKEN_TYPES.TOKEN_TYPE_INT,
            TOKEN_TYPES.TOKEN_TYPE_COLON,
            TOKEN_TYPES.TOKEN_TYPE_STR,
            TOKEN_TYPES.TOKEN_TYPE_RBRACE,
            TOKEN_TYPES.TOKEN_TYPE_EOF,
        ])

    def test_strings(self):
        exprs = [
            ('"foobar"', [TOKEN_TYPES.TOKEN_TYPE_STR], ["foobar"]),
            ("'foo bar'", [TOKEN_TYPES.TOKEN_TYPE_STR], ["foo bar"]),
            ("'foobar'+ 'a'", [TOKEN_TYPES.TOKEN_TYPE_STR, TOKEN_TYPES.TOKEN_TYPE_PLUS, TOKEN_TYPES.TOKEN_TYPE_STR], ["foobar", "+", "a"]),
        ]
        for expr, expectedTypes, expectedValues in exprs:
            l = Lexer(expr)
            tokens = l.lex()
            tokenTypes = list(map(lambda t: t.tokenType, tokens))
            tokenLiterals = list(map(lambda t: t.literal, tokens))

            expectedTypes.extend([TOKEN_TYPES.TOKEN_TYPE_EOF])

            self.assertEqual(tokenTypes, expectedTypes)

    def test_lexComments(self):
        code = """1; //3; 4;"""
        l = Lexer(code)
        tokens = l.lex()
        tokenTypes = list(map(lambda t: t.tokenType, tokens))

        self.assertEqual(tokenTypes, [
            TOKEN_TYPES.TOKEN_TYPE_INT,
            TOKEN_TYPES.TOKEN_TYPE_SEMICOLON,
            TOKEN_TYPES.TOKEN_TYPE_COMMENT,
            TOKEN_TYPES.TOKEN_TYPE_EOF,
        ])

if __name__ == '__main__':
    unittest.main()
