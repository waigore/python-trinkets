import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from boa import Environment, Compiler, VM, Parser
from boa.object import OBJECT_TYPES

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__)) + '/scripts'

class Script(object):
    def __init__(self, scriptName, asserts):
        self.scriptName = scriptName
        self.asserts = asserts

SCRIPTS = [
    Script('01_lets.boa', [
        ('a', OBJECT_TYPES.OBJECT_TYPE_INT, '3'),
        ('b', OBJECT_TYPES.OBJECT_TYPE_INT, '2'),
        ('c', OBJECT_TYPES.OBJECT_TYPE_INT, '3'),
    ]),
    Script('02_expressions.boa', [
        ('a', OBJECT_TYPES.OBJECT_TYPE_INT, '-3'),
        ('b', OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, 'true'),
        ('monkey', OBJECT_TYPES.OBJECT_TYPE_STRING, '"monkey"'),
        ('arr', OBJECT_TYPES.OBJECT_TYPE_ARRAY, '[3, -1, 30]'),
        ('m3', OBJECT_TYPES.OBJECT_TYPE_INT, '97'),
    ]),
    Script('03_funcs.boa', [
        ('f', OBJECT_TYPES.OBJECT_TYPE_INT, '50'),
    ]),
    Script('04_loops.boa', [
        ('a', OBJECT_TYPES.OBJECT_TYPE_INT, '10'),
        ('b', OBJECT_TYPES.OBJECT_TYPE_ARRAY, '[2, 4, 6]'),
        ('c', OBJECT_TYPES.OBJECT_TYPE_INT, '6'),
        ('i', OBJECT_TYPES.OBJECT_TYPE_INT, '10'),
    ]),
    Script('05_loops2.boa', [
        ('a', OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, 'true'),
        ('b', OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, 'false'),
        ('c', OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, 'true'),
    ]),
    Script('06_closures.boa', [
        ('val', OBJECT_TYPES.OBJECT_TYPE_INT, '6'),
        ('val2', OBJECT_TYPES.OBJECT_TYPE_INT, '11'),
        ('val3', OBJECT_TYPES.OBJECT_TYPE_INT, '28'),
    ]),
    Script('07_blocks.boa', [
        ('c', OBJECT_TYPES.OBJECT_TYPE_INT, '15'),
    ]),
    Script('08_objects.boa', [
        ('johnGreeting', OBJECT_TYPES.OBJECT_TYPE_STRING, '"Greetings Jack, my name is John and I am a programmer."'),
        ('jackGreeting', OBJECT_TYPES.OBJECT_TYPE_STRING, '"Greetings John, my name is Jack and I am a manager."'),
    ]),
]

class VMHelper(object):
    def __init__(self, testCase, code):
        self.code = code
        self.testCase = testCase

        self.parser = Parser(code)
        program = self.parser.parseProgram()

        self.compiler = Compiler()
        self.compiler.compile(program)
        self.bytecode = self.compiler.bytecode()

        self.vm = VM(self.bytecode, self.compiler.symbolTable)
        self.vm.run()

        self.checkSanity()

    def checkSanity(self):
        #this WILL blow up if an errant opcode left something on the stack for example...
        self.testCase.assertEqual(self.vm.sp, 0)
        self.testCase.assertEqual(self.vm.frameIndex, 1)

    def checkGlobalExpected(self, identifier, typ, value):
        self.testCase.assertEqual(self.vm.getGlobal(identifier).objectType, typ)
        self.testCase.assertEqual(self.vm.getGlobal(identifier).inspect(), value)

class EnvHelper(object):
    def __init__(self, testCase, code):
        self.code = code
        self.testCase = testCase

        self.env = Environment()
        self.env.evaluate(code)

    def checkGlobalExpected(self, identifier, typ, value):
        self.testCase.assertEqual(self.env.getGlobal(identifier).objectType, typ)
        self.testCase.assertEqual(self.env.getGlobal(identifier).inspect(), value)

class TestEquivEvalVM(unittest.TestCase):
    def runScriptAndAsserts(self, script, asserts):
        with open(script, 'r') as f:
            code = f.read()
        vmHelper = VMHelper(self, code)
        envHelper = EnvHelper(self, code)

        for identifier, expectedType, expectedValue in asserts:
            self.assertEqual(
                vmHelper.vm.getGlobal(identifier).inspect(),
                envHelper.env.getGlobal(identifier).inspect()
            )
            vmHelper.checkGlobalExpected(identifier, expectedType, expectedValue)
            envHelper.checkGlobalExpected(identifier, expectedType, expectedValue)

    def test_allScripts(self):
        for script in SCRIPTS:
            self.runScriptAndAsserts(SCRIPT_DIR + '/' + script.scriptName, script.asserts)

if __name__ == '__main__':
    unittest.main()
