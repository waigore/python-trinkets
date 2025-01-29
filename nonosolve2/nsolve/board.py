from enum import Enum

class IslandType(Enum):
    ACROSS = 1
    DOWN = 2

class TileType(Enum):
    EMPTY = ' '
    FILLED = 'O'
    CROSSED = 'X'

    def pretty(self):
        return f'{self.value} '

class NonogramIsland(object):
    def __init__(self, typ, location, value):
        self.value = value
        self.typ = typ
        self.location = location
    
    def pretty(self):
        return f'{self.value}'

class NonogramBoard(object):
    def __init__(self, dimen, islands=None):
        across, down = dimen
        self.across = across
        self.down = down

        self._init_tiles()

        if not islands:
            islands = {
                'across': [[]] * across,
                'down': [[]] * down
            }
        self._init_islands(islands)
    
    def _init_tiles(self):
        self._tiles = [[TileType.EMPTY for x in range(self.across)] for y in range(self.down)]

    def _init_islands(self, islands):
        self._across_islands = [[NonogramIsland(typ=IslandType.ACROSS, location=i, value=island_value) for island_value in i_row] for i, i_row in enumerate(islands['across'])]
        self._down_islands = [[NonogramIsland(typ=IslandType.DOWN, location=i, value=island_value) for island_value in i_row] for i, i_row in enumerate(islands['down'])]

    @property
    def across_islands(self):
        return self._across_islands
    
    @property
    def down_islands(self):
        return self._down_islands
    
    @property
    def empty_count(self):
        return sum(len([t for t in self._tiles[y] if t == TileType.EMPTY]) for y in range(self.down))

    def __repr__(self):
        a = self._print_across_islands()
        b = self._print_board_with_down_islands()
        if a:
            return a + '\n' + b
        else:
            return b
    
    def _print_across_islands(self):
        max_length = max(len(a) for a in self._across_islands)
        s = []
        for i in range(max_length):
            row = ' ' + ' '.join(['  ' if i-(max_length-len(a)) < 0 else a[i-(max_length-len(a))].pretty().rjust(2, ' ') for a in self._across_islands]) + ' '
            s.append(row)
        return '\n'.join(s)

    def _print_board_with_down_islands(self):
        s = []
        for y in range(0, self.down):
            row = '|' + '|'.join([self._tiles[y][x].pretty() for x in range(self.across)]) + '|'
            down_island_str = ' '.join(i.pretty() for i in self._down_islands[y])
            if down_island_str:
                row = row + ' ' + down_island_str
            s.append(row)
        return '\n'.join(s)

    def __getitem__(self, key):
        x, y = key
        return self._tiles[y][x]
    
    def __setitem__(self, key, val):
        x, y = key
        self._tiles[y][x] = val

    def expected_fill_count(self):
        return sum([sum(i.value for i in a) for a in self._across_islands])

    def islands_valid(self):
        sum_across_islands = sum([sum(i.value for i in a) for a in self._across_islands])
        sum_down_islands = sum([sum(i.value for i in d) for d in self._down_islands])
        return sum_across_islands == sum_down_islands
    
    def mark_empty(self, key):
        x, y = key
        self._tiles[y][x] = TileType.EMPTY
    
    def mark_filled(self, key):
        x, y = key
        self._tiles[y][x] = TileType.FILLED
    
    def mark_crossed(self, key):
        x, y = key
        self._tiles[y][x] = TileType.CROSSED
