import json

TYPE_ACROSS = 0
TYPE_DOWN = 1

SQ_EMPTY = ' '
SQ_FILLED = '*'
SQ_MARKED = 'X'

class IllFormedNgramException(Exception): pass

def format_row(row):
    print('[%s]' % '|'.join(row))

def format_col(col):
    for val in col:
        print('[%s]' % val)
    print('\n')

def rshift(arr, s, e, shift_by):
    blocks_to_shift = e-s+1
    for i in range(0, shift_by):
        arr2 = list(arr)
        for j in reversed(range(blocks_to_shift)):
            fr = s+j
            to = fr+i+1
            arr2[to] = arr2[fr]
            arr2[fr] = SQ_EMPTY
        format_row(arr2)

#test_arr = ['X', 'X', 'X', ' ', 'X', ' ', 'X', 'X', ' ', ' ']
#rshift(test_arr, 6, 7, 2)
#rshift(test_arr, 4, 7, 2)
#rshift(test_arr, 0, 7, 2)

class PossibleStates(object):
    def __init__(self, length, arr_values, typ):
        self.arr_values = arr_values
        self.length = length
        self.typ = typ

        self.create_starter_arr()
        '''
        if self.typ == TYPE_ACROSS:
            format_row(self.starter_arr)
        else:
            format_col(self.starter_arr)
        '''
        self.gen_rshifted_arrays()

    def is_solved(self, arr):
        return SQ_EMPTY in arr

    def gen_rshifted_arrays(self):
        start_indexes = []
        end_indexes = []
        for i in range(len(self.arr_values)):
            if i == 0:
                start_indexes.append(0)
                end_indexes.append(self.arr_values[0]-1)
            else:
                s_index = sum(self.arr_values[0:i])+i
                e_index = s_index+self.arr_values[i]-1
                start_indexes.append(s_index)
                end_indexes.append(e_index)
        #print(start_indexes, end_indexes)
        shift_by = self.arr_values[-1]
        e = end_indexes[-1]
        for i in reversed(range(len(start_indexes))):
            s = start_indexes[i]
            #rshift(self.starter_arr, s, e, shift_by)

    def create_starter_arr(self):
        self.starter_arr = [SQ_EMPTY]*self.length
        curr_arr_index = 0
        if len(self.arr_values) == 0:
            self.starter_arr = [SQ_MARKED]*self.length
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
        self.across_arr_values = across
        self.down_arr_values = down
        for arr_values in self.across_arr_values:
            PossibleStates(len(across), arr_values, TYPE_ACROSS)
        for arr_values in self.down_arr_values:
            PossibleStates(len(down), arr_values, TYPE_DOWN)

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
    Nonogram.from_json_file('puzzle1.json')
