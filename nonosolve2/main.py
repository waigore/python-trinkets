from tests.testutil import add_single_solve_test_cases, E, F, C, I, map_creator, map_tile_name
import tests.lines_15x15

from nsolve.board import TileType, NonogramIsland
from nsolve.line import LineSolver


def test(line_template, island_template):
        line = [map_creator(t)() for t in line_template]
        solver = LineSolver.from_line(line=line, islands=[I(v) for v in island_template])

        solver.solve()
        l = str(solver)
        print(l)

if __name__ == '__main__':
    lines = tests.lines_15x15.lines
    l = lines[2]
    test(l['line'], l['islands'])