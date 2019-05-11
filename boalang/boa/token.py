
from .util import DictLikeStruct

TOKEN_TYPE_ILLEGAL = 'TOKEN_TYPE_ILLEGAL'
TOKEN_TYPE_EOF = 'TOKEN_TYPE_EOF'
TOKEN_TYPE_IDENT = 'TOKEN_TYPE_IDENT'
TOKEN_TYPE_INT = 'TOKEN_TYPE_INT'
TOKEN_TYPE_STR = 'TOKEN_TYPE_STR'
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
TOKEN_TYPE_EXCLAMATION = 'TOKEN_TYPE_EXCLAMATION'
TOKEN_TYPE_PERIOD = 'TOKEN_TYPE_PERIOD'
TOKEN_TYPE_SEMICOLON = 'TOKEN_TYPE_SEMICOLON'
TOKEN_TYPE_LPAREN = 'TOKEN_TYPE_LPAREN'
TOKEN_TYPE_RPAREN = 'TOKEN_TYPE_RPAREN'
TOKEN_TYPE_LBRACE = 'TOKEN_TYPE_LBRACE'
TOKEN_TYPE_RBRACE = 'TOKEN_TYPE_RBRACE'
TOKEN_TYPE_FUNCTION = 'TOKEN_TYPE_FUNCTION'
TOKEN_TYPE_LET = 'TOKEN_TYPE_LET'
TOKEN_TYPE_IF = 'TOKEN_TYPE_IF'
TOKEN_TYPE_ELSE = 'TOKEN_TYPE_ELSE'
TOKEN_TYPE_RETURN = 'TOKEN_TYPE_RETURN'
TOKEN_TYPE_TRUE = 'TOKEN_TYPE_TRUE'
TOKEN_TYPE_FALSE = 'TOKEN_TYPE_FALSE'
TOKEN_TYPE_NOT = 'TOKEN_TYPE_NOT'
TOKEN_TYPE_IN = 'TOKEN_TYPE_IN'
TOKEN_TYPE_AND = 'TOKEN_TYPE_AND'
TOKEN_TYPE_OR = 'TOKEN_TYPE_OR'

KEYWORD_FN = 'fn'
KEYWORD_FUNCTION = 'function'
KEYWORD_LET = 'let'
KEYWORD_IF = 'if'
KEYWORD_ELSE = 'else'
KEYWORD_RETURN = 'return'
KEYWORD_TRUE = 'true'
KEYWORD_FALSE = 'false'
KEYWORD_NOT = 'not'
KEYWORD_IN = 'in'
KEYWORD_AND = 'and'
KEYWORD_OR = 'or'

class TokenType(object):
    def __init__(self, name, value, isOperator=True, isKeyword=False):
        self.name = name
        self.value = value
        self.isOperator = isOperator
        self.isKeyword = isKeyword

    def __repr__(self):
        return '[%s "%s"]' % (self.name, self.value)

class Token(object):
    def __init__(self, tokenType, literal):
        self.tokenType = tokenType
        self.literal = literal

    def __repr__(self):
        return '[%s "%s"]' % (self.tokenType, self.literal)

TOKEN_TYPES = DictLikeStruct({
    TOKEN_TYPE_ILLEGAL: TokenType(TOKEN_TYPE_ILLEGAL, 'ILLEGAL', isOperator=False),
    TOKEN_TYPE_EOF: TokenType(TOKEN_TYPE_EOF, 'EOF', isOperator=False),
    TOKEN_TYPE_IDENT: TokenType(TOKEN_TYPE_IDENT, 'IDENT', isOperator=False),
    TOKEN_TYPE_INT: TokenType(TOKEN_TYPE_INT, 'INT', isOperator=False),
    TOKEN_TYPE_STR: TokenType(TOKEN_TYPE_STR, 'STR', isOperator=False),
    TOKEN_TYPE_FUNCTION: TokenType(TOKEN_TYPE_FUNCTION, KEYWORD_FN, isOperator=False),
    TOKEN_TYPE_LET: TokenType(TOKEN_TYPE_LET, KEYWORD_LET, isOperator=False, isKeyword=True),
    TOKEN_TYPE_IF: TokenType(TOKEN_TYPE_IF, KEYWORD_IF, isOperator=False, isKeyword=True),
    TOKEN_TYPE_ELSE: TokenType(TOKEN_TYPE_ELSE, KEYWORD_ELSE, isOperator=False, isKeyword=True),
    TOKEN_TYPE_RETURN: TokenType(TOKEN_TYPE_RETURN, KEYWORD_RETURN, isOperator=False, isKeyword=True),
    TOKEN_TYPE_TRUE: TokenType(TOKEN_TYPE_TRUE, KEYWORD_TRUE, isOperator=False, isKeyword=True),
    TOKEN_TYPE_FALSE: TokenType(TOKEN_TYPE_FALSE, KEYWORD_FALSE, isOperator=False, isKeyword=True),
    TOKEN_TYPE_NOT: TokenType(TOKEN_TYPE_NOT, KEYWORD_NOT, isOperator=False, isKeyword=True),
    TOKEN_TYPE_IN: TokenType(TOKEN_TYPE_IN, KEYWORD_IN, isOperator=False, isKeyword=True),
    TOKEN_TYPE_AND: TokenType(TOKEN_TYPE_AND, KEYWORD_AND, isOperator=False, isKeyword=True),
    TOKEN_TYPE_OR: TokenType(TOKEN_TYPE_OR, KEYWORD_OR, isOperator=False, isKeyword=True),
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
    TOKEN_TYPE_EXCLAMATION: TokenType(TOKEN_TYPE_EXCLAMATION, '!'),
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
    KEYWORD_IF: TOKEN_TYPE_IF,
    KEYWORD_ELSE: TOKEN_TYPE_ELSE,
    KEYWORD_RETURN: TOKEN_TYPE_RETURN,
    KEYWORD_TRUE: TOKEN_TYPE_TRUE,
    KEYWORD_FALSE: TOKEN_TYPE_FALSE,
    KEYWORD_NOT: TOKEN_TYPE_NOT,
    KEYWORD_IN: TOKEN_TYPE_IN,
    KEYWORD_AND: TOKEN_TYPE_AND,
    KEYWORD_OR: TOKEN_TYPE_OR,
})

def allOperatorTypes():
    opTypes = filter(lambda t: t.isOperator, TOKEN_TYPES.toDict().values())
    return sorted(opTypes, key=lambda t: len(t.value), reverse=True)

def lookupIdent(ident):
    if ident in KEYWORDS:
        return TOKEN_TYPES[KEYWORDS[ident]]
    else:
        return TOKEN_TYPES.TOKEN_TYPE_IDENT
