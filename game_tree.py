from game_state import DeskState
from graph import Graph


class GameTree:
    def __init__(self, move_number: int, state: DeskState = None):
        if state is None:
            initial_state = DeskState(True)
        else:
            initial_state = DeskState(False, True, state.depth, state.next_cell_state.get_opposite(), state.matrix, passed_last_move=state.passed_last_move)

        self.move_number = move_number
        self.nodes = []
        self.graph = Graph()
        self.count_on_level = [0] * (move_number + 1)
        self.root_index = self.__build(initial_state)

    def __build(self, state: DeskState):
        children_indexes = []

        following_states, passed_last_move = state.get_following_states()
        if passed_last_move and len(following_states) == 0:
            return -1
        elif state.depth < self.move_number:
            for following_state in following_states:
                if following_state in self.nodes:
                    children_indexes.append(self.nodes.index(following_state))
                else:
                    child_index = self.__build(following_state)
                    children_indexes.append(child_index)

        self.count_on_level[state.depth] += 1

        state_index = len(self.nodes)
        self.nodes.append(state)

        for child_node_index in children_indexes:
            if child_node_index >= 0:
                self.graph.insert_node(state_index, child_node_index)

        return state_index

    def get_max_count_on_level(self):
        max_count = 0
        for count in self.count_on_level:
            if count > max_count:
                max_count = count
        return max_count
