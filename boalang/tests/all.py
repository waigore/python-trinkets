import unittest

from test_lex import TestLexing
from test_parse import TestParsing
from test_eval import TestEval
from test_code import TestCode
from test_compile import TestCompilation
from test_vm import TestVM
from test_equiv import TestEquivEvalVM

def suite():
    #all test cases imported into the main variable get auto added to the suite it seems
    mySuite = unittest.TestSuite()
    return mySuite

if __name__ == '__main__':
    unittest.main()
