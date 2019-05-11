from .token import TOKEN_TYPES
from .object import (
    newInteger,
    newReturnValue,
    newError,
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
    STATEMENT_TYPE_LET,
    STATEMENT_TYPE_ASSIGN,
    EXPRESSION_TYPE_IDENT,
    EXPRESSION_TYPE_INT_LIT,
    EXPRESSION_TYPE_BOOLEAN,
    EXPRESSION_TYPE_PREFIX,
    EXPRESSION_TYPE_INFIX,
    EXPRESSION_TYPE_IF,
)

def boaEval(node, env=None):
    nodeType = node.nodeType

    if nodeType == NODE_TYPE_PROGRAM:
        return evalProgram(node, env)
    elif nodeType == NODE_TYPE_STATEMENT:
        stmtType = node.statementType
        if stmtType == STATEMENT_TYPE_EXPRESSION:
            return boaEval(node.expression, env)
        elif stmtType == STATEMENT_TYPE_BLOCK:
            return evalBlockStatement(node, env)
        elif stmtType == STATEMENT_TYPE_RETURN:
            val = boaEval(node.value, env)
            if isError(val):
                return val
            return newReturnValue(val)
        elif stmtType == STATEMENT_TYPE_LET:
            val = boaEval(node.value, env)
            if isError(val):
                return val
            env.setIdentifier(node.identifier, val)
        elif stmtType == STATEMENT_TYPE_ASSIGN:
            if not env.hasIdentifier(node.identifier):
                return newError("Identifier not declared: %s" % node.identifier.value)
            val = boaEval(node.value, env)
            if isError(val):
                return val
            env.setIdentifier(node.identifier, val)
    elif nodeType == NODE_TYPE_EXPRESSION:
        exprType = node.expressionType
        if exprType == EXPRESSION_TYPE_INT_LIT:
            return newInteger(node.value)
        elif exprType == EXPRESSION_TYPE_IDENT:
            return evalIdentifier(node, env)
        elif exprType == EXPRESSION_TYPE_BOOLEAN:
            return TRUE if node.value else FALSE
        elif exprType == EXPRESSION_TYPE_PREFIX:
            rightEvaluated = boaEval(node.right, env)
            if isError(rightEvaluated):
                return rightEvaluated
            return evalPrefixExpression(node.operator, rightEvaluated, env)
        elif exprType == EXPRESSION_TYPE_INFIX:
            leftEvaluated = boaEval(node.left, env)
            if isError(leftEvaluated):
                return leftEvaluated
            rightEvaluated = boaEval(node.right, env)
            if isError(rightEvaluated):
                return rightEvaluated
            return evalInfixExpression(node.operator, leftEvaluated, rightEvaluated, env)
        elif exprType == EXPRESSION_TYPE_IF:
            return evalIfExpression(node, env)

    return None

def evalProgram(program, env):
    result = None
    for statement in program.statements:
        result = boaEval(statement, env)
        if result is not None:
            if result.objectType == OBJECT_TYPES.OBJECT_TYPE_RETURN_VALUE:
                return result.value
            elif result.objectType == OBJECT_TYPES.OBJECT_TYPE_ERROR:
                return result

    return result

def evalBlockStatement(block, env):
    result = None
    for statement in block.statements:
        result = boaEval(statement, env)
        if result is not None:
            typ = result.objectType
            if typ in [OBJECT_TYPES.OBJECT_TYPE_RETURN_VALUE, OBJECT_TYPES.OBJECT_TYPE_ERROR]:
                return result

    return result

def evalPrefixExpression(operator, right, env):
    if operator == TOKEN_TYPES.TOKEN_TYPE_EXCLAMATION.value:
        return evalExclamationOperatorExpression(right, env)
    elif operator == TOKEN_TYPES.TOKEN_TYPE_NOT.value:
        return evalExclamationOperatorExpression(right, env)
    elif operator == TOKEN_TYPES.TOKEN_TYPE_MINUS.value:
        return evalMinusOperatorExpression(right, env)
    else:
        return newError("Unknown operator: %s%s" % (operator, right.objectType))

def evalInfixExpression(operator, left, right, env):
    if left.objectType != right.objectType:
        return newError("Type mismatch: %s %s " % (left.objectType, operator, right.objectType))
    if left.objectType == OBJECT_TYPES.OBJECT_TYPE_INT and \
            right.objectType == OBJECT_TYPES.OBJECT_TYPE_INT:
        return evalIntegerInfixExpression(operator, left, right, env)
    elif left.objectType == OBJECT_TYPES.OBJECT_TYPE_BOOLEAN and \
            right.objectType == OBJECT_TYPES.OBJECT_TYPE_BOOLEAN:
        return evalBooleanInfixExpression(operator, left, right, env)
    else:
        return newError("Unknown operator: %s %s %s" % (left.objectType, operator, right.objectType))

def evalIfExpression(node, env):
    conditionEvaluated = boaEval(node.condition, env)
    if isError(conditionEvaluated):
        return conditionEvaluated

    if isTruthy(conditionEvaluated):
        return boaEval(node.consequence, env)
    elif node.alternative is not None:
        return boaEval(node.alternative, env)
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

def isError(obj):
    if obj is None: return False
    return obj.objectType == OBJECT_TYPES.OBJECT_TYPE_ERROR

def evalIdentifier(node, env):
    if not env.hasIdentifier(node):
        return newError("Identifier not found: %s" % node.value)
    val = env.getIdentifier(node)
    return val

def evalBooleanInfixExpression(operator, left, right, env):
    leftVal = left.value
    rightVal = right.value

    if operator == TOKEN_TYPES.TOKEN_TYPE_EQ.value:
        return TRUE if leftVal == rightVal else FALSE
    elif operator == TOKEN_TYPES.TOKEN_TYPE_NEQ.value:
        return TRUE if leftVal != rightVal else FALSE
    else:
        return newError("Unknown operator: %s %s %s" % (left.objectType, operator, right.objectType))

def evalIntegerInfixExpression(operator, left, right, env):
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
        return newError("Unknown operator: %s %s %s" % (left.objectType, operator, right.objectType))

def evalExclamationOperatorExpression(right, env):
    if right == TRUE:
        return FALSE
    elif right == FALSE:
        return TRUE
    elif right == NULL:
        return TRUE
    else:
        return FALSE

def evalMinusOperatorExpression(right, env):
    if right.objectType != OBJECT_TYPES.OBJECT_TYPE_INT:
        return newError("Unknown operator: -%s" % right.objectType)
    value = right.value
    return newInteger(-right.value)
