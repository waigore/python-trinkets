import argparse
from boa import VM, Compiler, Parser

if __name__ == '__main__':
    argParser = argparse.ArgumentParser(description='Boa language interpreter')
    argParser.add_argument('scripts', metavar='SCRIPT', type=str, nargs='+', help='scripts to execute sequentially')

    args = argParser.parse_args()
    for script in args.scripts:
        with open(script, 'r') as f:
            code = f.read()
        parser = Parser(code)
        compiler = Compiler()
        try:
            program = parser.parseProgram()
        except Exception as e:
            print('Error during parsing: ' + e.message)
            continue

        try:
            compiler.compile(program)
        except Exception as e:
            print('Error during compilation: ' + e.message)
            continue

        try:
            vm = VM(compiler.bytecode())
            vm.run()
        except Exception as e:
            print('Error during execution: ' + e.message)
            continue
