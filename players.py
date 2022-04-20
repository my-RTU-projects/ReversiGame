import random
from enum import Enum
from game_tree import GameTree
from game_state import CellState, DeskState


class PlayerType(Enum):
    ALPHA_BETA_BOT = 1
    PERSON = 2


class Player:
    def __init__(self, applied_cell_state: CellState, player_type: PlayerType):
        self.applied_cell_state = applied_cell_state
        self.player_type = player_type


class AlphaBetaPlayer(Player):
    def __init__(self, applied_cell_state: CellState, estimated_depth: int):
        super(AlphaBetaPlayer, self).__init__(applied_cell_state, PlayerType.ALPHA_BETA_BOT)
        self.estimated_depth = estimated_depth
        self.tree = None
        self.player_choice = None
        self.estimates = [None]

    def retry(self):
        self.tree = None
        self.player_choice = None
        self.estimates = [None]

    def choose_next(self, current_state: DeskState):
        self.tree = GameTree(self.estimated_depth, current_state)
        self.estimates = [None] * len(self.tree.nodes)
        self.estimate_state(self.tree.root_index, float('-inf'), float('inf'))
        best = self.__get_best()
        self.player_choice = best
        if best is not None:
            return self.tree.nodes[best]
        else:
            return None

    def estimate_state(self, state_index, alpha, beta):
        related_states = self.tree.graph.get_related_nodes(state_index)

        if len(related_states) == 0:
            black_count, white_count, empty_count = self.tree.nodes[state_index].get_cell_state_distribution()

            if self.applied_cell_state == CellState.BLACK:
                estimate = black_count - white_count
            else:
                estimate = white_count - black_count
            self.estimates[state_index] = estimate
            return estimate

        if self.tree.nodes[state_index].next_cell_state == self.applied_cell_state:
            estimate = float('-inf')
            for related_state_index in related_states:
                related_state_estimate = self.estimate_state(related_state_index, alpha, beta)
                estimate = max(estimate, related_state_estimate)
                alpha = max(alpha, estimate)
                if beta <= alpha:
                    break
        else:
            estimate = float('inf')
            for related_state_index in related_states:
                related_state_estimate = self.estimate_state(related_state_index, alpha, beta)
                estimate = min(estimate, related_state_estimate)
                beta = min(beta, estimate)
                if beta <= alpha:
                    break

        self.estimates[state_index] = estimate
        return estimate

    def __get_best(self):
        related_nodes = self.tree.graph.get_related_nodes(self.tree.root_index)
        max_array = []
        maximal = -128
        for node_index in related_nodes:
            node_estimate = self.estimates[node_index]
            if node_estimate > maximal:
                max_array.clear()
                maximal = node_estimate
            if node_estimate == maximal:
                max_array.append(node_index)

        if len(max_array) > 0:
            return random.choice(max_array)
        else:
            return None


class DecisionPlayer(Player):
    def __init__(self, applied_cell_state: CellState, get_decision):
        super(DecisionPlayer, self).__init__(applied_cell_state, PlayerType.PERSON)
        self.get_decision = get_decision

    def retry(self):
        pass

    def choose_next(self, current_state: DeskState):
        if current_state is None:
            return None

        decision = self.get_decision()
        if decision is None:
            return DeskState(
                False,
                False,
                current_state.depth,
                current_state.next_cell_state,
                current_state.matrix
            )
        cell_coord, directions = decision

        return DeskState(
            False,
            False,
            current_state.depth,
            current_state.next_cell_state,
            current_state.matrix,
            cell_coord,
            directions
        )
