from .parse import Parser
from .lex import Lexer
from .evaluator import boaEval
from .environment import Environment, BoaParserError
from .object import OBJECT_TYPES

try:
    import readline
except:
    pass

PROMPT = ">> "

class Repl(object):
    def __init__(self):
        self.env = Environment()

    def start(self):
        while True:
            try:
                line = input(PROMPT)
            except EOFError:
                return
            except KeyboardInterrupt:
                return

            try:
                evaluated = self.env.evaluate(line)
                if evaluated is not None and evaluated.objectType != OBJECT_TYPES.OBJECT_TYPE_NULL:
                    print(evaluated.inspect())
            except BoaParserError as bpe:
                for err in bpe.errors:
                    print(err.msg)
                continue
