from functools import reduce


class LineIsland(object):
    def __init__(self, solver, island, position, dimen):
        self._island = island
        self._solver = solver
        self.position = position
        self.dimen = dimen

    def init(self):
        self._islands_left = self._solver.get_islands_before(self.position)
        self._islands_right = self._solver.get_islands_after(self.position)

        self._init_constraint_zone()
        self._init_possible_states()

    def _init_constraint_zone(self):
        def add_island_min_space(c, i):
            return c + i.value + 1

        def sub_island_min_space(c, i):
            return c - (i.value + 1)

        leftmost_pos = reduce(add_island_min_space, self._islands_left, 0)
        rightmost_pos = reduce(sub_island_min_space, self._islands_right, self.dimen-1)
        self._constraint_zone = tuple(range(leftmost_pos, rightmost_pos+1)) #inclusive

    def _init_possible_states(self):
        self._possible_state_map = {}
        for start_pos in self._constraint_zone:
            state = tuple(range(start_pos, start_pos + self.value))
            if any (p not in self._constraint_zone for p in state):
                continue
            self._possible_state_map[state] = [] #(3,) -> (3, 4, 6, 7, 8, 9, 10, 13, 14)

    def link_line_possible_state(self, p_state, l_state):
        self._possible_state_map[p_state].append(l_state)
    
    def prune_line_possible_state(self, p_state, l_state):
        self._possible_state_map[p_state].remove(l_state)

    def recalc_constraint_zone(self):
        states = self.valid_states
        def claimable(pos):
            return any(pos in possible_state for possible_state in states)

        new_constraint_zone = tuple(pos for pos in self._constraint_zone if claimable(pos))
        old_len = len(self._constraint_zone)
        new_len = len(new_constraint_zone)
        self._constraint_zone = new_constraint_zone
        return old_len - new_len

    def claims(self, pos):
        return pos in self._constraint_zone

    def fillable(self, pos):
        return all(pos in possible_state for possible_state in self.valid_states)

    def solved(self):
        return len(self.valid_states) == 1

    @property
    def possible_states(self):
        return self._possible_state_map.keys()
    
    @property
    def valid_states(self):
        return [p for p, v in self._possible_state_map.items() if len(v) > 0]

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