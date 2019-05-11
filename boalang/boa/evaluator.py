from .token import TOKEN_TYPES
from .object import (
    newInteger,
    newReturnValue,
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
    STATEMENT_TYPE_BLOCK,
    STATEMENT_TYPE_RETURN,
    EXPRESSION_TYPE_INT_LIT,
    EXPRESSION_TYPE_BOOLEAN,
    EXPRESSION_TYPE_PREFIX,
    EXPRESSION_TYPE_INFIX,
    EXPRESSION_TYPE_IF,
)

def boaEval(node):
    nodeType = node.nodeType

    if nodeType == NODE_TYPE_PROGRAM:
        return evalProgram(node)
    elif nodeType == NODE_TYPE_STATEMENT:
        stmtType = node.statementType
        if stmtType == STATEMENT_TYPE_EXPRESSION:
            return boaEval(node.expression)
        elif stmtType == STATEMENT_TYPE_BLOCK:
            return evalBlockStatement(node)
        elif stmtType == STATEMENT_TYPE_RETURN:
            val = boaEval(node.value)
            return newReturnValue(val)
    elif nodeType == NODE_TYPE_EXPRESSION:
        exprType = node.expressionType
        if exprType == EXPRESSION_TYPE_INT_LIT:
            return newInteger(node.value)
        elif exprType == EXPRESSION_TYPE_BOOLEAN:
            return TRUE if node.value else FALSE
        elif exprType == EXPRESSION_TYPE_PREFIX:
            rightEvaluated = boaEval(node.right)
            return evalPrefixExpression(node.operator, rightEvaluated)
        elif exprType == EXPRESSION_TYPE_INFIX:
            leftEvaluated = boaEval(node.left)
            rightEvaluated = boaEval(node.right)
            return evalInfixExpression(node.operator, leftEvaluated, rightEvaluated)
        elif exprType == EXPRESSION_TYPE_IF:
            return evalIfExpression(node)

    return None

def evalProgram(program):
    result = None
    for statement in program.statements:
        result = boaEval(statement)
        if result.objectType == OBJECT_TYPES.OBJECT_TYPE_RETURN_VALUE:
            return result.value

    return result

def evalBlockStatement(block):
    result = None
    for statement in block.statements:
        result = boaEval(statement)
        if result is not None and result.objectType == OBJECT_TYPES.OBJECT_TYPE_RETURN_VALUE:
            return result

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
        return evalBooleanInfixExpression(operator, left, right)

def evalIfExpression(node):
    conditionEvaluated = boaEval(node.condition)

    if isTruthy(conditionEvaluated):
        return boaEval(node.consequence)
    elif node.alternative is not None:
        return boaEval(node.alternative)
    else:
        return None

def isTruthy(obj):
    if obj == NULL:
        return False
    elif obj == TRUE:
        return True
    elif obj == FALSE:
        return False
    else:
        return True

def evalBooleanInfixExpression(operator, left, right):
    leftVal = left.value
    rightVal = right.value

    if operator == TOKEN_TYPES.TOKEN_TYPE_EQ.value:
        return TRUE if leftVal == rightVal else FALSE
    elif operator == TOKEN_TYPES.TOKEN_TYPE_NEQ.value:
        return TRUE if leftVal != rightVal else FALSE
    else:
        return None

def evalIntegerInfixExpression(operator, left, right):
    leftVal = left.value
    rightVal = right.value

    if operator == TOKEN_TYPES.TOKEN_TYPE_PLUS.value:
        return newInteger(leftVal + rightVal)
    elif operator == TOKEN_TYPES.TOKEN_TYPE_MINUS.value:
        return newInteger(leftVal - rightVal)
    elif operator == TOKEN_TYPES.TOKEN_TYPE_ASTERISK.value:
        return newInteger(leftVal * rightVal)
    elif operator == TOKEN_TYPES.TOKEN_TYPE_SLASH.value:
        return newInteger(leftVal / rightVal)
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
    return newInteger(-right.value)
