
from .token import TOKEN_TYPES

NODE_TYPE_PROGRAM = "PROGRAM"
NODE_TYPE_STATEMENT = "STATEMENT"
NODE_TYPE_EXPRESSION = "EXPRESSION"

STATEMENT_TYPE_LET = "LET_STATEMENT"
STATEMENT_TYPE_RETURN = "RETURN_STATEMENT"
STATEMENT_TYPE_EXPRESSION = "EXPRESSION_STATEMENT"
STATEMENT_TYPE_BLOCK = "BLOCK_STATEMENT"

EXPRESSION_TYPE_IDENT = "IDENT_EXPRESSION"
EXPRESSION_TYPE_INT_LIT = "INT_LIT_EXPRESSION"
EXPRESSION_TYPE_FUNC_LIT = "FUNC_LIT_EXPRESSION"
EXPRESSION_TYPE_BOOLEAN = "BOOLEAN_EXPRESSION"
EXPRESSION_TYPE_PREFIX = "PREFIX_EXPRESSION"
EXPRESSION_TYPE_INFIX = "INFIX_EXPRESSION"
EXPRESSION_TYPE_IF = "IF_EXPRESSION"
EXPRESSION_TYPE_CALL = "CALL_EXPRESSION"

class Node(object):
    def __init__(self, token, typ):
        self.token = token
        self.nodeType = typ

    @property
    def tokenLiteral(self):
        return self.token.literal

    def __repr__(self):
        return '[Node type=%s t=%s]' % (self.nodeType)

class Statement(Node):
    def __init__(self, statementType, token, value):
        super(Statement, self).__init__(token, NODE_TYPE_STATEMENT)
        self.statementType = statementType
        self.value = value #Expression

    def __repr__(self):
        return '[%s t=%s v=%s]' % (self.statementType, self.token, self.value)

class Expression(Node):
    def __init__(self, expressionType, token):
        super(Expression, self).__init__(token, NODE_TYPE_EXPRESSION)
        self.expressionType = expressionType

class LetStatement(Statement):
    def __init__(self, token, identifier, value):
        super(LetStatement, self).__init__(STATEMENT_TYPE_LET, token, value)
        self.identifier = identifier

    def __repr__(self):
        return 'let %s = %s;' % (self.identifier.value, self.value)

class ReturnStatement(Statement):
    def __init__(self, token, value):
        super(ReturnStatement, self).__init__(STATEMENT_TYPE_RETURN, token, value)

    def __repr__(self):
        return 'return %s;' % (self.value)

class ExpressionStatement(Statement):
    def __init__(self, token, expr):
        super(ExpressionStatement, self).__init__(STATEMENT_TYPE_EXPRESSION, token, expr)

    @property
    def expression(self):
        return self.value

    def __repr__(self):
        return str(self.expression)

class BlockStatement(Statement):
    def __init__(self, token, statements):
        super(BlockStatement, self).__init__(STATEMENT_TYPE_BLOCK, token, statements)

    @property
    def statements(self):
        return self.value

    def __repr__(self):
        return '{%s}' % ' '.join([str(s) for s in self.statements])

class Identifier(Expression):
    def __init__(self, token, value=None):
        super(Identifier, self).__init__(EXPRESSION_TYPE_IDENT, token)
        self.value = value if value is not None else token.literal

    def __repr__(self):
        return str(self.value)

class Boolean(Expression):
    def __init__(self, token, value):
        super(Boolean, self).__init__(EXPRESSION_TYPE_BOOLEAN, token)
        self.value = value

    def __repr__(self):
        return str(self.value)

class IntegerLiteral(Expression):
    def __init__(self, token, value):
        super(IntegerLiteral, self).__init__(EXPRESSION_TYPE_INT_LIT, token)
        self.value = value

    def __repr__(self):
        return str(self.value)

class FunctionLiteral(Expression):
    def __init__(self, token, parameters, body):
        super(FunctionLiteral, self).__init__(EXPRESSION_TYPE_FUNC_LIT, token)
        self.parameters = parameters #list of identifiers
        self.body = body #BlockStatement

    def __repr__(self):
        return 'fn (%s) %s' % (','.join([str(p) for p in self.parameters]), self.body)

class PrefixExpression(Expression):
    def __init__(self, token, right):
        super(PrefixExpression, self).__init__(EXPRESSION_TYPE_PREFIX, token)
        self.operator = token.literal
        self.right = right

    def __repr__(self):
        isKeyword = self.token.tokenType.isKeyword
        return '(%s%s%s)' %(self.operator, ' ' if isKeyword else '', self.right)

class InfixExpression(Expression):
    def __init__(self, token, left, right):
        super(InfixExpression, self).__init__(EXPRESSION_TYPE_INFIX, token)
        self.operator = token.literal
        self.left = left
        self.right = right

    def __repr__(self):
        return '(%s %s %s)' % (self.left, self.operator, self.right)

class IfExpression(Expression):
    def __init__(self, token, condition, consequence, alternative):
        super(IfExpression, self).__init__(EXPRESSION_TYPE_IF, token)
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    def __repr__(self):
        alt = (' else %s' % self.alternative) if self.alternative else ''
        return ('if (%s) %s%s' % (self.condition, self.consequence, alt))

class CallExpression(Expression):
    def __init__(self, token, function, arguments):
        super(CallExpression, self).__init__(EXPRESSION_TYPE_CALL, token)
        self.function = function #identifier or function literal
        self.arguments = arguments #Expression list

    def __repr__(self):
        return '%s(%s)' % (self.function, ','.join([str(arg) for arg in self.arguments]))

class Program(Node):
    def __init__(self):
        super(Program, self).__init__(None, NODE_TYPE_PROGRAM)
        self.statements = []

    def addStatement(self, s):
        self.statements.append(s)

    @property
    def tokenLiteral(self):
        if not self.statements:
            return ''
        return self.statements[0].tokenLiteral

    def __repr__(self):
        return ''.join([str(statement) for statement in self.statements])
