from enum import Enum
from functools import reduce

from .board import TileType

class LineOrientation(Enum):
    ACROSS = 1
    DOWN = 2

class LineIsland(object):
    def __init__(self, solver, island, position, dimen):
        self._island = island
        self._solver = solver
        self.position = position
        self.dimen = dimen
    
    def init(self):
        self._islands_left = self._solver.get_islands_before(self.position)
        self._islands_right = self._solver.get_islands_after(self.position)

        self._possible_states = []
        self._init_constraint_zone()

    def _init_constraint_zone(self):
        def add_island_min_space(c, i):
            return c + i.value + 1

        def sub_island_min_space(c, i):
            return c - (i.value + 1)

        leftmost_pos = reduce(add_island_min_space, self._islands_left, 0)
        rightmost_pos = reduce(sub_island_min_space, self._islands_right, self.dimen-1)
        self._constraint_zone = tuple(range(leftmost_pos, rightmost_pos+1)) #inclusive

    def generate_possible_states(self):
        self._possible_states = []
        for start_pos in self._constraint_zone:
            state = tuple(range(start_pos, start_pos + self.value))
            if any (p not in self._constraint_zone for p in state):
                continue
            if not self._solver.island_state_valid(self.position, state):
                continue
            self._possible_states.append(state)
    
    def recalc_constraint_zone(self):
        def claimable(pos):
            return any(pos in possible_state for possible_state in self._possible_states)

        new_constraint_zone = tuple(pos for pos in self._constraint_zone if claimable(pos))
        self._constraint_zone = new_constraint_zone
    
    def claims(self, pos):
        return pos in self._constraint_zone
    
    def fillable(self, pos):
        return all(pos in possible_state for possible_state in self._possible_states)
    
    def solved(self):
        return len(self._possible_states) == 1

    @property
    def value(self):
        return self._island.value

    @property
    def typ(self):
        return self._island.typ

    @property
    def location(self):
        return self._island.location
    
    def pretty(self, include_solved=False):
        if include_solved:
            s = self.solved()
            return '[' + str(self.value) + ']' if s else str(self.value)
        return f'{self.value}'

class LineSolver(object):
    def __init__(self, board, line_orientation, location):
        self._board = board
        self.line_orientation = line_orientation
        self.location = location
        self._dirty = True
        
        self._init()

    def _init(self):
        if self.line_orientation == LineOrientation.ACROSS:
            self._dimen = self._board.across
            islands = self._board.down_islands[self.location]
        else:
            self._dimen = self._board.down
            islands = self._board.across_islands[self.location]

        self._init_line()
        self._init_line_islands(islands)
    
    def _init_line(self):
        self._line = []
        for i in range(self._dimen):
            if self.line_orientation == LineOrientation.ACROSS:
                x, y = i, self.location
            else:
                x, y = self.location, i
            self._line.append(self._board[x, y])
    
    def _init_line_islands(self, islands):
        self._line_islands = [LineIsland(solver=self, island=island, position=i, dimen=self._dimen) for i, island in enumerate(islands)]
        for island in self._line_islands:
            island.init()

    def get_islands_before(self, position):
        return self._line_islands[:position]
    
    def get_islands_after(self, position):
        return self._line_islands[position+1:]

    def island_state_valid(self, island_pos, state): #tuple of island values
        hypothetical_line = list(self._line)
        for coord in state:
            t = self._line[coord]
            if t == TileType.CROSSED:
                return False
            hypothetical_line[coord] = TileType.FILLED

        if not self._line_filled_count_consistent(hypothetical_line):
            return False

        filled_islands = self._extract_filled_islands(hypothetical_line)
        for filled_island in filled_islands:
            if any(tile in state for tile in filled_island) and len(filled_island) > len(state):
                return False

        return True

    def _line_filled_count_consistent(self, line):
        expected_filled_cnt = sum(i.value for i in self._line_islands)
        actual_filled_cnt = line.count(TileType.FILLED)
        return actual_filled_cnt <= expected_filled_cnt

    def _extract_filled_islands(self, line):
        filled_islands = []
        is_island = False
        curr_island = []
        for i, t in enumerate(line):
            if t == TileType.FILLED:
                if not is_island:
                    is_island = True
                curr_island.append(i)
            else:
                is_island = False
                if curr_island:
                    filled_islands.append(curr_island)
                    curr_island = []
        if curr_island:
            filled_islands.append(curr_island)
        return filled_islands

    def solve(self):
        self._init_line()

        for island in self._line_islands:
            island.generate_possible_states()
            island.recalc_constraint_zone()
        
        for i, t in enumerate(self._line):
            if t != TileType.EMPTY:
                continue
            claims = tuple(island for island in self._line_islands if island.claims(i))
            if len(claims) == 0:
                self._line[i] = TileType.CROSSED
            elif len(claims) == 1 and claims[0].fillable(i):
                self._line[i] = TileType.FILLED
            
        self._dirty = False

    @property
    def dirty(self):
        return self._dirty

    def __repr__(self):
        l = self._print_line_with_islands()
        j = self._print_island_constraint_zones()
        if j:
            l = l + '\n' + j
        return l

    def _print_line_with_islands(self):
        row = '|' + '|'.join([t.pretty() for t in self._line]) + '|'
        islands_str = ' '.join(i.pretty(include_solved=True) for i in self._line_islands)
        if islands_str:
            row = row + ' ' + islands_str
        if self.dirty:
            row = row + ' *'
        return row
    
    def _print_island_constraint_zones(self):
        s = []
        for island in self._line_islands:
            r = ' ' + ' '.join(['* ' if island.claims(pos) else '  ' for pos, t in enumerate(self._line)]) + '  ' + island.pretty()
            s.append(r)
        return '\n'.join(s)