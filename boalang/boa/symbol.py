
GLOBAL_SCOPE = "GLOBAL_SCOPE"

class SymbolNotFoundError(Exception): pass

class Symbol(object):
    def __init__(self, name, scope, index):
        self.name = name
        self.scope = scope #String denoting the scope name
        self.index = index

class SymbolTable(object):
    def __init__(self):
        self.store = {} #maps strings to Symbols
        self.numDefinitions = 0

    def define(self, name): #accepts string, returns Symbols
        symbol = Symbol(name, GLOBAL_SCOPE, self.numDefinitions)
        self.store[name] = symbol
        self.numDefinitions += 1
        return symbol

    def resolve(self, name):
        try:
            return self.store[name]
        except:
            raise SymbolNotFoundError(name)
