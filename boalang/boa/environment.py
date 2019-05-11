from .parse import Parser
from .evaluator import boaEval
from .ast import EXPRESSION_TYPE_IDENT

class BoaParserError(Exception):
    def __init__(self, msg, errors):
        super(BoaParserError, self).__init__(msg)
        self.errors = errors

class BoaEnvError(Exception): pass

class Environment(object):
    def __init__(self, outer=None):
        self.store = {}
        self.outer = outer

    def newInner(self):
        env = Environment(outer=self)
        return env

    def getIdentifier(self, ident):
        if ident.expressionType != EXPRESSION_TYPE_IDENT:
            raise BoaEnvError('Node not identifier: ' % (str(ident)))

        if not self.hasIdentifier(ident) and self.outer is not None:
            return self.outer.getIdentifier(ident)
        return self.store[ident.value]

    def hasIdentifier(self, ident):
        if ident.expressionType != EXPRESSION_TYPE_IDENT:
            raise BoaEnvError('Node not identifier: ' % (str(ident)))
        return ident.value in self.store

    def setIdentifier(self, ident, val):
        if ident.expressionType != EXPRESSION_TYPE_IDENT:
            raise BoaEnvError('Node not identifier: ' % (str(ident)))
        self.store[ident.value] = val #val is BoaObject
        return val

    def evaluate(self, code):
        p = Parser(code)
        program = p.parseProgram()
        if len(p.errors) > 0:
            raise BoaParserError("Errors during parsing", p.errors)
        return boaEval(program, self)
