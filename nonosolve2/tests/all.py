import unittest

from test_board import TestBoard

def suite():
    #all test cases imported into the main variable get auto added to the suite
    mySuite = unittest.TestSuite()
    return mySuite

if __name__ == '__main__':
    unittest.main()
