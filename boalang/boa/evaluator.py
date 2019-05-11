from .token import TOKEN_TYPES
from .object import (
    newObject,
    NULL,
    TRUE,
    FALSE,
    OBJECT_TYPES,
    OBJECT_TYPE_INT,
    OBJECT_TYPE_BOOLEAN,
)
from .ast import (
    NODE_TYPE_PROGRAM,
    NODE_TYPE_STATEMENT,
    NODE_TYPE_EXPRESSION,
    STATEMENT_TYPE_EXPRESSION,
    EXPRESSION_TYPE_INT_LIT,
    EXPRESSION_TYPE_BOOLEAN,
    EXPRESSION_TYPE_PREFIX,
)

def boaEval(node):
    nodeType = node.nodeType

    if nodeType == NODE_TYPE_PROGRAM:
        return evalStatements(node.statements)
    elif nodeType == NODE_TYPE_STATEMENT:
        stmtType = node.statementType
        if stmtType == STATEMENT_TYPE_EXPRESSION:
            return boaEval(node.expression)
    elif nodeType == NODE_TYPE_EXPRESSION:
        exprType = node.expressionType
        if exprType == EXPRESSION_TYPE_INT_LIT:
            return newObject(OBJECT_TYPE_INT, node.value)
        elif exprType == EXPRESSION_TYPE_BOOLEAN:
            return TRUE if node.value else FALSE
        elif exprType == EXPRESSION_TYPE_PREFIX:
            rightEvaluated = boaEval(node.right)
            return evalPrefixExpression(node.operator, rightEvaluated)

    return None

def evalStatements(statements):
    result = None
    for statement in statements:
        result = boaEval(statement)

    return result

def evalPrefixExpression(operator, right):
    if operator == TOKEN_TYPES.TOKEN_TYPE_EXCLAMATION.value:
        return evalExclamationOperatorExpression(right)
    elif operator == TOKEN_TYPES.TOKEN_TYPE_MINUS.value:
        return evalMinusOperatorExpression(right)
    else:
        return None

def evalExclamationOperatorExpression(right):
    if right == TRUE:
        return FALSE
    elif right == FALSE:
        return TRUE
    elif right == NULL:
        return TRUE
    else:
        return FALSE

def evalMinusOperatorExpression(right):
    if right.objectType != OBJECT_TYPES.OBJECT_TYPE_INT:
        return None
    value = right.value
    return newObject(OBJECT_TYPE_INT, -right.value)
