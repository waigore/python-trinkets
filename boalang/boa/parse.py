
from .lex import Lexer
from .ast import *
from .token import TOKEN_TYPES
from .util import DictLikeStruct

LOWEST = 1
BOOL = 2
EQUALS = 3
LESSGREATER = 4
SUM = 5
PRODUCT = 6
PREFIX = 7
CALL = 8
INDEX = 9

PRECEDENCE_LIST = [
    LOWEST, BOOL, EQUALS, LESSGREATER, SUM, PRODUCT, PREFIX, CALL, INDEX
]

PRECEDENCE_MAP = DictLikeStruct({
    TOKEN_TYPES.TOKEN_TYPE_AND: BOOL,
    TOKEN_TYPES.TOKEN_TYPE_OR: BOOL,
    TOKEN_TYPES.TOKEN_TYPE_EQ: EQUALS,
    TOKEN_TYPES.TOKEN_TYPE_NEQ: EQUALS,
    TOKEN_TYPES.TOKEN_TYPE_IN: LESSGREATER,
    TOKEN_TYPES.TOKEN_TYPE_NOTIN: LESSGREATER,
    TOKEN_TYPES.TOKEN_TYPE_LT: LESSGREATER,
    TOKEN_TYPES.TOKEN_TYPE_GT: LESSGREATER,
    TOKEN_TYPES.TOKEN_TYPE_LTEQ: LESSGREATER,
    TOKEN_TYPES.TOKEN_TYPE_GTEQ: LESSGREATER,
    TOKEN_TYPES.TOKEN_TYPE_PLUS: SUM,
    TOKEN_TYPES.TOKEN_TYPE_MINUS: SUM,
    TOKEN_TYPES.TOKEN_TYPE_SLASH: PRODUCT,
    TOKEN_TYPES.TOKEN_TYPE_ASTERISK: PRODUCT,
    TOKEN_TYPES.TOKEN_TYPE_LPAREN: CALL,
    TOKEN_TYPES.TOKEN_TYPE_PERIOD: INDEX,
    TOKEN_TYPES.TOKEN_TYPE_LBRACKET: INDEX,
})

class ParserError(object):
    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return '[ParserError "%s"]' % self.msg

