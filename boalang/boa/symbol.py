
GLOBAL_SCOPE = "GLOBAL_SCOPE"
LOCAL_SCOPE = "LOCAL_SCOPE"

class SymbolNotFoundError(Exception): pass

class Symbol(object):
    def __init__(self, name, scope, index):
        self.name = name
        self.scope = scope #String denoting the scope name
        self.index = index

class SymbolTable(object):
    def __init__(self, outer=None):
        self.store = {} #maps strings to Symbols
        self.numDefinitions = 0
        self.outer = outer #Enclosing SymbolTable

    def define(self, name): #accepts string, returns Symbols
        symbol = Symbol(name, GLOBAL_SCOPE, self.numDefinitions)
        if self.outer is None:
            symbol.scope = GLOBAL_SCOPE
        else:
            symbol.scope = LOCAL_SCOPE
        self.store[name] = symbol
        self.numDefinitions += 1
        return symbol

    def resolve(self, name):
        try:
            return self.store[name]
        except:
            if self.outer is not None:
                return self.outer.resolve(name)
            else:
                raise SymbolNotFoundError(name)
