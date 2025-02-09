import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from nsolve.board import NonogramBoard

class TestBoard(unittest.TestCase):
    def test_initboard(self):
        board = NonogramBoard(dimen=(5, 5)) #5 across, 5 down
        self.assertEqual(board.across, 5)
        self.assertEqual(board.down, 5)
        self.assertTrue(board.islands_valid())
        self.assertEqual(board.expected_fill_count(), 0)

        b = str(board)
        self.assertEqual(b, """
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
""".strip('\n'))
    
    def test_initboardwithislands(self):
        islands = {
            "across": [
                [1, 1, 1],
                [],
                [1],
                [1, 1],
                [],
            ],
            "down": [
                [1],
                [1],
                [1, 1],
                [1],
                [1]
            ]
        }
        board = NonogramBoard(dimen=(5, 5), islands=islands)
        self.assertTrue(board.islands_valid())
        self.assertEqual(board.expected_fill_count(), 6)

        b = str(board)
        self.assertEqual(b, """
  1             
  1        1    
  1     1  1    
|  |  |  |  |  | 1
|  |  |  |  |  | 1
|  |  |  |  |  | 1 1
|  |  |  |  |  | 1
|  |  |  |  |  | 1
""".strip('\n'))
        
    def test_initboardwithinvalidislands(self):
        islands = {
            "across": [
                [1, 1, 1],
                [],
                [],
                [],
                [],
            ],
            "down": [
                [1],
                [],
                [],
                [],
                [1]
            ]
        }
        board = NonogramBoard(dimen=(5, 5), islands=islands)
        self.assertFalse(board.islands_valid())

    def test_markboard(self):
        board = NonogramBoard(dimen=(5, 5)) #5 across, 5 down
        board.mark_crossed((0, 1))
        board.mark_empty((4, 2))
        board.mark_filled((3, 2))
        
        b = str(board)
        self.assertEqual(b, """
|  |  |  |  |  |
|X |  |  |  |  |
|  |  |  |O |  |
|  |  |  |  |  |
|  |  |  |  |  |
""".strip('\n'))

    

if __name__ == '__main__':
    unittest.main()