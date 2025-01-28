import unittest

from test_board import TestBoard
from test_line import TestLine
from test_solveline5x5 import TestSolveLine5x5
from testutil import add_test_cases

import lines_5x5

def suite():
    #all test cases imported into the main variable get auto added to the suite
    mySuite = unittest.TestSuite()
    return mySuite

if __name__ == '__main__':
    add_test_cases(TestSolveLine5x5, lines_5x5.lines)

    unittest.main()
