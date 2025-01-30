import json
import sys

from nsolve.board import NonogramBoard
from nsolve.solve import NonogramSolver

if __name__ == '__main__':
    fn = sys.argv[1]
    with open(fn) as f:
        d = json.load(f)
        across = d['across']
        down = d['down']
        dimen = (len(across), len(down))
        out_f = f'{fn}.txt'

        print(f'Loaded {fn}, dimen = {dimen}')
        print(f'Writing to {out_f}')
        
        board = NonogramBoard(dimen=dimen, islands=d)
        if not board.islands_valid():
            print('Island hints not valid, not proceeding!')
            sys.exit(1)
        
        solver = NonogramSolver.from_board(board)
        board_states = []
        for iteration, line_solver in solver.solve():
            board_state = str(board)
            board_states.append({
                'iteration': iteration,
                'board_state': board_state,
                'orientation': line_solver.line_orientation.pretty() if line_solver else '',
                'location': str(line_solver.location+1) if line_solver else '',
            })
        
        with open(out_f, 'w') as fw:
            for bs in board_states:
                iteration = bs['iteration']
                iter_str = f'Iteration #{iteration}'
                line_solver = (' (' + bs['orientation'] + ', ' + bs['location'] + ')') if bs['orientation'] else ''
                iter_str += line_solver
                sep = '-' * len(iter_str)

                fw.write(iter_str + '\n')
                fw.write(sep + '\n')
                fw.write(bs['board_state'] + '\n\n')

        iterations = board_states[-1]['iteration']
        print(f'Solved! Took {iterations} iterations')


