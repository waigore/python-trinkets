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
    return ('[%s]' % '|'.join(row))

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

def gen_start_end_indexes(starter_arr, fr, to):
    s_indexes = []
    e_indexes = []
    in_filled = False
    for i in range(fr, to+1):
        sq = starter_arr[i]
        in_filled = sq == SQ_FILLED
        if in_filled and len(s_indexes) == len(e_indexes):
            s_indexes.append(i)
        if not in_filled and len(s_indexes) > len(e_indexes):
            e_indexes.append(i-1)
    if len(s_indexes) > len(e_indexes):
        e_indexes.append(to)
    return s_indexes, e_indexes

'''
test_arr = ['*', ' ', '*', ' ', '*', ' ', ' ', ' ', ' ', ' ']
print(gen_start_end_indexes(test_arr, 0, 4))
print(gen_start_end_indexes(test_arr, 0, 9))
print(gen_start_end_indexes(test_arr, 0, 2))

test_arr = ['*', ' ', '*', '*', '*', ' ', ' ', ' ', ' ', ' ']
print(gen_start_end_indexes(test_arr, 0, 4))
print(gen_start_end_indexes(test_arr, 0, 9))

test_arr = [' ', '*', '*', '*', ' ', '*', '*', ' ', '*', ' ']
print(gen_start_end_indexes(test_arr, 0, 9))
'''

def gen_all_states(starter_arr, range_start, range_end):
    start_indexes, end_indexes = gen_start_end_indexes(starter_arr, 0, range_start-1)
    #print("starter_arr:", format_row(starter_arr), "s_i:", start_indexes, "e_i:", end_indexes, "r_start:", range_start, "r_end:", range_end)
    shift_by = range_end - range_start + 1
    if shift_by <= 0:
        return []

    e = end_indexes[-1]
    new_states = []
    #print("starter_arr:", self.starter_arr)
    for i in reversed(range(len(start_indexes))):
        s = start_indexes[i]
        #print("s:", s, "e:", e, "shift_by:", shift_by)
        new_arrs = rshift(starter_arr, s, e, shift_by)

        #print("\tgenerated:")
        #for new_arr in new_arrs:
        #    print("\t%s" % format_row(new_arr))
        new_states.extend(new_arrs)

        if i <= 0:
            continue

        new_range_start = start_indexes[i]-1
        for j in range(shift_by):
            new_arr = new_arrs[j]
            new_range_end = new_range_start+j
            #print("Recursing:", format_row(new_arr), start_indexes, 'new_range_start:', new_range_start, 'new_range_end:', new_range_end)
            new_states.extend(gen_all_states(new_arr, new_range_start, new_range_end))
            #for k in range(len(new_start_indexes)):

    return new_states



#test_arr = ['X', 'X', 'X', ' ', 'X', ' ', 'X', 'X', ' ', ' ']
#rshift(test_arr, 6, 7, 2)
#rshift(test_arr, 4, 7, 2)
#rshift(test_arr, 0, 7, 2)

#test_arr = ['*', ' ', '*', ' ', '*', ' ', ' ', ' ', ' ', ' ']
#states = list(set(gen_all_states(test_arr, 5, 9)))
#test_arr = ['*', '*', '*', ' ', '*', ' ', ' ', ' ', ' ', ' ']
#states = list(set(gen_all_states(test_arr, 5, 9)))
#states.sort(reverse=True)
#for state in states:
#    print(format_row(state))

#print(rshift(test_arr, 4, 4, 5))
#print(rshift(test_arr, 0, 4, 5))

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

        '''
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
        '''
        r_start = end_indexes[-1]+1
        r_end = len(self.starter_arr)-1
        arrs = list(set(gen_all_states(self.starter_arr, r_start, r_end)))
        arrs.sort(reverse=True)
        self.states.extend(arrs)

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

    def solve(self):
        i = 1
        while not self.is_solved():
            #print("=====Iteration %d=====" % i)
            i+=1
            self.mark_board()
            #print(self)
            self.purge_states()
            #print(self)
            #print()

    def is_solved(self):
        numrows = len(self.across)
        numcols = len(self.down)
        for i in range(numrows):
            for j in range(numcols):
                if self.board[i][j] == SQ_EMPTY:
                    return False
        return True

    def purge_states(self):
        numrows = len(self.across)
        numcols = len(self.down)
        for i in range(numrows):
            row_state = self.row_states[i]
            #print('Possible states for row (!!!):', i, [format_row(r) for r in row_state.states])
            states_to_delete = []
            for state in row_state.states:
                to_delete = False
                for j in range(len(state)):
                    state_sq = state[j]
                    board_sq = self.board[i][j]
                    if (state_sq == SQ_FILLED and board_sq == SQ_MARKED) or \
                      (state_sq == SQ_EMPTY and board_sq == SQ_FILLED):
                        to_delete = True
                        break
                if to_delete:
                    states_to_delete.append(state)
            #print('To delete for row:', i, states_to_delete)
            for state in states_to_delete:
                row_state.states.remove(state)
            #print('Possible states for row after deletion:', i, [format_row(r) for r in row_state.states])

        for i in range(numcols):
            col_state = self.col_states[i]
            states_to_delete = []
            for state in col_state.states:
                to_delete = False
                for j in range(len(state)):
                    state_sq = state[j]
                    board_sq = self.board[j][i]
                    if (state_sq == SQ_FILLED and board_sq == SQ_MARKED) or \
                      (state_sq == SQ_EMPTY and board_sq == SQ_FILLED):
                        to_delete = True
                        break
                if to_delete:
                    states_to_delete.append(state)
            #print('To delete for col:', i, states_to_delete)
            for state in states_to_delete:
                col_state.states.remove(state)
            #print('Possible states for col:', i, [format_row(r) for r in col_state.states])


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
    n = Nonogram.from_json_file('puzzle5.json')
    n.solve()
    print(n)
