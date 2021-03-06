from .token import TOKEN_TYPES
from .object import (
    newInteger,
    newString,
    newArray,
    newHash,
    newReturnValue,
    newError,
    newFunction,
    newMethod,
    newClass,
    newClassInstance,
    NULL,
    TRUE,
    FALSE,
    BREAK,
    CONTINUE,
    OBJECT_TYPES,
    OBJECT_TYPE_INT,
    OBJECT_TYPE_BOOLEAN,
    OBJECT_TYPE_STRING,
    OBJECT_TYPE_ARRAY,
    OBJECT_TYPE_HASH,
    OBJECT_TYPE_FUNCTION,
    OBJECT_TYPE_BUILTIN_FUNCTION,
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
    STATEMENT_TYPE_WHILE,
    STATEMENT_TYPE_FOR,
    STATEMENT_TYPE_BREAK,
    STATEMENT_TYPE_CONTINUE,
    STATEMENT_TYPE_CLASS,
    STATEMENT_TYPE_METHOD,
    EXPRESSION_TYPE_IDENT,
    EXPRESSION_TYPE_INSTANCE_REF,
    EXPRESSION_TYPE_INT_LIT,
    EXPRESSION_TYPE_FUNC_LIT,
    EXPRESSION_TYPE_STR_LIT,
    EXPRESSION_TYPE_ARRAY_LIT,
    EXPRESSION_TYPE_HASH_LIT,
    EXPRESSION_TYPE_BOOLEAN,
    EXPRESSION_TYPE_NULL_LIT,
    EXPRESSION_TYPE_PREFIX,
    EXPRESSION_TYPE_INFIX,
    EXPRESSION_TYPE_INDEX,
    EXPRESSION_TYPE_GET,
    EXPRESSION_TYPE_IF,
    EXPRESSION_TYPE_CALL,
)
from .builtins import BUILTIN_FUNCTIONS

CLASS_DEFS = {
}

def lookupClass(name):
    try:
        return CLASS_DEFS[name]
    except:
        return None

def registerClass(name, clazz):
    CLASS_DEFS[name] = clazz

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
        elif stmtType == STATEMENT_TYPE_BREAK:
            return BREAK
        elif stmtType == STATEMENT_TYPE_CONTINUE:
            return CONTINUE
        elif stmtType == STATEMENT_TYPE_WHILE:
            return evalWhileStatement(node, env)
        elif stmtType == STATEMENT_TYPE_FOR:
            return evalForStatement(node, env)
        elif stmtType == STATEMENT_TYPE_RETURN:
            if node.value is None:
                return newReturnValue(NULL)
            val = boaEval(node.value, env)
            if isError(val):
                return val
            return newReturnValue(val)
        elif stmtType == STATEMENT_TYPE_LET:
            val = boaEval(node.value, env)
            if isError(val):
                return val
            try:
                env.declareIdentifier(node.identifier, val)
                return NULL
            except Exception as e:
                return newError(e.message)
        elif stmtType == STATEMENT_TYPE_ASSIGN:
            if node.identifier.expressionType == EXPRESSION_TYPE_INDEX:
                return indexedAssignStatement(node, env)
            elif node.identifier.expressionType == EXPRESSION_TYPE_IDENT:
                return assignStatement(node, env)
            elif node.identifier.expressionType == EXPRESSION_TYPE_GET:
                return propertyAssignStatement(node, env)
            else:
                return newError("Identifier not valid: %s" % node.identifier)
        elif stmtType == STATEMENT_TYPE_CLASS:
            return evalClassStatement(node, env)
    elif nodeType == NODE_TYPE_EXPRESSION:
        exprType = node.expressionType
        if exprType == EXPRESSION_TYPE_INT_LIT:
            return newInteger(node.value)
        elif exprType == EXPRESSION_TYPE_STR_LIT:
            return newString(node.value)
        elif exprType == EXPRESSION_TYPE_ARRAY_LIT:
            elementsEvaluated = evalExpressions(node.elements, env)
            if len(elementsEvaluated) == 1 and isError(elementsEvaluated[0]):
                return elementsEvaluated[0]
            return newArray(elementsEvaluated)
        elif exprType == EXPRESSION_TYPE_HASH_LIT:
            return evalHashLiteral(node, env)
        elif exprType == EXPRESSION_TYPE_IDENT:
            return evalIdentifier(node, env)
        elif exprType == EXPRESSION_TYPE_INSTANCE_REF:
            return evalInstanceRef(node, env)
        elif exprType == EXPRESSION_TYPE_BOOLEAN:
            return TRUE if node.value else FALSE
        elif exprType == EXPRESSION_TYPE_NULL_LIT:
            return NULL
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
        elif exprType == EXPRESSION_TYPE_INDEX:
            leftEvaluated = boaEval(node.left, env)
            if isError(leftEvaluated):
                return leftEvaluated
            idxEvaluated = boaEval(node.index, env)
            if isError(idxEvaluated):
                return idxEvaluated
            return evalIndexExpression(leftEvaluated, idxEvaluated)
        elif exprType == EXPRESSION_TYPE_GET:
            objEvaluated = boaEval(node.object, env)
            if isError(objEvaluated):
                return objEvaluated
            return evalGetExpression(objEvaluated, node.property, env)
        elif exprType == EXPRESSION_TYPE_IF:
            return evalIfExpression(node, env)
        elif exprType == EXPRESSION_TYPE_FUNC_LIT:
            params = node.parameters
            body = node.body
            return newFunction(params, body, env)
        elif exprType == EXPRESSION_TYPE_CALL:
            function = boaEval(node.function, env)
            if isError(function):
                return function

            args = evalExpressions(node.arguments, env)
            if len(args) == 1 and isError(args[0]):
                return args[0]

            return applyFunction(function, args)

    return newError("Could not evaluate: %s" % node)

