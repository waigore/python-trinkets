from .parse import Parser
from .lex import Lexer
from .evaluator import boaEval

try:
    import readline
except:
    pass

PROMPT = ">> "

class Repl(object):
    def __init__(self):
        pass

    def start(self):
        while True:
            try:
                line = input(PROMPT)
            except EOFError:
                return
            except KeyboardInterrupt:
                return

            p = Parser(line)
            program = p.parseProgram()

            if len(p.errors) > 0:
                for err in p.errors:
                    print(err.msg)
                continue

            evaluated = boaEval(program)
            if evaluated is not None:
                print(evaluated.inspect())
