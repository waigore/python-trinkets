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
    EXPRESSION_TYPE_INFIX,
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
        elif exprType == EXPRESSION_TYPE_INFIX:
            leftEvaluated = boaEval(node.left)
            rightEvaluated = boaEval(node.right)
            return evalInfixExpression(node.operator, leftEvaluated, rightEvaluated)

    return None

def evalStatements(statements):
    result = None
    for statement in statements:
        result = boaEval(statement)

    return result

def evalPrefixExpression(operator, right):
    if operator == TOKEN_TYPES.TOKEN_TYPE_EXCLAMATION.value:
        return evalExclamationOperatorExpression(right)
    elif operator == TOKEN_TYPES.TOKEN_TYPE_NOT.value:
        return evalExclamationOperatorExpression(right)
    elif operator == TOKEN_TYPES.TOKEN_TYPE_MINUS.value:
        return evalMinusOperatorExpression(right)
    else:
        return None

def evalInfixExpression(operator, left, right):
    if left.objectType == OBJECT_TYPES.OBJECT_TYPE_INT and \
            right.objectType == OBJECT_TYPES.OBJECT_TYPE_INT:
        return evalIntegerInfixExpression(operator, left, right)
    else:
        return None

def evalIntegerInfixExpression(operator, left, right):
    leftVal = left.value
    rightVal = right.value

    if operator == TOKEN_TYPES.TOKEN_TYPE_PLUS.value:
        return newObject(OBJECT_TYPE_INT, leftVal + rightVal)
    elif operator == TOKEN_TYPES.TOKEN_TYPE_MINUS.value:
        return newObject(OBJECT_TYPE_INT, leftVal - rightVal)
    elif operator == TOKEN_TYPES.TOKEN_TYPE_ASTERISK.value:
        return newObject(OBJECT_TYPE_INT, leftVal * rightVal)
    elif operator == TOKEN_TYPES.TOKEN_TYPE_SLASH.value:
        return newObject(OBJECT_TYPE_INT, leftVal / rightVal)
    elif operator == TOKEN_TYPES.TOKEN_TYPE_GT.value:
        return TRUE if leftVal > rightVal else FALSE
    elif operator == TOKEN_TYPES.TOKEN_TYPE_LT.value:
        return TRUE if leftVal < rightVal else FALSE
    elif operator == TOKEN_TYPES.TOKEN_TYPE_GTEQ.value:
        return TRUE if leftVal >= rightVal else FALSE
    elif operator == TOKEN_TYPES.TOKEN_TYPE_LTEQ.value:
        return TRUE if leftVal <= rightVal else FALSE
    elif operator == TOKEN_TYPES.TOKEN_TYPE_EQ.value:
        return TRUE if leftVal == rightVal else FALSE
    elif operator == TOKEN_TYPES.TOKEN_TYPE_NEQ.value:
        return TRUE if leftVal != rightVal else FALSE
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