def evalProgram(program, env):
    result = NULL
    for statement in program.statements:
        result = boaEval(statement, env)
        if result is not None:
            if result.objectType == OBJECT_TYPES.OBJECT_TYPE_RETURN_VALUE:
                return result.value
            elif result.objectType == OBJECT_TYPES.OBJECT_TYPE_ERROR:
                return result

    return result

def evalBlockStatement(block, env):
    result = NULL
    for statement in block.statements:
        result = boaEval(statement, env)
        if result is not None:
            typ = result.objectType
            if typ in [
                    OBJECT_TYPES.OBJECT_TYPE_RETURN_VALUE,
                    OBJECT_TYPES.OBJECT_TYPE_ERROR,
                    OBJECT_TYPES.OBJECT_TYPE_CONTINUE,
                    OBJECT_TYPES.OBJECT_TYPE_BREAK]:
                return result

    return result

def evalLoopBlockStatement(block, env): #returns true if loop execution should continue, false otherwise
    result = NULL
    for statement in block.statements:
        result = boaEval(statement, env)
        if result is not None:
            typ = result.objectType
            if typ in [OBJECT_TYPES.OBJECT_TYPE_RETURN_VALUE,
                    OBJECT_TYPES.OBJECT_TYPE_ERROR,
                    OBJECT_TYPES.OBJECT_TYPE_BREAK]:
                return result, False
            elif typ == OBJECT_TYPES.OBJECT_TYPE_CONTINUE:
                return result, True

    return result, True

def evalIndexedAssignment(left, idx, val, env):
    try:
        left[idx] = val
        return NULL
    except:
        return newError("Could not assign value to subscript %s of %s" % (idx.inspect(), left.objectType))

def evalAttributeAssignment(obj, attrName, val, env):
    try:
        if val.objectType == OBJECT_TYPES.OBJECT_TYPE_FUNCTION:
            method = newMethod(obj, val.parameters, val.body, env)
            obj.setAttribute(attrName, method)
        #elif val.objectType == OBJECT_TYPES.OBJECT_TYPE_METHOD:
        #    return newError("Instance method cannot be rebound: %s.%s" % (attrName, obj.inspect()))
        else:
            obj.setAttribute(attrName, val)
        return NULL
    except Exception as e:
        return newError("Could not assign value to attribute %s of %s" % (attrName, obj.inspect()))

