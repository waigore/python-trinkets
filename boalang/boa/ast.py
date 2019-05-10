
from .token import TOKEN_TYPES

NODE_TYPE_STATEMENT = "STATEMENT"
NODE_TYPE_EXPRESSION = "EXPRESSION"
NODE_TYPE_IDENTIFIER = "IDENTIFIER"
NODE_TYPE_INT_LITERAL = "INT_LITERAL"

STATEMENT_TYPE_LET = "LET_STATEMENT"
STATEMENT_TYPE_RETURN = "RETURN_STATEMENT"
STATEMENT_TYPE_EXPRESSION = "EXPRESSION_STATEMENT"

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
    def __init__(self, token):
        super(Expression, self).__init__(token, NODE_TYPE_EXPRESSION)

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

class Identifier(Node):
    def __init__(self, token, value=None):
        super(Identifier, self).__init__(token, NODE_TYPE_IDENTIFIER)
        self.value = value if value is not None else token.literal

    def __repr__(self):
        return str(self.value)

class IntegerLiteral(Node):
    def __init__(self, token, value):
        super(IntegerLiteral, self).__init__(token, NODE_TYPE_INT_LITERAL)
        self.value = value

    def __repr__(self):
        return str(self.value)

class PrefixExpression(Expression):
    def __init__(self, token, right):
        super(PrefixExpression, self).__init__(token)
        self.operator = token.literal
        self.right = right

    def __repr__(self):
        return '(%s%s)' %(self.operator, self.right)

class Program(object):
    def __init__(self):
        self.statements = []

    def addStatement(self, s):
        self.statements.append(s)

    @property
    def tokenLiteral(self):
        if not self.statements:
            return ''
        return self.statements[0].tokenLiteral

    def __repr__(self):
        return ''.join(self.statements)
