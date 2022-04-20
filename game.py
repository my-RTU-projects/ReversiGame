from players import Player, PlayerType, AlphaBetaPlayer
from game_state import DeskState, CellState


class Game:
    def __init__(self,
                 first_player: Player,
                 second_player: Player
                 ):
        self.new_game(first_player, second_player)

    def new_game(self, first_player: Player, second_player: Player):
        self.first_player = first_player
        self.second_player = second_player
        self.prev_state = None
        self.current_state = DeskState(True)
        self.next_cell_state_to_apply = CellState.BLACK
        self.is_finished = False
        if self.is_person_next():
            self.allowed_steps_for_person = self.current_state.get_allowed_cells()
        else:
            self.allowed_steps_for_person = []

    def is_person_next(self):
        return self.next_cell_state_to_apply == CellState.BLACK and \
               self.first_player.player_type == PlayerType.PERSON or \
               self.next_cell_state_to_apply == CellState.WHITE and \
               self.second_player.player_type == PlayerType.PERSON

    def next(self):
        self.prev_state = self.current_state
        if self.next_cell_state_to_apply == CellState.BLACK:
            self.current_state = self.first_player.choose_next(self.current_state)
            self.next_cell_state_to_apply = CellState.WHITE
        else:
            self.current_state = self.second_player.choose_next(self.current_state)
            self.next_cell_state_to_apply = CellState.BLACK

        if self.current_state is None:
            self.is_finished = True
            return

        if self.is_person_next():
            self.allowed_steps_for_person = self.current_state.get_allowed_cells()
            if self.allowed_steps_for_person is None or len(self.allowed_steps_for_person) == 0:
                black_count, white_count, empty_count = self.current_state.get_cell_state_distribution()
                if empty_count == 1 or self.prev_state.matrix == self.current_state.matrix:
                    self.is_finished = True
                    return

