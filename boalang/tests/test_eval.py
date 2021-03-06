import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from boa.parse import Parser
from boa.evaluator import boaEval
from boa.environment import Environment
from boa.object import OBJECT_TYPES

class TestEval(unittest.TestCase):
    def test_intLiteral(self):
        code = """5"""
        env = Environment()
        result = env.evaluate(code)
        self.assertEqual(result.objectType, OBJECT_TYPES.OBJECT_TYPE_INT)
        self.assertEqual(result.value, 5)

    def test_boolLiteral(self):
        code = """true"""
        env = Environment()
        result = env.evaluate(code)
        self.assertEqual(result.objectType, OBJECT_TYPES.OBJECT_TYPE_BOOLEAN)
        self.assertEqual(result.value, True)

    def test_prefixExpressions(self):
        exprs = [
            ("!true", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, False),
            ("!false", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("!5", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, False),
            ("-254", OBJECT_TYPES.OBJECT_TYPE_INT, -254),
            ("not true", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, False),
        ]

        for code, expectedType, expectedValue in exprs:
            env = Environment()
            result = env.evaluate(code)
            self.assertEqual(result.objectType, expectedType)
            self.assertEqual(result.value, expectedValue)

    def test_infixExpressions(self):
        exprs = [
            ("1 + 1", OBJECT_TYPES.OBJECT_TYPE_INT, 2),
            ("1 - 1", OBJECT_TYPES.OBJECT_TYPE_INT, 0),
            ("1 * 1", OBJECT_TYPES.OBJECT_TYPE_INT, 1),
            ("1 / 1", OBJECT_TYPES.OBJECT_TYPE_INT, 1),
            ("1 == 1", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("1 != 1", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, False),
            ("1 > 1", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, False),
            ("1 > 0", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("1 < 1", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, False),
            ("1 < 2", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("1 <= 2", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("1 >= -1", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("1 + 1 == 2", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("6 * 7 - 1 == 41", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("true == true", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("true == false", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, False),
            ("true != true", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, False),
            ("true != false", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("'foobar' + 'barfoo'", OBJECT_TYPES.OBJECT_TYPE_STRING, "foobarbarfoo"),
            ("'foobar' == 'barfoo'", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, False),
            ("'foobar' != 'barfoo'", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("1 in [1, 2, 3]", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("1 notin [1, 2, 3]", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, False),
            ("1 notin [1, 2, 3] == not(1 in [1, 2, 3])", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("'1' in '123'", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("'mon' + 'key' == 'monkey'", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ('"\\nmy\\rfair\\tlady\\b\\\\\\\'\\\""', OBJECT_TYPES.OBJECT_TYPE_STRING, '\nmy\rfair\tlady\b\\\'\"'),
            ("'monkey'.length", OBJECT_TYPES.OBJECT_TYPE_INT, 6),
            ("('mon' + 'key').length", OBJECT_TYPES.OBJECT_TYPE_INT, 6),
            ("[].length", OBJECT_TYPES.OBJECT_TYPE_INT, 0),
            ("[1, 2, 3, 4, 5, 6].length", OBJECT_TYPES.OBJECT_TYPE_INT, 6),
            ("[[0], [1, 2]][1].length", OBJECT_TYPES.OBJECT_TYPE_INT, 2),
            ('("mon"+"key").toUpper().toLower() == "monkey"', OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
        ]

        for code, expectedType, expectedValue in exprs:
            env = Environment()
            result = env.evaluate(code)
            self.assertEqual(result.objectType, expectedType)
            self.assertEqual(result.value, expectedValue)

    def test_arrays(self):
        exprs = [
            ("[1, 2, 3, 4, 5]", OBJECT_TYPES.OBJECT_TYPE_ARRAY, "[1, 2, 3, 4, 5]"),
            ("[1] + [1]", OBJECT_TYPES.OBJECT_TYPE_ARRAY, "[1, 1]"),
            ("[1] + ['1']", OBJECT_TYPES.OBJECT_TYPE_ARRAY, '[1, "1"]'),
        ]

        for code, expectedType, expectedValue in exprs:
            env = Environment()
            result = env.evaluate(code)
            self.assertEqual(result.objectType, expectedType)
            self.assertEqual(result.inspect(), expectedValue)

    def test_ifExpressions(self):
        exprs = [
            ("if (5 * 5 + 10 > 34) { 99 } else { 100 }", OBJECT_TYPES.OBJECT_TYPE_INT, 99),
            ("if (false) { 99 } elif (true) { 101 } else { 100 }", OBJECT_TYPES.OBJECT_TYPE_INT, 101),
            ("if (false) { 99 } elif (false) { 101 } else { 100 }", OBJECT_TYPES.OBJECT_TYPE_INT, 100),
        ]

        for code, expectedType, expectedValue in exprs:
            env = Environment()
            result = env.evaluate(code)
            self.assertEqual(result.objectType, expectedType)
            self.assertEqual(result.value, expectedValue)

    def test_returnStatements(self):
        exprs = [
            ("""
                if (10 > 1) {
                    if (10 > 1) {
                        return 10;
                    }
                    return 1;
                }
            """, OBJECT_TYPES.OBJECT_TYPE_INT, 10)
        ]

        for code, expectedType, expectedValue in exprs:
            env = Environment()
            result = env.evaluate(code)
            self.assertEqual(result.objectType, expectedType)
            self.assertEqual(result.value, expectedValue)

    def test_builtins(self):
        exprs = [
            ("""len("abc")""", OBJECT_TYPES.OBJECT_TYPE_INT, 3),
            ("""len("")""", OBJECT_TYPES.OBJECT_TYPE_INT, 0),
            ("""len([1, 2, 3, 4, 5])""", OBJECT_TYPES.OBJECT_TYPE_INT, 5),
        ]

        for code, expectedType, expectedValue in exprs:
            env = Environment()
            result = env.evaluate(code)
            self.assertEqual(result.objectType, expectedType)
            self.assertEqual(result.value, expectedValue)

    def test_assignmentsAndLoops(self):
        exprs = [
            ("let a = 1; a = a + 1; a", OBJECT_TYPES.OBJECT_TYPE_INT, 2),
            ("let a = [1, 2, 3, 4, 5]; a[0] = 5; a[0]", OBJECT_TYPES.OBJECT_TYPE_INT, 5),
            ("let a = [1, 2, 3, 4, 5]; let b = [3]; let c = a[0] + b[0]; c", OBJECT_TYPES.OBJECT_TYPE_INT, 4),
            ("let a = 1; if (true) { a = 2; }; a", OBJECT_TYPES.OBJECT_TYPE_INT, 2),
            ("let a = 1; if (true) { let a = 2; }; a", OBJECT_TYPES.OBJECT_TYPE_INT, 1),
            ("let a = 1; while (a < 10) { a = a + 1; } a", OBJECT_TYPES.OBJECT_TYPE_INT, 10),
            ("let a = 1; let b = 0; while (a < 10) { a = a + 1; let b = a; } b", OBJECT_TYPES.OBJECT_TYPE_INT, 0),
            ("let a = 1; let b = 0; while (a < 10) { a = a + 1; b = a; } b", OBJECT_TYPES.OBJECT_TYPE_INT, 10),
            ("""
             let a = 1;
             let b = 1;
             while (a < 10) {
                while (b < 10) {
                    if (b >= 5) {
                        break;
                    }
                    b = b + 1;
                }
                a = a + 1;
             }
             a + b
             """, OBJECT_TYPES.OBJECT_TYPE_INT, 15),
             ("let a = if (true) { 1 }; a", OBJECT_TYPES.OBJECT_TYPE_INT, 1),
             ("let a = if (false) { 1 }; a", OBJECT_TYPES.OBJECT_TYPE_NULL, None),
             ("let a = 0; for (i in [1, 2, 3]) { a = a + i; } a", OBJECT_TYPES.OBJECT_TYPE_INT, 6),
             ("let a = 0; for (i in [1, 2, 3, 4, 5]) { a = a + i; if (a > 5) { break; } } a", OBJECT_TYPES.OBJECT_TYPE_INT, 6),
             ("let nop = fn() {} let a = nop(); a", OBJECT_TYPES.OBJECT_TYPE_NULL, None),
             ("let adder = fn(amt) { return fn(x) {x+amt}}; let myAdder = adder(2); myAdder(5)", OBJECT_TYPES.OBJECT_TYPE_INT, 7),
             ("let a = 0; let d = {1:1, 2:2, 3:3}; for (i in d) { a = a + d[i]; } a", OBJECT_TYPES.OBJECT_TYPE_INT, 6),
        ]

        for code, expectedType, expectedValue in exprs:
            env = Environment()
            result = env.evaluate(code)
            self.assertEqual(result.objectType, expectedType)
            self.assertEqual(result.value, expectedValue)

    def test_objectsAndAttributes(self):
        exprs = [
            ("let a = object(); a.getLength = fn() { return this.length; }; a.length = 5; a.getLength()", OBJECT_TYPES.OBJECT_TYPE_INT, 5),
            ("let a = object(); a.b = object(); a.getB = fn() { return this.b; }; a.b.name = 'ABC'; a.getB().name", OBJECT_TYPES.OBJECT_TYPE_STRING, "ABC"),
            ("let a = object(); a.b = '123456'; a.isLong = fn() { if (this.b.length > 4) { true } else { false } }; a.isLong()", OBJECT_TYPES.OBJECT_TYPE_BOOLEAN, True),
            ("let a = object(); a.string = '123456'; a.number = 123456; a.get = fn(x) { if (x) { this.string } else { this.number} }; a.get(true)", OBJECT_TYPES.OBJECT_TYPE_STRING, "123456"),
        ]

        for code, expectedType, expectedValue in exprs:
            env = Environment()
            result = env.evaluate(code)
            self.assertEqual(result.objectType, expectedType)
            self.assertEqual(result.value, expectedValue)

    def test_classes(self):
        exprs = [
            ("class A { size() { return this.numItems; } }; let a = A(); a.numItems = 4; a.size()", OBJECT_TYPES.OBJECT_TYPE_INT, 4),
            ("class Point { constructor(x, y) { this.x = x; this.y = y; } }; let p = Point(1, 2); p.x + p.y", OBJECT_TYPES.OBJECT_TYPE_INT, 3),
            ("class Person { constructor(name) { this.setName(name); } setName(name) { this.name = name; } getName() { return this.name;} }; let p = Person('Jekyll'); p.getName()", OBJECT_TYPES.OBJECT_TYPE_STRING, "Jekyll"),
        ]

        for code, expectedType, expectedValue in exprs:
            env = Environment()
            result = env.evaluate(code)
            self.assertEqual(result.objectType, expectedType)
            self.assertEqual(result.value, expectedValue)

    def test_evalErrors(self):
        exprs = [
            ("true + false", OBJECT_TYPES.OBJECT_TYPE_ERROR),
        ]

        for code, expectedType in exprs:
            env = Environment()
            result = env.evaluate(code)
            self.assertEqual(result.objectType, expectedType)

if __name__ == '__main__':
    unittest.main()
