import json

TYPE_ACROSS = 0
TYPE_DOWN = 1

SQ_EMPTY = ' '
SQ_FILLED = '*'
SQ_MARKED = 'X'

SUG_MARK = 'MARK'
SUG_FILL = 'FILL'
SUG_UNK = 'UNK'

class IllFormedNgramException(Exception): pass

def format_row(row):
    print ('[%s]' % '|'.join(row))

def format_col(col):
    for val in col:
        print('[%s]' % val)
    print('\n')

def rshift(arr, s, e, shift_by):
    blocks_to_shift = e-s+1
    new_arrs = []
    for i in range(0, shift_by):
        arr2 = list(arr)
        for j in reversed(range(blocks_to_shift)):
            fr = s+j
            to = fr+i+1
            arr2[to] = arr2[fr]
            arr2[fr] = SQ_EMPTY
        #format_row(arr2)
        new_arrs.append(tuple(arr2))
    return new_arrs

#test_arr = ['X', 'X', 'X', ' ', 'X', ' ', 'X', 'X', ' ', ' ']
#rshift(test_arr, 6, 7, 2)
#rshift(test_arr, 4, 7, 2)
#rshift(test_arr, 0, 7, 2)

class PossibleStates(object):
    def __init__(self, length, arr_values, typ):
        self.arr_values = arr_values
        self.length = length
        self.typ = typ
        self.states = []

        self.create_starter_arr()
        self.gen_rshifted_arrays()

        '''
        print("Row/Col:", self.starter_arr)
        for state in self.states:
            if self.typ == TYPE_ACROSS:
                format_row(state)
            else:
                format_col(state)
        '''

    def get_all_squares(self, index):
        return tuple(state[index] for state in self.states)

    def get_sq_suggestion(self, index):
        all_empty = not any(sq == SQ_FILLED for sq in self.get_all_squares(index))
        all_filled = not any(sq == SQ_EMPTY for sq in self.get_all_squares(index))
        if all_empty:
            return SUG_MARK
        elif all_filled:
            return SUG_FILL
        else:
            return SUG_UNK

    def is_arr_solved(self, arr):
        return SQ_EMPTY in arr

    def gen_rshifted_arrays(self):
        start_indexes = []
        end_indexes = []

        self.states.append(tuple(self.starter_arr))
        #self.arr_values == 0 ?
        if len(self.arr_values) == 0:
            return

        for i in range(len(self.arr_values)):
            if i == 0:
                start_indexes.append(0)
                end_indexes.append(self.arr_values[0]-1)
            else:
                s_index = sum(self.arr_values[0:i])+i
                e_index = s_index+self.arr_values[i]-1
                start_indexes.append(s_index)
                end_indexes.append(e_index)

        e = end_indexes[-1]
        shift_by = len(self.starter_arr)-e-1
        #shift_by == 0?
        if shift_by <= 0:
            return
        #print("starter_arr:", self.starter_arr)
        for i in reversed(range(len(start_indexes))):
            s = start_indexes[i]
            #print("s:", s, "e:", e, "shift_by:", shift_by)
            new_arrs = rshift(self.starter_arr, s, e, shift_by)
            self.states.extend(new_arrs)

    def create_starter_arr(self):
        self.starter_arr = [SQ_EMPTY]*self.length
        curr_arr_index = 0
        if len(self.arr_values) == 0:
            #self.starter_arr = [SQ_MARKED]*self.length
            return

        for i in range(len(self.starter_arr)):
            smaller =  i < sum(self.arr_values[0:curr_arr_index+1])+curr_arr_index
            if smaller:
                self.starter_arr[i] = SQ_FILLED
            else:
                self.starter_arr[i] = SQ_EMPTY
                curr_arr_index += 1
        #print(self.starter_arr)


class Nonogram(object):
    def __init__(self, across, down):
        self.across = across
        self.down = down
        self.board = [[SQ_EMPTY for j in range(len(down))] for i in range(len(across))]
        self.row_states = [None]*len(across)
        self.col_states = [None]*len(down)

        for i, arr_values in enumerate(self.across):
            self.row_states[i] = PossibleStates(len(across), arr_values, TYPE_ACROSS)
        for i, arr_values in enumerate(self.down):
            self.col_states[i] = PossibleStates(len(down), arr_values, TYPE_DOWN)

    def __str__(self):
        s = []
        for row in self.board:
            row_s = '[%s]' % '|'.join(row)
            s.append(row_s)
        return '\n'.join(s)

    def mark_board(self):
        numrows = len(self.across)
        numcols = len(self.down)
        for i in range(numrows):
            row_state = self.row_states[i]
            for j in range(numcols):
                sug = row_state.get_sq_suggestion(j)
                if sug == SUG_FILL:
                    self.board[i][j] = SQ_FILLED
                elif sug == SUG_MARK:
                    self.board[i][j] = SQ_MARKED
                else:
                    continue
        for i in range(numcols):
            col_state = self.col_states[i]
            for j in range(numrows):
                sug = col_state.get_sq_suggestion(j)
                if sug == SUG_FILL:
                    self.board[j][i] = SQ_FILLED
                elif sug == SUG_MARK:
                    self.board[j][i] = SQ_MARKED

    @classmethod
    def from_json_file(cls, fname):
        with open(fname, 'r') as json_data:
            d = json.load(json_data)
            for arg in ('width', 'height', 'across', 'down'):
                if arg not in d:
                    raise IllFormedNgramException("'%s' not found" % arg)

            width, height = d['width'], d['height']
            across, down = d['across'], d['down']
            if len(across) != height:
                raise IllFormedNgramException("'across' does not match height: %d" % height)
            if len(down) != width:
                raise IllFormedNgramException("'down' does not match width: %d" % width)
            obj = cls(across, down)
            return obj

if __name__ == '__main__':
    n = Nonogram.from_json_file('puzzle1.json')
    n.mark_board()
    print(n)
