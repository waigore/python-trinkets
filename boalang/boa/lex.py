from .token import TOKEN_TYPES, Token, lookupIdent, allOperatorTypes

class Lexer(object):
    def __init__(self, input):
        self.input = input
        self.reset()

    def reset(self):
        self.position = 0
        self.readPosition = 0
        self.ch = ''

        self.allOperatorTypes = allOperatorTypes()

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

    def peekChars(self, numChars):
        if self.readPosition >= len(self.input):
            return ''
        else:
            return self.input[self.readPosition:self.readPosition+numChars]

    def nextToken(self):
        tok = None

        self.skipWhitespace()

        ch = self.ch
        if self.ch == '/' and self.peekChars(1) == '/':
            literal = self.readComment()
            tok = Token(TOKEN_TYPES.TOKEN_TYPE_COMMENT, literal)
            return tok

        for operatorType in self.allOperatorTypes:
            opLen = len(operatorType.value)
            s = ch + self.peekChars(opLen-1)
            if s == operatorType.value:
                for i in range(opLen):
                    self.readChar()
                tok = Token(operatorType, s)
                return tok

        if ch == '':
            tok = Token(TOKEN_TYPES.TOKEN_TYPE_EOF, ch)
            self.readChar()
            return tok
        elif self.isIdentifierChar(self.ch):
            literal = self.readIdentifier()
            tokType = lookupIdent(literal)
            tok = Token(tokType, literal)
            return tok
        elif self.isDigit(self.ch):
            literal = self.readNumber()
            tok = Token(TOKEN_TYPES.TOKEN_TYPE_INT, literal)
            return tok
        elif self.ch == '"':
            literal = self.readString('"')
            tok = Token(TOKEN_TYPES.TOKEN_TYPE_STR, literal)
            return tok
        elif self.ch == "'":
            literal = self.readString("'")
            tok = Token(TOKEN_TYPES.TOKEN_TYPE_STR, literal)
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

    def readString(self, quoteChar):
        pos = self.position + 1
        while True:
            self.readChar()
            if self.ch == quoteChar or self.ch == '':
                self.readChar()
                break
        return self.input[pos:self.position-1]

    def readIdentifier(self):
        pos = self.position
        while self.isIdentifierChar(self.ch) or self.isDigit(self.ch):
            self.readChar()

        return self.input[pos:self.position]

    def readComment(self):
        pos = self.position
        while self.ch != '\n':
            if self.ch == '':
                break
            self.readChar()
        return self.input[pos:self.position]

    def skipWhitespace(self):
        while self.ch.isspace():
            self.readChar()
