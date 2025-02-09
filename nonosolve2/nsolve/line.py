from enum import Enum

from .lineisland import LineIsland
from .lineutil import generate_pstate_combi
from .board import TileType

class LineOrientation(Enum):
    ACROSS = 1
    DOWN = 2

    def pretty(self):
        if self == LineOrientation.ACROSS:
            s = 'across'
        else:
            s = 'down'
        return s

class LineSolver(object):
    def __init__(self, board=None, line_orientation=LineOrientation.ACROSS, location=None, line=None, islands=None):
        self._board = board
        self.line_orientation = line_orientation
        self.location = location
        self._update_count = 0
        self._post_count = 0
        self._constraint_zone_change_count = 0

        if line:
            self._dimen = len(line)
            self._line = line
        else:
            if self.line_orientation == LineOrientation.ACROSS:
                self._dimen = self._board.across
                islands = self._board.down_islands[self.location]
            elif self.line_orientation == LineOrientation.DOWN:
                self._dimen = self._board.down
                islands = self._board.across_islands[self.location]
            else:
                raise ValueError("Unknown line orientation: " + self.line_orientation)
            
            self.update_from_board(self._board)

        self._line_islands = self._create_line_islands(islands)
        for island in self._line_islands:
            island.init() #ask each island to calculate its constraint zones and generate possible states
        
        self._generate_line_possible_states()
    
    @staticmethod
    def from_board(board, line_orientation, location):
        return LineSolver(board=board, line_orientation=line_orientation, location=location)

    @staticmethod
    def from_line(line, islands):
        return LineSolver(line=line, islands=islands)

    def update_from_board(self, board):
        self._line = self._create_line_from_board(board)
        self._update_count += 1
    
    def post_to_board(self, board):
        posts = []
        for i, t in enumerate(self._line):
            if self.line_orientation == LineOrientation.ACROSS:
                x, y = i, self.location
            else:
                x, y = self.location, i

            orig_tile = board[x, y]
            if orig_tile == TileType.EMPTY and t != TileType.EMPTY:
                board[x, y] = t
                posts.append((x, y))
        
        self._post_count = 0
        return posts 

    def _create_line_from_board(self, board):
        line = []
        for i in range(self._dimen):
            if self.line_orientation == LineOrientation.ACROSS:
                x, y = i, self.location
            else:
                x, y = self.location, i
            line.append(board[x, y])
        return line

    def _create_line_islands(self, islands):
        return [LineIsland(solver=self, island=island, position=i, dimen=self._dimen) for i, island in enumerate(islands)]

    def get_islands_before(self, position):
        return self._line_islands[:position]
    
    def get_islands_after(self, position):
        return self._line_islands[position+1:]
    
    def _generate_line_possible_states(self):
        pstate_matrix = [i.possible_states for i in self._line_islands]
        line_pstate_combis = generate_pstate_combi(pstate_matrix)
        invalid_line_pstates = []
        
        for line_pstate, island_blocks in line_pstate_combis.items():
            if not self.line_pstate_valid(line_pstate, island_blocks):
                invalid_line_pstates.append(line_pstate)
                continue
            for i, island_block in enumerate(island_blocks):
                line_island = self._line_islands[i]
                line_island.link_line_possible_state(island_block, line_pstate)
        
        for ip in invalid_line_pstates:
            line_pstate_combis.pop(ip, None)

        self.line_pstate_map = line_pstate_combis #(3, 4, 6, 7, 8, 9, 10, 13, 14) -> [(3,), (4,), (6, 7, 8, 9, 10), (13, 14)]

    def prune_line_possible_states(self):
        inconsistent_line_pstates = []
        for line_pstate, island_blocks in self.line_pstate_map.items():
            if self.line_pstate_consistent_with_board(line_pstate):
                continue
            inconsistent_line_pstates.append(line_pstate)
            for i, island_block in enumerate(island_blocks):
                line_island = self._line_islands[i]
                line_island.prune_line_possible_state(island_block, line_pstate)
        
        for bp in inconsistent_line_pstates:
            self.line_pstate_map.pop(bp, None)

    def line_pstate_blocked(self, line_pstate):
        return any(self._line[coord] == TileType.CROSSED for coord in line_pstate)

    def line_pstate_valid(self, line_pstate, island_blocks):       
        unique_fills = set(line_pstate)
        if len(unique_fills) != len(line_pstate):
            return False
        
        for i, island_block in enumerate(island_blocks):
            if i == len(island_blocks) - 1:
                continue
            last_filled = island_block[-1]
            next_filled = island_blocks[i+1][0]
            if next_filled - last_filled < 2:
                return False
        
        return True

    def line_pstate_consistent_with_board(self, line_pstate):
        if self.line_pstate_blocked(line_pstate):
            return False
        
        hypothetical_line = list(self._line)
        for coord in line_pstate:
            hypothetical_line[coord] = TileType.FILLED
        
        actual_fills = len([t for t in hypothetical_line if t == TileType.FILLED])
        expected_fills = self.expected_fill_count
        if actual_fills != expected_fills:
            return False
        
        return True

    def solve(self):
        self.prune_line_possible_states()
        self._constraint_zone_change_count = 0
        self._post_count = 0
        for island in self._line_islands:
            self._constraint_zone_change_count += island.recalc_constraint_zone()
        
        for i, t in enumerate(self._line):
            if t != TileType.EMPTY:
                continue
            claims = tuple(island for island in self._line_islands if island.claims(i))
            if len(claims) == 0:
                self._line[i] = TileType.CROSSED
                self._post_count += 1
            elif len(claims) == 1 and claims[0].fillable(i):
                self._line[i] = TileType.FILLED
                self._post_count += 1

        self._update_count = 0
        return self.post_count > 0

    @property
    def solved(self):
        return not any(t for t in self._line if t == TileType.EMPTY)

    @property
    def constraint_zone_change_count(self):
        return self._constraint_zone_change_count
    
    @property
    def post_count(self):
        return self._post_count

    @property
    def update_count(self):
        return self._update_count
    
    @property
    def expected_fill_count(self):
        return sum(i.value for i in self._line_islands)

    @property
    def actual_fill_count(self):
        return len([t for t in self._line if t == TileType.FILLED])

    @property
    def dirty(self):
        return self._update_count > 0

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