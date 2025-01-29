import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from nsolve.board import TileType, NonogramIsland
from nsolve.line import LineSolver

def E():
    return TileType.EMPTY

def F():
    return TileType.FILLED

def C():
    return TileType.CROSSED

def I(val):
    return NonogramIsland(typ=None, location=0, value=val)

def map_creator(c):
    if c == ' ':
        return E
    elif c == 'O':
        return F
    elif c == 'X':
        return C
    else:
        raise ValueError('Unknown map type:', c)

def map_tile_name(c):
    if c == ' ':
        return '_'
    else:
        return c

def make_line_test_function(line_template, island_template, result):
    def test(self):
        line = [map_creator(t)() for t in line_template]
        solver = LineSolver.from_line(line=line, islands=[I(v) for v in island_template])
        solver.solve()

        l = str(solver)
        self.assertEqual(l, result.strip('\n'))
    return test

def add_single_solve_test_cases(cls, lines):
    for line_construct in lines:
        line_template = line_construct['line']
        island_template = line_construct['islands']
        result = line_construct['result']
        func = make_line_test_function(line_template, island_template, result)
        func_name = 'test_' + ''.join(map_tile_name(c) for c in line_template) + 'z' + ''.join(str(i) for i in island_template)
        print('Adding', func_name)
        setattr(cls, func_name, func)