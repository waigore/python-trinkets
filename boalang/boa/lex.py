from .token import TOKEN_TYPES, Token, lookupIdent

class Lexer(object):
    def __init__(self, input):
        self.input = input
        self.reset()

    def reset(self):
        self.position = 0
        self.readPosition = 0
        self.ch = ''

        self.readChar()

    def lex(self):
        tok = None
        eof = False
        tokens = []
        while True:
            tok = self.nextToken()
            if tok.tokenType == TOKEN_TYPES.TOKEN_TYPE_EOF:
                eof = True
            tokens.append(tok)
            if eof:
                break
        return tokens

    def readChar(self):
        if self.readPosition >= len(self.input):
            self.ch = ''
        else:
            self.ch = self.input[self.readPosition]
        self.position = self.readPosition
        self.readPosition += 1

    def nextToken(self):
        tok = None

        self.skipWhitespace()

        ch = self.ch
        if ch == TOKEN_TYPES.TOKEN_TYPE_ASSIGN.value:
            tok = Token(TOKEN_TYPES.TOKEN_TYPE_ASSIGN, ch)
        elif ch == TOKEN_TYPES.TOKEN_TYPE_SEMICOLON.value:
            tok = Token(TOKEN_TYPES.TOKEN_TYPE_SEMICOLON, ch)
        elif ch == TOKEN_TYPES.TOKEN_TYPE_LPAREN.value:
            tok = Token(TOKEN_TYPES.TOKEN_TYPE_LPAREN, ch)
        elif ch == TOKEN_TYPES.TOKEN_TYPE_RPAREN.value:
            tok = Token(TOKEN_TYPES.TOKEN_TYPE_RPAREN, ch)
        elif ch == TOKEN_TYPES.TOKEN_TYPE_COMMA.value:
            tok = Token(TOKEN_TYPES.TOKEN_TYPE_COMMA, ch)
        elif ch == TOKEN_TYPES.TOKEN_TYPE_PLUS.value:
            tok = Token(TOKEN_TYPES.TOKEN_TYPE_PLUS, ch)
        elif ch == TOKEN_TYPES.TOKEN_TYPE_LBRACE.value:
            tok = Token(TOKEN_TYPES.TOKEN_TYPE_LBRACE, ch)
        elif ch == TOKEN_TYPES.TOKEN_TYPE_RBRACE.value:
            tok = Token(TOKEN_TYPES.TOKEN_TYPE_RBRACE, ch)
        elif ch == '':
            tok = Token(TOKEN_TYPES.TOKEN_TYPE_EOF, ch)
        else:
            if self.isIdentifierChar(self.ch):
                literal = self.readIdentifier()
                tokType = lookupIdent(literal)
                tok = Token(tokType, literal)
                return tok
            elif self.isDigit(self.ch):
                literal = self.readNumber()
                tok = Token(TOKEN_TYPES.TOKEN_TYPE_INT, literal)
                return tok
            else:
                tok = Token(TOKEN_TYPES.TOKEN_TYPE_ILLEGAL, ch)

        self.readChar()

        return tok

    def isIdentifierChar(self, c):
        return c.isalpha() or c == '_'

    def isDigit(self, c):
        return c.isdigit()

    def readNumber(self):
        pos = self.position
        while self.isDigit(self.ch):
            self.readChar()

        return self.input[pos:self.position]

    def readIdentifier(self):
        pos = self.position
        while self.isIdentifierChar(self.ch):
            self.readChar()

        return self.input[pos:self.position]

    def skipWhitespace(self):
        while self.ch.isspace():
            self.readChar()
