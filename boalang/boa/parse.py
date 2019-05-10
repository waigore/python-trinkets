
from .lex import Lexer
from .ast import *
from .token import TOKEN_TYPES
from .util import DictLikeStruct

LOWEST = 1
EQUALS = 2
LESSGREATER = 3
SUM = 4
PRODUCT = 5
PREFIX = 6
CALL = 7

PRECEDENCE_LIST = [
    LOWEST, EQUALS, LESSGREATER, SUM, PRODUCT, PREFIX, CALL
]

PRECEDENCE_MAP = DictLikeStruct({
    TOKEN_TYPES.TOKEN_TYPE_EQ: EQUALS,
    TOKEN_TYPES.TOKEN_TYPE_NEQ: EQUALS,
    TOKEN_TYPES.TOKEN_TYPE_LT: LESSGREATER,
    TOKEN_TYPES.TOKEN_TYPE_GT: LESSGREATER,
    TOKEN_TYPES.TOKEN_TYPE_LTEQ: LESSGREATER,
    TOKEN_TYPES.TOKEN_TYPE_GTEQ: LESSGREATER,
    TOKEN_TYPES.TOKEN_TYPE_PLUS: SUM,
    TOKEN_TYPES.TOKEN_TYPE_MINUS: SUM,
    TOKEN_TYPES.TOKEN_TYPE_SLASH: PRODUCT,
    TOKEN_TYPES.TOKEN_TYPE_ASTERISK: PRODUCT,
})

class ParserError(object):
    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return '[ParserError "%s"]' % self.msg

