import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from nsolve.lineutil import generate_pstate_combi

class TestPstateCombiGen(unittest.TestCase):
    def test_simplegen(self):
        pstate_matrix = [
            [(0,), (1,), (2,)],
            [(2,), (3,), (4,)]
        ] #5x5 1 1
        pstate_combis = generate_pstate_combi(pstate_matrix)
        self.assertEqual(len(pstate_combis.keys()), 9)
    
    def test_complexgen(self):
        pstate_matrix = [
            [(0,), (1,), (2,), (3,)],
            [(2,), (3,), (4,), (5,)],
            [(4, 5, 6, 7, 8), (5, 6, 7, 8, 9), (6, 7, 8, 9, 10), (7, 8, 9, 10, 11)],
            [(10, 11), (11, 12), (12, 13), (13, 14)]
        ] #15x15 1 1 5 2
        pstate_combis = generate_pstate_combi(pstate_matrix)
        #print(pstate_combis)
        self.assertEqual(len(pstate_combis.keys()), 256)

if __name__ == '__main__':
    unittest.main()