def evalAttributeIndexAssignment(obj, left, idx, val, env):
    if left.expressionType == EXPRESSION_TYPE_IDENT:
        leftEvaluated = evalGetIdentExpression(obj, left, env)
    elif left.expressionType == EXPRESSION_TYPE_INDEX:
        leftEvaluated = evalGetIndexExpression(obj, left, env)
    else:
        return newError("Attribute index assignment not supported: %s.%s[%s]" % obj.inspect(), left, idx)
    if isError(leftEvaluated):
        return leftEvaluated

    idxEvaluated = boaEval(idx, env)
    if isError(idxEvaluated):
        return idxEvaluated

    return evalIndexedAssignment(leftEvaluated, idxEvaluated, val, env)

def propertyAssignStatement(node, env):
    setExpr = node.identifier
    val = node.value
    objEvaluated = boaEval(setExpr.object, env)
    if isError(objEvaluated):
        return objEvaluated

    valEvaluated = boaEval(val, env)
    if isError(valEvaluated):
        return valEvaluated

    return setExpressionAssignStatement(objEvaluated, setExpr.property, valEvaluated, env)


def setExpressionAssignStatement(obj, property, val, env):
    if property.expressionType == EXPRESSION_TYPE_IDENT:
        return evalAttributeAssignment(obj, property.value, val, env)
    elif property.expressionType == EXPRESSION_TYPE_INDEX:
        return evalAttributeIndexAssignment(obj, property.left, property.index, val, env)
    elif property.expressionType == EXPRESSION_TYPE_GET:
        attrEvaluated = evalGetExpression(obj, property.object, env)
        return setExpressionAssignStatement(attrEvaluated, property.property, val, env)
    else:
        return newError("Assignment not supported: %s" % property)

def indexedAssignStatement(node, env):
    identEvaluated = boaEval(node.identifier.left, env)
    if isError(identEvaluated):
        return identEvaluated

    idxEvaluated = boaEval(node.identifier.index, env)
    if isError(idxEvaluated):
        return idxEvaluated

    if not identEvaluated.objectType.isIterable:
        return newError("Identifier not subscriptable: %s" % ident.value)

    val = boaEval(node.value, env)
    if isError(val):
        return val

    return evalIndexedAssignment(identEvaluated, idxEvaluated, val, env)

def assignStatement(node, env):
    ident = node.identifier
    if not env.hasIdentifier(ident):
        return newError("Identifier not declared: %s" % ident.value)

    val = boaEval(node.value, env)
    if isError(val):
        return val

    try:
        env.setIdentifier(node.identifier, val)
        return NULL
    except Exception as e:
        return newError(e.message)

def evalClassStatement(node, env):
    className = node.name
    clazz = lookupClass(className)
    #if clazz:
    #    return newError("Class already defined: %s" % clazz.name)

    methods = {}
    for methodStatement in node.methodStatements:
        method = evalMethodStatement(methodStatement, env)
        #methods.append(method)
        methods[methodStatement.name] = method

    if node.constructorStatement:
        cs = node.constructorStatement
        constructorEvaluated = newFunction(cs.parameters, cs.body, env)

    clazz = newClass(className, node.constructorStatement, methods, env)
    registerClass(className, clazz)

    return NULL

def evalMethodStatement(node, env):
    return newFunction(node.parameters, node.body, env)

def evalWhileStatement(node, env):
    result = NULL
    while True:
        conditionEvaluated = boaEval(node.condition, env)
        if isError(conditionEvaluated):
            return conditionEvaluated

        if isTruthy(conditionEvaluated):
            innerEnv = env.newInner()
            result, continueExecution = evalLoopBlockStatement(node.blockStatement, innerEnv)
            if not continueExecution:
                break
        else:
            break
    if result is not None and result.objectType in [OBJECT_TYPES.OBJECT_TYPE_BREAK, OBJECT_TYPES.OBJECT_TYPE_CONTINUE]:
        return NULL
    return result

