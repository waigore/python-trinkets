import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from nsolve.board import NonogramBoard
from nsolve.solve import NonogramSolver

class TestNonogramSolve(unittest.TestCase):
    def test_initandsolveboard(self):
        islands = {
            "across": [
                [3],
                [1, 1],
                [5],
                [1, 1],
                [2],
            ],
            "down": [
                [1, 1],
                [1, 1, 1],
                [5],
                [1],
                [3]
            ]
        }
        board = NonogramBoard(dimen=(5, 5), islands=islands)
        solver = NonogramSolver.from_board(board)
        self.assertFalse(solver.solved)

        solver.solve()
        self.assertTrue(solver.solved)
        b = str(board)
        self.assertEqual(b, """
     1     1    
  3  1  5  1  2 
|O |X |O |X |X | 1 1
|O |X |O |X |O | 1 1 1
|O |O |O |O |O | 5
|X |X |O |X |X | 1
|X |O |O |O |X | 3
""".strip('\n'))