class Parser(object):
    def __init__(self, input):
        self.lexer = Lexer(input)
        self.prefixParseFns = {}
        self.infixParseFns = {}
        self.registerAllParseFns()

        self.reset()

    def reset(self):
        self.curToken = None
        self.peekToken = None
        self.errors = []

        self.nextToken()
        self.nextToken()

    def getPrefixParseFn(self, tokenType):
        return self.prefixParseFns[tokenType.name] if tokenType.name in self.prefixParseFns else None

    def getInfixParseFn(self, tokenType):
        return self.infixParseFns[tokenType.name] if tokenType.name in self.infixParseFns else None

    def registerAllParseFns(self):
        self.registerPrefix(TOKEN_TYPES.TOKEN_TYPE_IDENT, self.parseIdentifier)
        self.registerPrefix(TOKEN_TYPES.TOKEN_TYPE_INT, self.parseIntegerLiteral)
        self.registerPrefix(TOKEN_TYPES.TOKEN_TYPE_EXCLAMATION, self.parsePrefixExpression)
        self.registerPrefix(TOKEN_TYPES.TOKEN_TYPE_MINUS, self.parsePrefixExpression)
        self.registerInfix(TOKEN_TYPES.TOKEN_TYPE_PLUS, self.parseInfixExpression)
        self.registerInfix(TOKEN_TYPES.TOKEN_TYPE_MINUS, self.parseInfixExpression)
        self.registerInfix(TOKEN_TYPES.TOKEN_TYPE_ASTERISK, self.parseInfixExpression)
        self.registerInfix(TOKEN_TYPES.TOKEN_TYPE_SLASH, self.parseInfixExpression)
        self.registerInfix(TOKEN_TYPES.TOKEN_TYPE_EQ, self.parseInfixExpression)
        self.registerInfix(TOKEN_TYPES.TOKEN_TYPE_NEQ, self.parseInfixExpression)
        self.registerInfix(TOKEN_TYPES.TOKEN_TYPE_LT, self.parseInfixExpression)
        self.registerInfix(TOKEN_TYPES.TOKEN_TYPE_GT, self.parseInfixExpression)
        self.registerInfix(TOKEN_TYPES.TOKEN_TYPE_LTEQ, self.parseInfixExpression)
        self.registerInfix(TOKEN_TYPES.TOKEN_TYPE_GTEQ, self.parseInfixExpression)

    def registerPrefix(self, tokenType, fn):
        self.prefixParseFns[tokenType.name] = fn

    def registerInfix(self, tokenType, fn):
        self.infixParseFns[tokenType.name] = fn

    def curTokenIs(self, tokenType):
        return self.curToken.tokenType == tokenType

    def peekTokenIs(self, tokenType):
        return self.peekToken.tokenType == tokenType

    def peekPrecedence(self):
        if self.peekToken.tokenType in PRECEDENCE_MAP:
            return PRECEDENCE_MAP[self.peekToken.tokenType]
        return LOWEST

    def curPrecedence(self):
        if self.curToken.tokenType in PRECEDENCE_MAP:
            return PRECEDENCE_MAP[self.curToken.tokenType]
        return LOWEST

    def expectPeek(self, tokenType):
        if self.peekTokenIs(tokenType):
            self.nextToken()
            return True
        else:
            self.peekError(tokenType)
            return False

    def peekError(self, tokenType):
        msg = "Expected next token to be %s but got %s instead" % (tokenType, self.peekToken.tokenType)
        self.errors.append(ParserError(msg))

    def noPrefixParseFnError(self, tokenType):
        msg = 'No prefix parse function for %s found' % tokenType
        self.errors.append(ParserError(msg))

    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.nextToken()

    def parseProgram(self):
        program = Program()

        while True:
            if self.curToken.tokenType == TOKEN_TYPES.TOKEN_TYPE_EOF:
                break
            statement = self.parseStatement()
            if statement is not None:
                program.addStatement(statement)

            self.nextToken()

        return program

    def parseStatement(self):
        if self.curToken.tokenType == TOKEN_TYPES.TOKEN_TYPE_LET:
            return self.parseLetStatement()
        elif self.curToken.tokenType == TOKEN_TYPES.TOKEN_TYPE_RETURN:
            return self.parseReturnStatement()
        else:
            return self.parseExpressionStatement()

    def parseLetStatement(self):
        letToken = self.curToken

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_IDENT):
            return None

        ident = Identifier(self.curToken)

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_ASSIGN):
            return None

        self.nextToken()

        value = self.parseExpression(LOWEST)
        statement = LetStatement(letToken, ident, value)

        if self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_SEMICOLON):
            self.nextToken()

        return statement

    def parseReturnStatement(self):
        returnToken = self.curToken

        self.nextToken()

        returnValue = self.parseExpression(LOWEST)
        statement = ReturnStatement(returnToken, returnValue)

        if self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_SEMICOLON):
            self.nextToken()

        return statement

    def parseExpressionStatement(self):
        exprToken = self.curToken
        expr = self.parseExpression(LOWEST)
        statement = ExpressionStatement(exprToken, expr)

        if self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_SEMICOLON):
            self.nextToken()

        return statement

    def parseExpression(self, precedence):
        prefix = self.getPrefixParseFn(self.curToken.tokenType)
        if prefix is None:
            self.noPrefixParseFnError(self.curToken.tokenType)
            return None

        leftExp = prefix()

        while not self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_SEMICOLON) \
                and precedence < self.peekPrecedence():
            infix = self.getInfixParseFn(self.peekToken.tokenType)
            if infix is None:
                return leftExp

            self.nextToken()

            leftExp = infix(leftExp)

        return leftExp

    def parsePrefixExpression(self):
        exprToken = self.curToken

        self.nextToken()

        right = self.parseExpression(PREFIX)
        expr = PrefixExpression(exprToken, right)

        return expr

    def parseInfixExpression(self, left):
        exprToken = self.curToken

        precedence = self.curPrecedence()
        self.nextToken()
        right = self.parseExpression(precedence)
        expr = InfixExpression(exprToken, left, right)
        return expr

    def parseIdentifier(self):
        ident = Identifier(self.curToken)
        return ident

    def parseIntegerLiteral(self):
        try:
            value = int(self.curToken.literal)
        except:
            msg = "Could not parse %s as integer" % (self.curToken.literal)
            self.errors.append(ParserError(msg))
            return None

        lit = IntegerLiteral(self.curToken, value)
        return lit