def evalForStatement(node, env):
    result = NULL
    iterator = node.iterator
    iterableEvaluated = boaEval(node.iterable, env)
    if isError(iterableEvaluated):
        return iterableEvaluated

    if not iterableEvaluated.objectType.isIterable:
        return newError("For expression not iterable: %s" % iterableEvaluated.inspect())

    for obj in iterableEvaluated:
        innerEnv = env.newInner()
        innerEnv.declareIdentifier(iterator, obj)
        result, continueExecution = evalLoopBlockStatement(node.blockStatement, innerEnv)
        if not continueExecution:
            break

    if result is not None and result.objectType in [OBJECT_TYPES.OBJECT_TYPE_BREAK, OBJECT_TYPES.OBJECT_TYPE_CONTINUE]:
        return NULL
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
    if left.objectType == OBJECT_TYPES.OBJECT_TYPE_INT and \
            right.objectType == OBJECT_TYPES.OBJECT_TYPE_INT:
        return evalIntegerInfixExpression(operator, left, right, env)
    elif left.objectType == OBJECT_TYPES.OBJECT_TYPE_BOOLEAN and \
            right.objectType == OBJECT_TYPES.OBJECT_TYPE_BOOLEAN:
        return evalBooleanInfixExpression(operator, left, right, env)
    elif left.objectType == OBJECT_TYPES.OBJECT_TYPE_STRING and \
            right.objectType == OBJECT_TYPES.OBJECT_TYPE_STRING:
        return evalStringInfixExpression(operator, left, right, env)
    elif left.objectType == OBJECT_TYPES.OBJECT_TYPE_ARRAY and \
            right.objectType == OBJECT_TYPES.OBJECT_TYPE_ARRAY:
        return evalArrayInfixExpression(operator, left, right, env)
    elif operator == TOKEN_TYPES.TOKEN_TYPE_IN.value and right.objectType.isIterable:
        return evalInExpression(left, right)
    elif operator == TOKEN_TYPES.TOKEN_TYPE_NOTIN.value and right.objectType.isIterable:
        return evalNotinExpression(left, right)
    else:
        return newError("Unknown operator: %s %s %s" % (left.objectType, operator, right.objectType))

def evalInExpression(left, right):
    return TRUE if left in right else FALSE

def evalNotinExpression(left, right):
    return TRUE if left not in right else FALSE

def evalIndexExpression(left, index):
    if left.objectType == OBJECT_TYPES.OBJECT_TYPE_ARRAY and \
            index.objectType == OBJECT_TYPES.OBJECT_TYPE_INT:
        return evalArrayIndexExpression(left, index)
    elif left.objectType == OBJECT_TYPES.OBJECT_TYPE_HASH:
        return evalHashIndexExpression(left, index)
    elif left.objectType == OBJECT_TYPES.OBJECT_TYPE_STRING:
        return evalStringIndexExpression(left, index)
    else:
        return newError("Indexing not supported: %s[%s]" % (left.objectType, index.objectType))

def evalGetExpression(objEvaluated, property, env):
    if isError(objEvaluated):
        return objEvaluated
    if property.expressionType == EXPRESSION_TYPE_IDENT:
        return evalGetIdentExpression(objEvaluated, property, env)
    elif property.expressionType == EXPRESSION_TYPE_INDEX:
        return evalGetIndexExpression(objEvaluated, property, env)
    elif property.expressionType == EXPRESSION_TYPE_CALL:
        return evalGetCallExpression(objEvaluated, property, env)
    elif property.expressionType == EXPRESSION_TYPE_GET:
        try:
            attributeEvaluated = evalGetExpression(objEvaluated, property.object, env)
            if isError(attributeEvaluated):
                return attributeEvaluated
            #nextIdent = property.object
            #if nextIdent.expressionType == EXPRESSION_TYPE_IDENT:
            #    attributeEvaluated = evalGetIdentExpression(objEvaluated, nextIdent, env)
            #elif nextIdent.expressionType == EXPRESSION_TYPE_INDEX:
            #    attributeEvaluated = evalGetIndexExpression(objEvaluated, nextIdent, env)
        except Exception as e:
            return newError("Could not get attribute %s.%s: %s" % (objEvaluated, nextIdent, e.message))
        return evalGetExpression(attributeEvaluated, property.property, env)
    else:
        return newError("Property not gettable: %s.%s" % (objEvaluated, property))

