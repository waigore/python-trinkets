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
