import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from nsolve.board import NonogramBoard
from nsolve.line import LineSolver, LineOrientation

class TestLine(unittest.TestCase):
    def test_initandsolvelinefromboard(self):
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
        line_solver = LineSolver(board, line_orientation=LineOrientation.ACROSS, location=0)
        self.assertTrue(line_solver.dirty)
        l = str(line_solver)
        self.assertEqual(l, """
|  |  |  |  |  | 1 *
""".strip('\n'))
        
        line_solver.solve()
        l = str(line_solver)
        self.assertFalse(line_solver.dirty)
        self.assertEqual(l, """
|  |  |  |  |  | 1
 *  *  *  *  *   1
""".strip('\n'))
        
        line_solver2 = LineSolver(board, line_orientation=LineOrientation.DOWN, location=0)
        line_solver2.solve()
        l2 = str(line_solver2)
        self.assertEqual(l2, """
|O |X |O |X |O | [1] [1] [1]
 *               1
       *         1
             *   1
""".strip('\n'))
        
        line_solver3 = LineSolver(board, line_orientation=LineOrientation.ACROSS, location=2)
        line_solver3.solve()
        l3 = str(line_solver3)
        self.assertEqual(l3, """
|  |  |  |  |  | 1 1
 *  *  *         1
       *  *  *   1
""".strip('\n'))

if __name__ == '__main__':
    unittest.main()