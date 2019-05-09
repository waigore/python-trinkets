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

if __name__ == '__main__':
    unittest.main()