def evalGetIdentExpression(objEvaluated, property, env):
    try:
        return objEvaluated.getAttribute(property.value)
    except Exception as e:
        return newError("Could not get attribute: %s" % e.message)

def evalGetIndexExpression(objEvaluated, property, env):
    #if property.left.expressionType != EXPRESSION_TYPE_IDENT:
    #    return newError("Attribute access not supported: %s.%s" % (obj, property.left))
    try:
        #if property.left.expressionType == EXPRESSION_TYPE_IDENT:
        #    leftEvaluated = evalGetIdentExpression(objEvaluated, property.left, env)
        #elif property.left.expressionType == EXPRESSION_TYPE_INDEX:
        #    leftEvaluated = evalGetIndexExpression(objEvaluated, property.left, env)
        leftEvaluated = evalGetExpression(objEvaluated, property.left, env)
        #else:
        #    return newError("Property not gettable: %s.%s" % (objEvaluated, property))
        if isError(leftEvaluated):
            return leftEvaluated
        idxEvaluated = boaEval(property.index, env)
        if isError(idxEvaluated):
            return idxEvaluated
        return evalIndexExpression(leftEvaluated, idxEvaluated)
    except Exception as e:
        return newError("Could not get attribute: %s" % e.message)

def evalGetCallExpression(objEvaluated, property, env):
    try:
        methodEvaluated = evalGetExpression(objEvaluated, property.function, env)
        if isError(methodEvaluated):
            return methodEvaluated
        if methodEvaluated.objectType != OBJECT_TYPES.OBJECT_TYPE_BUILTIN_METHOD:
            return newError("Not a method: %s" % property)

        args = evalExpressions(property.arguments, env)
        if len(args) == 1 and isError(args[0]):
            return args[0]

        return applyFunction(methodEvaluated, args)
    except Exception as e:
        return newError("Could not get attribute: %s" % e.message)

def evalArrayIndexExpression(left, index):
    arr = left.value
    idx = index.value
    try:
        val = arr[idx]
    except:
        return newError("Array index error: %s" % index.inspect())
    return val

def evalHashIndexExpression(left, index):
    try:
        val = left[index]
    except Exception as e:
        return newError("Hash index error: %s" % index.inspect())
    return val

def evalStringIndexExpression(left, index):
    try:
        val = left[index]
    except Exception as e:
        return newError("String index error: %s" % index.inspect())
    return val

def evalIfExpression(node, env):
    for condition, consequence in node.conditionalBlocks:
        conditionEvaluated = boaEval(condition, env)
        if isError(conditionEvaluated):
            return conditionEvaluated

        if isTruthy(conditionEvaluated):
            innerEnv = env.newInner()
            return boaEval(consequence, innerEnv)

    if node.alternative is not None:
        innerEnv = env.newInner()
        return boaEval(node.alternative, innerEnv)
    else:
        return NULL

def evalExpressions(exprs, env):
    result = []
    for expr in exprs:
        evaluated = boaEval(expr, env)
        if isError(evaluated):
            return [evaluated]
        result.append(evaluated)
    return result

