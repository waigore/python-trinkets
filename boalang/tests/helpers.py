from boa.parse import Parser
from boa.compile import Compiler
from boa.vm import VM
from boa.environment import Environment

class CompileHelper(object):
    def __init__(self, testCase, code):
        self.code = code
        self.testCase = testCase

        self.parser = Parser(code)
        program = self.parser.parseProgram()

        self.compiler = Compiler()
        self.compiler.compile(program)
        self.bytecode = self.compiler.bytecode()

    def checkInstructionsExpected(self, instructions):
        self.testCase.assertEqual(self.bytecode.instructions, instructions)

    def checkConstantsExpected(self, constants):
        cVals = [c.value for c in self.bytecode.constants]
        self.testCase.assertEqual(len(cVals), len(constants))
        for c, expectedC in zip(cVals, constants):
            self.testCase.assertEqual(c, expectedC)

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

    def checkStackExpected(self, expectedPairs):
        inspectedStack = self.vm.inspectStack()
        self.testCase.assertEqual(len(expectedPairs), len(inspectedStack))
        for stackEl, expectedPair in zip(inspectedStack, expectedPairs):
            expectedType, expectedVal = expectedPair
            self.testCase.assertEqual(stackEl.objectType, expectedType)
            self.testCase.assertEqual(stackEl.inspect(), expectedVal)

    def checkLastPoppedExpected(self, expectedType, expectedValue):
        obj = self.vm.lastPoppedStackEl()
        self.testCase.assertEqual(obj.objectType, expectedType)
        self.testCase.assertEqual(obj.inspect(), expectedValue)

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
