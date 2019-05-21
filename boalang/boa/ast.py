
from .token import TOKEN_TYPES

NODE_TYPE_PROGRAM = "PROGRAM"
NODE_TYPE_STATEMENT = "STATEMENT"
NODE_TYPE_EXPRESSION = "EXPRESSION"

STATEMENT_TYPE_LET = "LET_STATEMENT"
STATEMENT_TYPE_ASSIGN = "ASSIGN_STATEMENT"
STATEMENT_TYPE_RETURN = "RETURN_STATEMENT"
STATEMENT_TYPE_EXPRESSION = "EXPRESSION_STATEMENT"
STATEMENT_TYPE_BLOCK = "BLOCK_STATEMENT"
STATEMENT_TYPE_WHILE = "WHILE_STATEMENT"
STATEMENT_TYPE_FOR = "FOR_STATEMENT"
STATEMENT_TYPE_BREAK = "BREAK_STATEMENT"
STATEMENT_TYPE_CONTINUE = "CONTINUE_STATEMENT"
STATEMENT_TYPE_CLASS = "CLASS_STATEMENT"
STATEMENT_TYPE_METHOD = "METHOD_STATEMENT"

EXPRESSION_TYPE_IDENT = "IDENT_EXPRESSION"
EXPRESSION_TYPE_INSTANCE_REF = "INSTANCE_REF_EXPRESSION"
EXPRESSION_TYPE_INT_LIT = "INT_LIT_EXPRESSION"
EXPRESSION_TYPE_FUNC_LIT = "FUNC_LIT_EXPRESSION"
EXPRESSION_TYPE_STR_LIT = "STR_LIT_EXPRESSION"
EXPRESSION_TYPE_NULL_LIT = "NULL_LIT_EXPRESSION"
EXPRESSION_TYPE_ARRAY_LIT = "ARRAY_LIT_EXPRESSION"
EXPRESSION_TYPE_HASH_LIT = "HASH_LIT_EXPRESSION"
EXPRESSION_TYPE_BOOLEAN = "BOOLEAN_EXPRESSION"
EXPRESSION_TYPE_PREFIX = "PREFIX_EXPRESSION"
EXPRESSION_TYPE_INFIX = "INFIX_EXPRESSION"
EXPRESSION_TYPE_INDEX = "INDEX_EXPRESSION"
EXPRESSION_TYPE_GET = "GET_EXPRESSION"
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

class AssignStatement(Statement):
    def __init__(self, token, identifier, value):
        super(AssignStatement, self).__init__(STATEMENT_TYPE_ASSIGN, token, value)
        self.identifier = identifier

    def __repr__(self):
        return '%s = %s;' % (self.identifier, self.value)

class ReturnStatement(Statement):
    def __init__(self, token, value):
        super(ReturnStatement, self).__init__(STATEMENT_TYPE_RETURN, token, value)

    def __repr__(self):
        return 'return %s;' % (self.value)

class BreakStatement(Statement):
    def __init__(self, token):
        super(BreakStatement, self).__init__(STATEMENT_TYPE_BREAK, token, None)

    def __repr__(self):
        return 'break;'

class ContinueStatement(Statement):
    def __init__(self, token):
        super(ContinueStatement, self).__init__(STATEMENT_TYPE_CONTINUE, token, None)

    def __repr__(self):
        return 'continue;'

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

class WhileStatement(Statement):
    def __init__(self, token, condition, blockStatement):
        super(WhileStatement, self).__init__(STATEMENT_TYPE_WHILE, token, blockStatement)
        self.condition = condition #expression

    @property
    def blockStatement(self):
        return self.value

    def __repr__(self):
        return 'while (%s) %s' % (self.condition, self.blockStatement)

class ForStatement(Statement):
    def __init__(self, token, iterator, iterable, blockStatement):
        super(ForStatement, self).__init__(STATEMENT_TYPE_FOR, token, blockStatement)
        self.iterable = iterable #expression evaluating to iterable
        self.iterator = iterator

    @property
    def blockStatement(self):
        return self.value

    def __repr__(self):
        return 'for (%s in %s) %s' % (self.iterator, self.iterable, self.blockStatement)

