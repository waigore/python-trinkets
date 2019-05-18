
GLOBAL_SCOPE = "GLOBAL_SCOPE"
LOCAL_SCOPE = "LOCAL_SCOPE"
BUILTIN_SCOPE = "BUILTIN_SCOPE"
FREE_SCOPE = "FREE_SCOPE"
FUNCTION_SCOPE = "FUNCTION_SCOPE"

class SymbolNotFoundError(Exception): pass

class Symbol(object):
    def __init__(self, name, scope, index):
        self.name = name
        self.scope = scope #String denoting the scope name
        self.index = index

class SymbolTable(object):
    def __init__(self, outer=None):
        self.store = {} #maps strings to Symbols
        self.freeSymbols = [] #list of Symbols
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

    def defineFunctionName(self, name):
        symbol = Symbol(name, FUNCTION_SCOPE, 0)
        self.store[name] = symbol

    def defineFree(self, origSymbol):
        self.freeSymbols.append(origSymbol)
        symbol = Symbol(origSymbol.name, FREE_SCOPE, len(self.freeSymbols)-1)
        self.store[origSymbol.name] = symbol
        return symbol

    def defineBuiltin(self, index, name):
        symbol = Symbol(name, BUILTIN_SCOPE, index)
        self.store[name] = symbol
        return symbol

    def resolve(self, name):
        try:
            return self.store[name]
        except:
            if self.outer is not None:
                sym = self.outer.resolve(name)
                if sym.scope in [GLOBAL_SCOPE, BUILTIN_SCOPE]:
                    return sym
                free = self.defineFree(sym)
                return free
            else:
                raise SymbolNotFoundError(name)
