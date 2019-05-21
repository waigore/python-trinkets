from .parse import Parser
from .evaluator import boaEval
from .ast import EXPRESSION_TYPE_IDENT

class BoaParserError(Exception):
    def __init__(self, msg, errors):
        super(BoaParserError, self).__init__(msg)
        self.errors = errors

class BoaEvalError(Exception): pass

class BoaEnvError(Exception): pass

class Environment(object):
    def __init__(self, outer=None, instance=None):
        self.store = {}
        self.outer = outer
        self.instance = instance

    def newInner(self):
        env = Environment(outer=self)
        return env

    def getGlobal(self, identName):
        if not identName not in self.store and self.outer is not None:
            return self.outer.getGlobal(identName)
        try:
            val = self.store[identName]
        except:
            raise BoaEnvError('Identifier not declared: %s' % (str(identName)))
        return val

    def getIdentifier(self, ident):
        if ident.expressionType != EXPRESSION_TYPE_IDENT:
            raise BoaEvalError('Node not identifier: %s' % (str(ident)))

        if not ident.value in self.store and self.outer is not None:
            return self.outer.getIdentifier(ident)
        try:
            val = self.store[ident.value]
        except:
            raise BoaEnvError('Identifier not declared: %s' % (str(ident)))
        return val

    def hasIdentifier(self, ident):
        if ident.expressionType != EXPRESSION_TYPE_IDENT:
            raise BoaEvalError('Node not identifier: %s' % (str(ident)))
        if not ident.value in self.store and self.outer is not None:
            return self.outer.hasIdentifier(ident)
        return ident.value in self.store

    def declareIdentifier(self, ident, val):
        if ident.expressionType != EXPRESSION_TYPE_IDENT:
            raise BoaEvalError('Node not identifier: %s' % (str(ident)))
        self.store[ident.value] = val

    def setIdentifier(self, ident, val):
        if ident.expressionType != EXPRESSION_TYPE_IDENT:
            raise BoaEvalError('Node not identifier: ' % (str(ident)))
        if ident.value not in self.store:
            if self.outer is not None:
                self.outer.setIdentifier(ident, val)
                return
            else:
                raise BoaEnvError('Identifier not declared: %s' % (str(ident)))
        self.store[ident.value] = val #val is BoaObject

    def evaluate(self, code):
        p = Parser(code)
        program = p.parseProgram()
        if len(p.errors) > 0:
            raise BoaParserError("Errors during parsing", p.errors)
        return boaEval(program, self)