class ParserSnapshot(object):
    def __init__(self, parser):
        self.parser = parser

        self.curToken = parser.curToken
        self.peekToken = parser.peekToken
        self.readPosition = parser.lexer.readPosition
        self.position = parser.lexer.position
        self.ch = parser.lexer.ch
        self.errors = list(parser.errors)

    def restore(self):
        self.parser.curToken = self.curToken
        self.parser.peekToken = self.peekToken
        self.parser.lexer.readPosition = self.readPosition
        self.parser.lexer.position = self.position
        self.parser.lexer.ch = self.ch
        self.parser.errors = self.errors

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
        self.registerPrefix(TOKEN_TYPES.TOKEN_TYPE_THIS, self.parseInstanceReference)
        self.registerPrefix(TOKEN_TYPES.TOKEN_TYPE_INT, self.parseIntegerLiteral)
        self.registerPrefix(TOKEN_TYPES.TOKEN_TYPE_STR, self.parseStringLiteral)
        self.registerPrefix(TOKEN_TYPES.TOKEN_TYPE_NULL, self.parseNullLiteral)
        self.registerPrefix(TOKEN_TYPES.TOKEN_TYPE_LBRACKET, self.parseArrayLiteral)
        self.registerPrefix(TOKEN_TYPES.TOKEN_TYPE_LBRACE, self.parseHashLiteral)
        self.registerPrefix(TOKEN_TYPES.TOKEN_TYPE_EXCLAMATION, self.parsePrefixExpression)
        self.registerPrefix(TOKEN_TYPES.TOKEN_TYPE_MINUS, self.parsePrefixExpression)
        self.registerPrefix(TOKEN_TYPES.TOKEN_TYPE_NOT, self.parsePrefixExpression)
        self.registerPrefix(TOKEN_TYPES.TOKEN_TYPE_TRUE, self.parseBoolean)
        self.registerPrefix(TOKEN_TYPES.TOKEN_TYPE_FALSE, self.parseBoolean)
        self.registerPrefix(TOKEN_TYPES.TOKEN_TYPE_LPAREN, self.parseGroupedExpression)
        self.registerPrefix(TOKEN_TYPES.TOKEN_TYPE_IF, self.parseIfExpression)
        self.registerPrefix(TOKEN_TYPES.TOKEN_TYPE_FUNCTION, self.parseFunctionLiteral)
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
        self.registerInfix(TOKEN_TYPES.TOKEN_TYPE_IN, self.parseInfixExpression)
        self.registerInfix(TOKEN_TYPES.TOKEN_TYPE_NOTIN, self.parseInfixExpression)
        self.registerInfix(TOKEN_TYPES.TOKEN_TYPE_AND, self.parseInfixExpression)
        self.registerInfix(TOKEN_TYPES.TOKEN_TYPE_OR, self.parseInfixExpression)
        self.registerInfix(TOKEN_TYPES.TOKEN_TYPE_PERIOD, self.parseGetExpression)
        self.registerInfix(TOKEN_TYPES.TOKEN_TYPE_LPAREN, self.parseCallExpression)
        self.registerInfix(TOKEN_TYPES.TOKEN_TYPE_LBRACKET, self.parseIndexExpression)

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

    def invalidAssignmentTargetError(self, expr):
        msg = 'Expression cannot be used as target of assignment: %s' % expr
        self.errors.append(ParserError(msg))

    def invalidMethodNameError(self, name):
        msg = 'Expected identifier as class method name: %s' % name
        self.errors.append(ParserError(msg))

    def nestedClassDefError(self, name):
        msg = 'Class cannot be defined in nested scope: %s' % name
        self.errors.append(ParserError(msg))

    def noPrefixParseFnError(self, tokenType):
        msg = 'Unparseable token %s found' % tokenType
        self.errors.append(ParserError(msg))

    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.nextToken()
        while self.curToken is not None and self.curTokenIs(TOKEN_TYPES.TOKEN_TYPE_COMMENT):
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
        snapshot = ParserSnapshot(self)
        if self.curTokenIs(TOKEN_TYPES.TOKEN_TYPE_LET):
            return self.parseLetStatement()
        elif self.curTokenIs(TOKEN_TYPES.TOKEN_TYPE_RETURN):
            return self.parseReturnStatement()
        elif self.curTokenIs(TOKEN_TYPES.TOKEN_TYPE_WHILE):
            return self.parseWhileStatement()
        elif self.curTokenIs(TOKEN_TYPES.TOKEN_TYPE_FOR):
            return self.parseForStatement()
        elif self.curTokenIs(TOKEN_TYPES.TOKEN_TYPE_BREAK) or \
                self.curTokenIs(TOKEN_TYPES.TOKEN_TYPE_CONTINUE):
            return self.parseLoopControlStatement()
        elif self.curTokenIs(TOKEN_TYPES.TOKEN_TYPE_CLASS):
            return self.parseClassStatement()
        #elif self.curTokenIs(TOKEN_TYPES.TOKEN_TYPE_IDENT) and \
        #        (self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_ASSIGN) or \
        #        self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_LBRACKET)):
        else:
            assignStatement = self.parseAssignStatement()
            if assignStatement is None and len(self.errors) > len(snapshot.errors):
                snapshot.restore()
                return self.parseExpressionStatement()
            else:
                return assignStatement
        #else:
        #    return self.parseExpressionStatement()

    def parseAssignStatement(self):
        assignTarget = self.parseExpression(LOWEST)
        if assignTarget is None:
            return None
        if assignTarget.expressionType not in [EXPRESSION_TYPE_IDENT, EXPRESSION_TYPE_GET, EXPRESSION_TYPE_INDEX]:
            self.invalidAssignmentTargetError(assignTarget)
            return None

        #identToken = self.curToken
        #ident = Identifier(identToken)

        #if self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_LBRACKET):
        #    self.nextToken()
        #    ident = self.parseIndexExpression(ident)

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_ASSIGN):
            return None

        self.nextToken()

        value = self.parseExpression(LOWEST)
        if value is None:
            return None
        statement = AssignStatement('=', assignTarget, value)

        if self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_SEMICOLON):
            self.nextToken()

        return statement

    def parseLetStatement(self):
        letToken = self.curToken

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_IDENT):
            return None

        ident = Identifier(self.curToken)

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_ASSIGN):
            return None

        self.nextToken()

        value = self.parseExpression(LOWEST)
        if value.expressionType == EXPRESSION_TYPE_FUNC_LIT:
            value.name = ident.value
        statement = LetStatement(letToken, ident, value)

        if self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_SEMICOLON):
            self.nextToken()

        return statement

    def parseReturnStatement(self):
        returnToken = self.curToken

        if self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_SEMICOLON):
            self.nextToken()
            return ReturnStatement(returnToken, None)

        self.nextToken()

        returnValue = self.parseExpression(LOWEST)
        statement = ReturnStatement(returnToken, returnValue)

        if self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_SEMICOLON):
            self.nextToken()

        return statement

    def parseWhileStatement(self):
        whileToken = self.curToken

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_LPAREN):
            return None

        self.nextToken()
        condition = self.parseExpression(LOWEST)

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_RPAREN):
            return None

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_LBRACE):
            return None

        blockStatement = self.parseBlockStatement()

        if self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_SEMICOLON):
            self.nextToken()

        whileStatement = WhileStatement(whileToken, condition, blockStatement)
        return whileStatement

    def parseForStatement(self):
        forToken = self.curToken

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_LPAREN):
            return None

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_IDENT):
            return None

        ident = Identifier(self.curToken)

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_IN):
            return None
        self.nextToken()

        iterable = self.parseExpression(LOWEST)

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_RPAREN):
            return None

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_LBRACE):
            return None

        blockStatement = self.parseBlockStatement()

        if self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_SEMICOLON):
            self.nextToken()

        forStatement = ForStatement(forToken, ident, iterable, blockStatement)
        return forStatement

    def parseLoopControlStatement(self):
        curToken = self.curToken
        if self.curTokenIs(TOKEN_TYPES.TOKEN_TYPE_CONTINUE):
            statement = ContinueStatement(curToken)
        else:
            statement = BreakStatement(curToken)

        if self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_SEMICOLON):
            self.nextToken()

        return statement

    def parseClassStatement(self):
        classToken = self.curToken

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_IDENT):
            return None

        className = self.curToken.literal

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_LBRACE):
            return None

        constructorStatement, methodStatements = self.parseClassDefinition(className)

        if self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_SEMICOLON):
            self.nextToken()

        classStatement = ClassStatement(classToken, className, constructorStatement, methodStatements)
        return classStatement

    def parseClassDefinition(self, className):
        lbrace = self.curToken
        statements = []

        self.nextToken()
        constructorStatement = None
        while not self.curTokenIs(TOKEN_TYPES.TOKEN_TYPE_RBRACE) and \
                not self.curTokenIs(TOKEN_TYPES.TOKEN_TYPE_EOF):
            statement = self.parseMethodStatement(className)
            if statement is not None:
                if statement.name == 'constructor':
                    constructorStatement = statement
                else:
                    statements.append(statement)
            self.nextToken()

        return constructorStatement, statements

    def parseMethodStatement(self, className):
        if not self.curTokenIs(TOKEN_TYPES.TOKEN_TYPE_IDENT):
            self.invalidMethodNameError(self.curToken)
            return None
        methodToken = self.curToken

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_LPAREN):
            return None

        parameters = self.parseFunctionParameters()

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_LBRACE):
            return None

        body = self.parseBlockStatement()

        if self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_SEMICOLON):
            self.nextToken()

        methodStatement = MethodStatement(methodToken, className, methodToken.literal, parameters, body)
        return methodStatement

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

    def parseGetExpression(self, obj):
        getToken = self.curToken

        self.nextToken()
        property = self.parseExpression(INDEX)
        expr = GetExpression(getToken, obj, property)
        return expr

    def parseCallExpression(self, function):
        callToken = self.curToken

        args = self.parseCallArguments()
        expr = CallExpression(callToken, function, args)
        return expr

    def parseCallArguments(self):
        return self.parseExpressionList(TOKEN_TYPES.TOKEN_TYPE_RPAREN)

    def parseIndexExpression(self, left):
        idxToken = self.curToken

        self.nextToken()
        idx = self.parseExpression(LOWEST)

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_RBRACKET):
            return None

        expr = IndexExpression(idxToken, left, idx)
        return expr

    def parseGroupedExpression(self):
        self.nextToken()
        expr = self.parseExpression(LOWEST)

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_RPAREN):
            return None

        return expr

    def parseIfExpression(self):
        conditionalBlocks = []
        alternative = None
        hasElse = False
        ifTok = self.curToken
        while True:
            if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_LPAREN):
                return None

            self.nextToken()
            condition = self.parseExpression(LOWEST)

            if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_RPAREN):
                return None

            if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_LBRACE):
                return None

            consequence = self.parseBlockStatement()

            conditionalBlocks.append((condition, consequence))

            if self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_ELIF):
                self.nextToken()
            elif self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_ELSE):
                self.nextToken()
                hasElse = True
                break
            else:
                break

        if hasElse:
            if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_LBRACE):
                return None

            alternative = self.parseBlockStatement()

        expr = IfExpression(ifTok, conditionalBlocks, alternative)
        return expr

    def parseBlockStatement(self):
        blockTok = self.curToken
        statements = []

        self.nextToken()
        while not self.curTokenIs(TOKEN_TYPES.TOKEN_TYPE_RBRACE) and \
                not self.curTokenIs(TOKEN_TYPES.TOKEN_TYPE_EOF):
            statement = self.parseStatement()
            if statement.statementType == STATEMENT_TYPE_CLASS:
                self.nestedClassDefError(statement.name)
                statement = None
            if statement is not None:
                statements.append(statement)
            self.nextToken()

        block = BlockStatement(blockTok, statements)
        return block

    def parseIdentifier(self):
        ident = Identifier(self.curToken)
        return ident

    def parseInstanceReference(self):
        this = InstanceReference(self.curToken)
        return this

    def parseBoolean(self):
        bool = Boolean(self.curToken, self.curTokenIs(TOKEN_TYPES.TOKEN_TYPE_TRUE))
        return bool

    def parseNullLiteral(self):
        null = NullLiteral(self.curToken)
        return null

    def parseIntegerLiteral(self):
        try:
            value = int(self.curToken.literal)
        except:
            msg = "Could not parse %s as integer" % (self.curToken.literal)
            self.errors.append(ParserError(msg))
            return None

        lit = IntegerLiteral(self.curToken, value)
        return lit

    def parseStringLiteral(self):
        lit = StringLiteral(self.curToken, self.curToken.literal)
        return lit

    def parseArrayLiteral(self):
        arrToken = self.curToken
        arrElements = self.parseExpressionList(TOKEN_TYPES.TOKEN_TYPE_RBRACKET)

        lit = ArrayLiteral(arrToken, arrElements)
        return lit

    def parseHashLiteral(self):
        hashToken = self.curToken
        pairs = []
        while not self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_RBRACE):
            self.nextToken()
            key = self.parseExpression(LOWEST)
            if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_COLON):
                return None
            self.nextToken()
            value = self.parseExpression(LOWEST)
            pairs.append((key, value))
            if not self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_RBRACE) and  \
                    not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_COMMA):
                return None

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_RBRACE):
            return None

        lit = HashLiteral(hashToken, pairs)
        return lit

    def parseExpressionList(self, endTokenType):
        l = []
        if self.peekTokenIs(endTokenType):
            self.nextToken()
            return l

        self.nextToken()
        l.append(self.parseExpression(LOWEST))

        while self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_COMMA):
            self.nextToken()
            self.nextToken()
            l.append(self.parseExpression(LOWEST))

        if not self.expectPeek(endTokenType):
            return None

        return l

    def parseFunctionLiteral(self):
        fnToken = self.curToken

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_LPAREN):
            return None

        parameters = self.parseFunctionParameters()

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_LBRACE):
            return None

        body = self.parseBlockStatement()

        lit = FunctionLiteral(self.curToken, parameters, body)
        return lit

    def parseFunctionParameters(self):
        identifiers = []

        if self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_RPAREN):
            self.nextToken()
            return identifiers

        self.nextToken()
        ident = Identifier(self.curToken)
        identifiers.append(ident)

        while self.peekTokenIs(TOKEN_TYPES.TOKEN_TYPE_COMMA):
            self.nextToken()
            self.nextToken()
            ident = Identifier(self.curToken)
            identifiers.append(ident)

        if not self.expectPeek(TOKEN_TYPES.TOKEN_TYPE_RPAREN):
            return None

        return identifiers
