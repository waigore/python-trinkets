from .parse import Parser
from .lex import Lexer
from .evaluator import boaEval
from .environment import Environment, BoaParserError

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
                if evaluated is not None:
                    print(evaluated.inspect())
            except BoaParserError as bpe:
                for err in bpe.errors:
                    print(err.msg)
                continue
