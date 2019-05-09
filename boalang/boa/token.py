
from .util import DictLikeStruct

TOKEN_TYPE_ILLEGAL = 'TOKEN_TYPE_ILLEGAL'
TOKEN_TYPE_EOF = 'TOKEN_TYPE_EOF'
TOKEN_TYPE_IDENT = 'TOKEN_TYPE_IDENT'
TOKEN_TYPE_INT = 'TOKEN_TYPE_INT'
TOKEN_TYPE_ASSIGN = 'TOKEN_TYPE_ASSIGN'
TOKEN_TYPE_PLUS = 'TOKEN_TYPE_PLUS'
TOKEN_TYPE_COMMA = 'TOKEN_TYPE_COMMA'
TOKEN_TYPE_SEMICOLON = 'TOKEN_TYPE_SEMICOLON'
TOKEN_TYPE_LPAREN = 'TOKEN_TYPE_LPAREN'
TOKEN_TYPE_RPAREN = 'TOKEN_TYPE_RPAREN'
TOKEN_TYPE_LBRACE = 'TOKEN_TYPE_LBRACE'
TOKEN_TYPE_RBRACE = 'TOKEN_TYPE_RBRACE'
TOKEN_TYPE_FUNCTION = 'TOKEN_TYPE_FUNCTION'
TOKEN_TYPE_LET = 'TOKEN_TYPE_LET'

KEYWORD_FUNCTION = 'fn'
KEYWORD_LET = 'let'

class TokenType(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value

    def __repr__(self):
        return '[%s %s]' % (self.name, self.value)

class Token(object):
    def __init__(self, tokenType, literal):
        self.tokenType = tokenType
        self.literal = literal

    def __repr__(self):
        return '[%s "%s"]' % (self.tokenType, self.literal)

TOKEN_TYPES = DictLikeStruct({
    TOKEN_TYPE_ILLEGAL: TokenType(TOKEN_TYPE_ILLEGAL, 'ILLEGAL'),
    TOKEN_TYPE_EOF: TokenType(TOKEN_TYPE_EOF, 'EOF'),
    TOKEN_TYPE_IDENT: TokenType(TOKEN_TYPE_IDENT, 'IDENT'),
    TOKEN_TYPE_INT: TokenType(TOKEN_TYPE_IDENT, 'INT'),
    TOKEN_TYPE_ASSIGN: TokenType(TOKEN_TYPE_ASSIGN, '='),
    TOKEN_TYPE_PLUS: TokenType(TOKEN_TYPE_PLUS, '+'),
    TOKEN_TYPE_COMMA: TokenType(TOKEN_TYPE_COMMA, ','),
    TOKEN_TYPE_SEMICOLON: TokenType(TOKEN_TYPE_SEMICOLON, ';'),
    TOKEN_TYPE_LPAREN: TokenType(TOKEN_TYPE_LPAREN, '('),
    TOKEN_TYPE_RPAREN: TokenType(TOKEN_TYPE_RPAREN, ')'),
    TOKEN_TYPE_LBRACE: TokenType(TOKEN_TYPE_LBRACE, '{'),
    TOKEN_TYPE_RBRACE: TokenType(TOKEN_TYPE_RBRACE, '}'),
    TOKEN_TYPE_FUNCTION: TokenType(TOKEN_TYPE_FUNCTION, 'FUNCTION'),
    TOKEN_TYPE_LET: TokenType(TOKEN_TYPE_LET, 'LET'),
})

KEYWORDS =  DictLikeStruct({
    KEYWORD_FUNCTION: TOKEN_TYPE_FUNCTION,
    KEYWORD_LET: TOKEN_TYPE_LET
})

def lookupIdent(ident):
    if ident in KEYWORDS:
        return TOKEN_TYPES[KEYWORDS[ident]]
    else:
        return TOKEN_TYPES.TOKEN_TYPE_IDENT
