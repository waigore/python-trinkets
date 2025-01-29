import unittest

from test_board import TestBoard
from test_line import TestLine
from test_lineutil import TestPstateCombiGen
from test_singlesolveline5x5 import TestSingleSolveLine5x5
from test_singlesolveline15x15 import TestSingleSolveLine15x15

from testutil import add_single_solve_test_cases

import lines_5x5
import lines_15x15

def suite():
    #all test cases imported into the main variable get auto added to the suite
    mySuite = unittest.TestSuite()
    return mySuite

if __name__ == '__main__':
    add_single_solve_test_cases(TestSingleSolveLine5x5, lines_5x5.lines)
    add_single_solve_test_cases(TestSingleSolveLine15x15, lines_15x15.lines)

    unittest.main()
