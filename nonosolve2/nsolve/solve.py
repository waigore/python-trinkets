from .line import LineOrientation, LineSolver

class NonogramSolver(object):
    def __init__(self, board):
        self._board = board

        self._init_line_solvers()

    def _init_line_solvers(self):
        self._across_solvers = [LineSolver.from_board(self._board, line_orientation=LineOrientation.ACROSS, location=i) for i in range(self._board.down)]
        self._down_solvers= [LineSolver.from_board(self._board, line_orientation=LineOrientation.DOWN, location=i) for i in range(self._board.across)]
        self._all_solvers = self._across_solvers + self._down_solvers
        
        for line_solver in self._all_solvers:
            line_solver.update_from_board(self._board)
        
    def solve(self):
        iter_counter = 0
        while not self.solved:
            dirty_line_solvers = [line_solver for line_solver in self._all_solvers if line_solver.dirty and not line_solver.solved]
            dirty_line_solvers.sort(key=lambda s: s.update_count + s.expected_fill_count - s.actual_fill_count, reverse=True)

            for line_solver in dirty_line_solvers:
                postable = line_solver.solve()
                if postable:
                    posts = line_solver.post_to_board(self._board)
                    iter_counter += 1
                    yield iter_counter, line_solver
                    for post in posts:
                        u = post[0] if line_solver.line_orientation == LineOrientation.ACROSS else post[1]
                        to_update = [s for s in self._all_solvers if s.line_orientation != line_solver.line_orientation and s.location == u]
                        for s in to_update:
                            s.update_from_board(self._board)
        return iter_counter, None

    def solve_no_steps(self):
        [_ for _ in self.solve()]
        return

    @staticmethod
    def from_board(board):
        return NonogramSolver(board)
    
    @property
    def solved(self):
        return self._board.empty_count == 0