import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from boa.code import OPCONSTANT, makeInstr
from boa.compile import Compiler
from boa.object import OBJECT_TYPES
from boa.parse import Parser
from boa.vm import VM

class VMHelper(object):
    def __init__(self, testCase, code):
        self.code = code
        self.testCase = testCase

        self.parser = Parser(code)
        program = self.parser.parseProgram()

        self.compiler = Compiler()
        self.compiler.compile(program)
        self.bytecode = self.compiler.bytecode()

        self.vm = VM(self.bytecode)
        self.vm.run()

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

class TestVM(unittest.TestCase):
    def test_infixOperations(self):
        helper = VMHelper(self, '3 + 5')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '8')

        helper = VMHelper(self, '1 + 2 - 3 + 4')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '4')

        helper = VMHelper(self, '2 * 2 * 2 * 2')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '16')

        helper = VMHelper(self, '5 * (2 + 10)')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '60')

        helper = VMHelper(self, 'true')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, 'true')

        helper = VMHelper(self, 'false')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, 'false')

        helper = VMHelper(self, 'true == false')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, 'false')

        helper = VMHelper(self, 'true == true')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, 'true')

        helper = VMHelper(self, '1 < 2')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, 'true')

        helper = VMHelper(self, '1 > 2 + 3')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, 'false')

        helper = VMHelper(self, '1 + 1 == 2')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, 'true')

        helper = VMHelper(self, '--5')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '5')

        helper = VMHelper(self, 'not true == false')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, 'true')

        helper = VMHelper(self, 'not true == !true')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, 'true')

        helper = VMHelper(self, 'not not false == ! not false')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, 'true')

        helper = VMHelper(self, 'if (true) { 10 } else { 20 }')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '10')

        helper = VMHelper(self, 'if (false) { 10 } elif (true) { 20 } else { 30 }')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '20')

        helper = VMHelper(self, 'if (false) { 10 } elif (true) { 20 }')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '20')

        helper = VMHelper(self, 'if (false) { 10 } else {  }')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_NULL, 'null')

        helper = VMHelper(self, 'if (true) {  } else { 10 }')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_NULL, 'null')

        helper = VMHelper(self, 'if (1 < 2) { 30 }')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '30')

        helper = VMHelper(self, 'if (1 > 2) { 10 }')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_NULL, 'null')

        helper = VMHelper(self, '!(if (false) { 5 })')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, 'true')

    def test_assignments(self):
        helper = VMHelper(self, 'let a = 1; let b = a; a+b')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '2')

        helper = VMHelper(self, 'let monkey = "mon" + "key"; monkey')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_STRING, '"monkey"')

        helper = VMHelper(self, 'let monkey = "mon" + "key"; monkey == "monkey"')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, 'true')

        helper = VMHelper(self, 'let a = if (true) { 10 }; a')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '10')

        helper = VMHelper(self, 'let a = if (false) { 10 }; a')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_NULL, 'null')

    def test_arraysAndHashes(self):
        helper = VMHelper(self, '[1, 2, 3]')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_ARRAY, '[1, 2, 3]')

        helper = VMHelper(self, '[1+2, 3-4, 5*6]')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_ARRAY, '[3, -1, 30]')

        helper = VMHelper(self, 'let b = ["mon"+"key", "boa", true]; (b[0] + b[1] == "monkeyboa") == b[2]')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, 'true')

        helper = VMHelper(self, 'let a = {1+1:2*2, 3+3:4*4}; a[2]')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '4')

        helper = VMHelper(self, 'let a = [0, 1]; a[1] = 3; a')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_ARRAY, '[0, 3]')

        helper = VMHelper(self, 'let a = {1:1, 2:2}; a[3] = 3; a[2] = 2*2; a[1]+a[2]+a[3]')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '8')

    def test_functionCalls(self):
        helper = VMHelper(self, 'let a = fn() { return 1; } a()')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '1')

        helper = VMHelper(self, 'fn() { return 1; }()')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '1')

        helper = VMHelper(self, 'fn() { 1+2*3-4; }()')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '3')

        helper = VMHelper(self, 'let a = fn() {1}; let b = fn() {a()+1}; let c = fn() {b()+1}; c()')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '3')

        helper = VMHelper(self, 'let a = fn() { return 1; 0} a()')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '1')

        helper = VMHelper(self, 'let a = fn(){1}; let aa = fn(){a}; aa()()')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '1')

        helper = VMHelper(self, 'let g = 50; let m = fn() {let n = 1; g-n}; let m2 = fn() { let n = 2; g-n}; m()+m2()')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '97')

        helper = VMHelper(self, 'let sum = fn(a,b){ let c = a + b; c;} sum(1, 2) + sum(3, 4)')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '10')

        helper = VMHelper(self, 'let sum = fn(a,b){ let c = a + b; c;} let outer = fn() { sum(1, 2) + sum(3, 4) }; outer()')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '10')

        helper = VMHelper(self, 'let g = 10; let s = fn(a, b){ let c = a+b; c + g;}; let outer = fn() { s(1, 2)+ s(3, 4)+g;}; outer()+g')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '50')

        helper = VMHelper(self, 'let g = if (true) { 10 } elif (false) {  } else { 30 }; g')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '10')

        helper = VMHelper(self, 'let g = if (1 < 2) { let b = 10; b/2 }; g')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '5')

        helper = VMHelper(self, 'let f = fn(a) { if (a > 5) { return true;} }; f(1)')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_NULL, 'null')

        helper = VMHelper(self, 'let f = fn(a) { if (a > 5) { return true; false} }; f(10)')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, 'true')

    def test_loops(self):
        helper = VMHelper(self, 'let a = 1; while (a < 10) { a = a + 1; }; a')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '10')

        helper = VMHelper(self, 'let a = 1; while (a < 10) { a = a + 1; if (a > 5) { break;} }; a')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '6')

        helper = VMHelper(self, 'let c = 0; let a = [1, 2, 3]; for (i in a) { c = c + i; }; c')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '6')

        helper = VMHelper(self, 'let c = 0; let a  = [1, 2, 3, 4, 5]; for (i in a) { c = c + i; if (i > 3) { break;} }; c')
        helper.checkLastPoppedExpected(OBJECT_TYPES.OBJECT_TYPE_INT, '10')