class ClassStatement(Statement):
    def __init__(self, token, name, methodStatements):
        super(ClassStatement, self).__init__(STATEMENT_TYPE_CLASS, token, name)
        self.methodStatements = methodStatements

    @property
    def name(self):
        return self.value

    def __repr__(self):
        return 'class %s { %s }' % (self.name, '; '.join([str(m) for m in self.methodStatements]))

class MethodStatement(Statement):
    def __init__(self, token, name, parameters, body):
        self.parameters = parameters #list of identifiers
        self.body = body #BlockStatement
        self.name = name

    def __repr__(self):
        return '%s (%s) %s' % (self.name, ','.join([str(p) for p in self.parameters]), self.body)

class Identifier(Expression):
    def __init__(self, token, value=None):
        super(Identifier, self).__init__(EXPRESSION_TYPE_IDENT, token)
        self.value = value if value is not None else token.literal

    def __repr__(self):
        return str(self.value)

class InstanceReference(Expression):
    def __init__(self, token):
        super(InstanceReference, self).__init__(EXPRESSION_TYPE_INSTANCE_REF, token)

    def __repr__(self):
        return 'this'

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

class StringLiteral(Expression):
    def __init__(self, token, value):
        super(StringLiteral, self).__init__(EXPRESSION_TYPE_STR_LIT, token)
        self.value = value

    def __repr__(self):
        return '"%s"' % str(self.value)

class NullLiteral(Expression):
    def __init__(self, token):
        super(NullLiteral, self).__init__(EXPRESSION_TYPE_NULL_LIT, token)

    def __repr__(self):
        return 'null'

class ArrayLiteral(Expression):
    def __init__(self, token, elements):
        super(ArrayLiteral, self).__init__(EXPRESSION_TYPE_ARRAY_LIT, token)
        self.value = elements

    @property
    def elements(self):
        return self.value

    def __repr__(self):
        return '[%s]' % (','.join([str(e) for e in self.elements]))

class HashLiteral(Expression):
    def __init__(self, token, elements):
        super(HashLiteral, self).__init__(EXPRESSION_TYPE_HASH_LIT, token)
        self.value = elements #list of (k, v) tuples

    @property
    def elements(self):
        return self.value

    def __repr__(self):
        return '{%s}' % (','.join(['%s:%s' % (k, v) for k, v in self.elements]))

class FunctionLiteral(Expression):
    def __init__(self, token, parameters, body):
        super(FunctionLiteral, self).__init__(EXPRESSION_TYPE_FUNC_LIT, token)
        self.parameters = parameters #list of identifiers
        self.body = body #BlockStatement
        self.name = None #only set in let statements

    def __repr__(self):
        return 'fn%s (%s) %s' % (self.name if self.name else '', ','.join([str(p) for p in self.parameters]), self.body)

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

class GetExpression(Expression):
    def __init__(self, token, object, property):
        super(GetExpression, self).__init__(EXPRESSION_TYPE_GET, token)
        self.object = object
        self.property = property

    def __repr__(self):
        return '%s.%s' % (self.object, self.property)

class IndexExpression(Expression):
    def __init__(self, token, left, index):
        super(IndexExpression, self).__init__(EXPRESSION_TYPE_INDEX, token)
        self.left = left #expression
        self.index = index #expression

    def __repr__(self):
        return '(%s[%s])' % (self.left, self.index)

class IfExpression(Expression):
    def __init__(self, token, conditionalBlocks, alternative):
        super(IfExpression, self).__init__(EXPRESSION_TYPE_IF, token)
        self.conditionalBlocks = conditionalBlocks #tuple of (condition, blockStatement)s
        self.alternative = alternative

    def __repr__(self):
        alt = (' else %s' % self.alternative) if self.alternative else ''
        formatted = []
        for i, conditionalBlock in enumerate(self.conditionalBlocks):
            condition, consequence = conditionalBlock
            if i == 0:
                formatted.append('if (%s) %s' % (condition, consequence))
            else:
                formatted.append('elif (%s) %s' % (condition, consequence))

        return ('%s%s' % (' '.join(formatted), alt))

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
