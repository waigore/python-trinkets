
GLOBAL_SCOPE = "GLOBAL_SCOPE"
LOCAL_SCOPE = "LOCAL_SCOPE"
BUILTIN_SCOPE = "BUILTIN_SCOPE"
FREE_SCOPE = "FREE_SCOPE"
BLOCK_SCOPE = "BLOCK_SCOPE"
FUNCTION_SCOPE = "FUNCTION_SCOPE"
CLASS_SCOPE = "CLASS_SCOPE"

class SymbolNotFoundError(Exception): pass

class Symbol(object):
    def __init__(self, name, scope, index, scopeDiff=0):
        self.name = name
        self.scope = scope #String denoting the scope name
        self.scopeDiff = scopeDiff
        self.index = index

class SymbolTable(object):
    def __init__(self, outer=None, isFunction=False):
        self.store = {} #maps strings to Symbols
        self.freeSymbols = [] #list of Symbols
        self.numClasses = 0
        self.numDefinitions = 0
        self.outer = outer #Enclosing SymbolTable
        self.isFunction = isFunction

    def define(self, name): #accepts string, returns Symbols
        symbol = Symbol(name, GLOBAL_SCOPE, self.numDefinitions)
        if self.outer is None:
            symbol.scope = GLOBAL_SCOPE
        else:
            symbol.scope = LOCAL_SCOPE
        self.store[name] = symbol
        self.numDefinitions += 1
        return symbol

    def defineClassName(self, name):
        symbol = Symbol(name, CLASS_SCOPE, self.numClasses)
        self.store[name] = symbol
        self.numClasses += 1
        return symbol

    def defineFunctionName(self, name):
        symbol = Symbol(name, FUNCTION_SCOPE, 0)
        self.store[name] = symbol
        return symbol

    def defineFree(self, origSymbol):
        self.freeSymbols.append(origSymbol)
        symbol = Symbol(origSymbol.name, FREE_SCOPE, len(self.freeSymbols)-1)
        self.store[origSymbol.name] = symbol
        return symbol

    def defineBuiltin(self, index, name):
        symbol = Symbol(name, BUILTIN_SCOPE, index)
        self.store[name] = symbol
        return symbol

    def innerResolve(self, name, scopeDiff, fnScopeInbtwn):
        if name in self.store:
            return self, self.store[name], scopeDiff, False
        if self.outer is None:
            raise SymbolNotFoundError(name)
        scope, sym, sd, isF = self.outer.innerResolve(name, scopeDiff+1, self.isFunction or fnScopeInbtwn)
        if sym.scope in [GLOBAL_SCOPE, BUILTIN_SCOPE, CLASS_SCOPE]:
            return scope, sym, sd, isF
        elif sym.scope == LOCAL_SCOPE:
            if not self.isFunction and not fnScopeInbtwn:
                blockSymbol = Symbol(name, BLOCK_SCOPE, sym.index, sd)
                return scope, blockSymbol, sd, isF
        elif sym.scope == BLOCK_SCOPE:
            if not self.isFunction and not fnScopeInbtwn:
                blockSymbol.scopeDiff = sd
                return scope, blockSymbol, sd, isF

        sym = self.defineFree(sym)
        return scope, sym, sd, isF

    def resolve(self, name):
        scope, symbol, scopeDiff, fnScopeInbtwn = self.innerResolve(name, 0, self.isFunction)
        return symbol
