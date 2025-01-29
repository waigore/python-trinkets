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

    def prune_possible_states(self, states):
        for state in states:
            self._possible_states.remove(state)

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