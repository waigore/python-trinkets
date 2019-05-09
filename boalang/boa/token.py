
from .util import DictLikeStruct

TOKEN_TYPE_ILLEGAL = 'TOKEN_TYPE_ILLEGAL'
TOKEN_TYPE_EOF = 'TOKEN_TYPE_EOF'
TOKEN_TYPE_IDENT = 'TOKEN_TYPE_IDENT'
TOKEN_TYPE_INT = 'TOKEN_TYPE_INT'
TOKEN_TYPE_ASSIGN = 'TOKEN_TYPE_ASSIGN'
TOKEN_TYPE_EQ = 'TOKEN_TYPE_EQ'
TOKEN_TYPE_NEQ = 'TOKEN_TYPE_NEQ'
TOKEN_TYPE_GT = 'TOKEN_TYPE_GT'
TOKEN_TYPE_LT = 'TOKEN_TYPE_LT'
TOKEN_TYPE_GTEQ = 'TOKEN_TYPE_GTEQ'
TOKEN_TYPE_LTEQ = 'TOKEN_TYPE_LTEQ'
TOKEN_TYPE_PLUS = 'TOKEN_TYPE_PLUS'
TOKEN_TYPE_MINUS = 'TOKEN_TYPE_MINUS'
TOKEN_TYPE_ASTERISK = 'TOKEN_TYPE_ASTERISK'
TOKEN_TYPE_SLASH = 'TOKEN_TYPE_SLASH'
TOKEN_TYPE_COMMA = 'TOKEN_TYPE_COMMA'
TOKEN_TYPE_PERIOD = 'TOKEN_TYPE_PERIOD'
TOKEN_TYPE_SEMICOLON = 'TOKEN_TYPE_SEMICOLON'
TOKEN_TYPE_LPAREN = 'TOKEN_TYPE_LPAREN'
TOKEN_TYPE_RPAREN = 'TOKEN_TYPE_RPAREN'
TOKEN_TYPE_LBRACE = 'TOKEN_TYPE_LBRACE'
TOKEN_TYPE_RBRACE = 'TOKEN_TYPE_RBRACE'
TOKEN_TYPE_FUNCTION = 'TOKEN_TYPE_FUNCTION'
TOKEN_TYPE_LET = 'TOKEN_TYPE_LET'
TOKEN_TYPE_IF = 'TOKEN_TYPE_IF'

KEYWORD_FN = 'fn'
KEYWORD_FUNCTION = 'function'
KEYWORD_LET = 'let'
KEYWORD_IF = 'if'

class TokenType(object):
    def __init__(self, name, value, isLiteral=True):
        self.name = name
        self.value = value
        self.isLiteral = isLiteral

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value

    def __repr__(self):
        return '[%s "%s"]' % (self.name, self.value)

class Token(object):
    def __init__(self, tokenType, literal):
        self.tokenType = tokenType
        self.literal = literal

    def __repr__(self):
        return '[%s "%s"]' % (self.tokenType, self.literal)

TOKEN_TYPES = DictLikeStruct({
    TOKEN_TYPE_ILLEGAL: TokenType(TOKEN_TYPE_ILLEGAL, 'ILLEGAL', isLiteral=False),
    TOKEN_TYPE_EOF: TokenType(TOKEN_TYPE_EOF, 'EOF', isLiteral=False),
    TOKEN_TYPE_IDENT: TokenType(TOKEN_TYPE_IDENT, 'IDENT', isLiteral=False),
    TOKEN_TYPE_INT: TokenType(TOKEN_TYPE_INT, 'INT', isLiteral=False),
    TOKEN_TYPE_FUNCTION: TokenType(TOKEN_TYPE_FUNCTION, 'FUNCTION', isLiteral=False),
    TOKEN_TYPE_LET: TokenType(TOKEN_TYPE_LET, 'LET', isLiteral=False),
    TOKEN_TYPE_IF: TokenType(TOKEN_TYPE_IF, 'IF', isLiteral=False),
    TOKEN_TYPE_ASSIGN: TokenType(TOKEN_TYPE_ASSIGN, '='),
    TOKEN_TYPE_EQ: TokenType(TOKEN_TYPE_EQ, '=='),
    TOKEN_TYPE_NEQ: TokenType(TOKEN_TYPE_NEQ, '!='),
    TOKEN_TYPE_GT: TokenType(TOKEN_TYPE_GT, '>'),
    TOKEN_TYPE_LT: TokenType(TOKEN_TYPE_LT, '<'),
    TOKEN_TYPE_GTEQ: TokenType(TOKEN_TYPE_GTEQ, '>='),
    TOKEN_TYPE_LTEQ: TokenType(TOKEN_TYPE_LTEQ, '<='),
    TOKEN_TYPE_PLUS: TokenType(TOKEN_TYPE_PLUS, '+'),
    TOKEN_TYPE_MINUS: TokenType(TOKEN_TYPE_MINUS, '-'),
    TOKEN_TYPE_ASTERISK: TokenType(TOKEN_TYPE_ASTERISK, '*'),
    TOKEN_TYPE_SLASH : TokenType(TOKEN_TYPE_SLASH, '/'),
    TOKEN_TYPE_COMMA: TokenType(TOKEN_TYPE_COMMA, ','),
    TOKEN_TYPE_PERIOD: TokenType(TOKEN_TYPE_PERIOD, '.'),
    TOKEN_TYPE_SEMICOLON: TokenType(TOKEN_TYPE_SEMICOLON, ';'),
    TOKEN_TYPE_LPAREN: TokenType(TOKEN_TYPE_LPAREN, '('),
    TOKEN_TYPE_RPAREN: TokenType(TOKEN_TYPE_RPAREN, ')'),
    TOKEN_TYPE_LBRACE: TokenType(TOKEN_TYPE_LBRACE, '{'),
    TOKEN_TYPE_RBRACE: TokenType(TOKEN_TYPE_RBRACE, '}'),
})

KEYWORDS =  DictLikeStruct({
    KEYWORD_FN: TOKEN_TYPE_FUNCTION,
    KEYWORD_FUNCTION : TOKEN_TYPE_FUNCTION,
    KEYWORD_LET: TOKEN_TYPE_LET,
    KEYWORD_IF: TOKEN_TYPE_IF
})

def allOperatorTypes():
    literalTypes = filter(lambda t: t.isLiteral, TOKEN_TYPES.toDict().values())
    return sorted(literalTypes, key=lambda t: len(t.value), reverse=True)

def lookupIdent(ident):
    if ident in KEYWORDS:
        return TOKEN_TYPES[KEYWORDS[ident]]
    else:
        return TOKEN_TYPES.TOKEN_TYPE_IDENT
