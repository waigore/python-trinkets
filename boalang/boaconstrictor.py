import argparse
from boa import Repl, Environment

if __name__ == '__main__':
    argParser = argparse.ArgumentParser(description='Boa language interpreter')
    argParser.add_argument('scripts', metavar='SCRIPT', type=str, nargs='*', help='scripts to execute sequentially')

    args = argParser.parse_args()
    if len(args.scripts) > 0:
        for script in args.scripts:
            with open(script, 'r') as f:
                code = f.read()
            env = Environment()
            env.evaluate(code)
    else:
        print('Boalang v1.0')
        repl = Repl()
        repl.start()