def applyFunction(function, args):
    if function.objectType == OBJECT_TYPES.OBJECT_TYPE_FUNCTION:
        innerEnv = extendFunctionEnv(function, args, function.env)
        evaluated = boaEval(function.body, innerEnv)
        if isError(evaluated):
            return evaluated
        return unwrapReturnValue(evaluated)
    elif function.objectType == OBJECT_TYPES.OBJECT_TYPE_METHOD:
        innerEnv = extendFunctionEnv(function, args, function.env)
        innerEnv.instance = function.instance
        evaluated = boaEval(function.body, innerEnv)
        if isError(evaluated):
            return evaluated
        return unwrapReturnValue(evaluated)
    elif function.objectType == OBJECT_TYPES.OBJECT_TYPE_BUILTIN_FUNCTION:
        return function.func(args)
    elif function.objectType == OBJECT_TYPES.OBJECT_TYPE_BUILTIN_METHOD:
        return function.func(args)
    elif function.objectType == OBJECT_TYPES.OBJECT_TYPE_CLASS:
        clazz = function
        instance, constructor = clazz.createInstance()
        if constructor:
            innerEnv = extendFunctionEnv(constructor, args, constructor.env)
            innerEnv.instance = instance
            evaluated = boaEval(constructor.body, innerEnv)
            if isError(evaluated):
                return evaluated
        return instance

    return newError("Cannot call: %s" % function.objectType)

def extendFunctionEnv(function, args, env):
    newEnv = env.newInner()
    for param, arg in zip(function.parameters, args):
        newEnv.declareIdentifier(param, arg)
    return newEnv

def unwrapReturnValue(obj):
    if obj.objectType != OBJECT_TYPES.OBJECT_TYPE_RETURN_VALUE:
        return obj
    else:
        return obj.value

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

def evalHashLiteral(node, env):
    pairs = []

    for key, val in node.elements:
        keyEvaluated = boaEval(key, env)
        if isError(keyEvaluated):
            return keyEvaluated

        if not keyEvaluated.objectType.isHashable:
            return newError("Key not hashable: %s" % keyEvaluated.inspect())

        valueEvaluated = boaEval(val, env)
        if isError(valueEvaluated):
            return valueEvaluated

        pairs.append((keyEvaluated, valueEvaluated))

    return newHash(pairs)

def evalIdentifier(node, env):
    try:
        val = env.getIdentifier(node)
    except:
        bfn = getBuiltinFunction(node.value)
        if bfn:
            return bfn
        else:
            clazz = lookupClass(node.value)
            if clazz:
                return clazz
        return newError("Identifier not found: %s" % node.value)
    return val

def evalInstanceRef(node, env):
    if env.instance is None:
        if env.outer is not None:
            return evalInstanceRef(node, env.outer)
        else:
            return newError("Not bound to instance: %s" % node.token)
    return env.instance

def getBuiltinFunction(name):
    if name not in BUILTIN_FUNCTIONS: return None
    return BUILTIN_FUNCTIONS[name]

def evalBooleanInfixExpression(operator, left, right, env):
    leftVal = left.value
    rightVal = right.value

    if operator == TOKEN_TYPES.TOKEN_TYPE_EQ.value:
        return TRUE if leftVal == rightVal else FALSE
    elif operator == TOKEN_TYPES.TOKEN_TYPE_NEQ.value:
        return TRUE if leftVal != rightVal else FALSE
    elif operator == TOKEN_TYPES.TOKEN_TYPE_OR.value:
        return TRUE if leftVal or rightVal else FALSE
    elif operator == TOKEN_TYPES.TOKEN_TYPE_AND.value:
        return TRUE if leftVal and rightVal else FALSE
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

def evalStringInfixExpression(operator, left, right, env):
    leftVal = left.value
    rightVal = right.value

    if operator == TOKEN_TYPES.TOKEN_TYPE_PLUS.value:
        return newString(leftVal + rightVal)
    elif operator == TOKEN_TYPES.TOKEN_TYPE_EQ.value:
        return TRUE if leftVal == rightVal else FALSE
    elif operator == TOKEN_TYPES.TOKEN_TYPE_NEQ.value:
        return TRUE if leftVal != rightVal else FALSE
    elif operator == TOKEN_TYPES.TOKEN_TYPE_IN.value:
        return TRUE if leftVal in rightVal else FALSE
    else:
        return newError("Unknown operator: %s %s %s" % (left.objectType, operator, right.objectType))

def evalArrayInfixExpression(operator, left, right, env):
    leftVal = left.value
    rightVal = right.value

    if operator == TOKEN_TYPES.TOKEN_TYPE_PLUS.value:
        return newArray(leftVal + rightVal)
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
