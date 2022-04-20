from enum import Enum


class Step:
    def __init__(self, plus_x, plus_y):
        self.x = plus_x
        self.y = plus_y


class Direction(Enum):
    LEFT = Step(-1, 0)
    RIGHT = Step(1, 0)
    UP = Step(0, -1)
    DOWN = Step(0, 1)
    LEFT_UP = Step(-1, -1)
    RIGHT_UP = Step(1, -1)
    LEFT_DOWN = Step(-1, 1)
    RIGHT_DOWN = Step(1, 1)


class CellCoord:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def is_valid(self):
        return 0 <= self.x < 4 and 0 <= self.y < 4

    def __eq__(self, other):
        if isinstance(other, CellCoord):
            return self.x == other.x and self.y == other.y
        return False


class CellState(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2

    def __str__(self):
        if self == CellState.EMPTY:
            return 'E'
        elif self == CellState.BLACK:
            return 'B'
        else:
            return 'W'

    def get_opposite(self):
        if self == CellState.BLACK:
            return CellState.WHITE
        else:
            return CellState.BLACK


class DeskState:
    def __init__(
            self,
            is_initial_state: bool,
            is_root: bool = None,
            parent_depth: int = None,
            new_cell_state: CellState = None,
            prev_state_matrix: list[list[CellState]] = None,
            cell_coord: CellCoord = None,
            directions: list[Direction] = None,
            passed_last_move: bool = None
    ):
        self.matrix = [[CellState.EMPTY] * 4 for i in range(4)]

        self.passed_last_move = False

        if is_initial_state:
            self.depth = 0
            self.matrix[1][1] = CellState.BLACK
            self.matrix[2][2] = CellState.BLACK
            self.matrix[1][2] = CellState.WHITE
            self.matrix[2][1] = CellState.WHITE

            self.next_cell_state = CellState.BLACK
            self.last_cell_state = CellState.WHITE
        else:
            if is_root:
                self.depth = 0
            else:
                self.depth = parent_depth + 1

            for i in range(4):
                for j in range(4):
                    self.matrix[i][j] = prev_state_matrix[i][j]

            if new_cell_state is not None and cell_coord is not None and directions is not None:
                self.seize_lines(cell_coord, new_cell_state, directions)
            elif passed_last_move is not None:
                self.passed_last_move = passed_last_move
            elif not is_root:
                self.passed_last_move = True

            self.last_cell_state = new_cell_state
            self.next_cell_state = new_cell_state.get_opposite()

    def seize_lines(self, cell_coord: CellCoord, new_cell_state: CellState, directions: list[Direction]):
        self.matrix[cell_coord.y][cell_coord.x] = new_cell_state
        for direction in directions:
            step = direction.value
            current_cell_coord = CellCoord(cell_coord.x + step.x, cell_coord.y + step.y)
            while self.matrix[current_cell_coord.y][current_cell_coord.x] != new_cell_state:
                self.matrix[current_cell_coord.y][current_cell_coord.x] = new_cell_state
                current_cell_coord.x += step.x
                current_cell_coord.y += step.y

    def get_following_states(self):
        following_states = []
        for i in range(4):
            for j in range(4):
                cell_coord = CellCoord(j, i)
                directions = self.__get_directions(cell_coord)
                if len(directions) > 0:
                    following_state = DeskState(False, False, self.depth, self.next_cell_state, self.matrix, cell_coord, directions)
                    following_states.append(following_state)

        # Пропуск хода
        if len(following_states) == 0 and not self.passed_last_move:
            following_states = [DeskState(False, False, self.depth, self.next_cell_state, self.matrix)]

        return following_states, self.passed_last_move

    def get_allowed_cells(self):
        allowed_cells_and_directories = []
        for i in range(4):
            for j in range(4):
                cell_coord = CellCoord(j, i)
                directions = self.__get_directions(cell_coord)
                if len(directions) > 0:
                    allowed = (cell_coord, directions)
                    allowed_cells_and_directories.append(allowed)
        return allowed_cells_and_directories

    def get_cell_state_distribution(self):
        black_count = 0
        white_count = 0
        for row in self.matrix:
            for el in row:
                if el == CellState.BLACK:
                    black_count += 1
                elif el == CellState.WHITE:
                    white_count += 1
        empty_count = 16 - black_count - white_count
        return black_count, white_count, empty_count

    def __get_directions(self, cell_coord: CellCoord):
        if self.matrix[cell_coord.y][cell_coord.x] == CellState.EMPTY:
            directions = []

            left = self.__has_closing(cell_coord, Direction.LEFT.value)
            if left:
                directions.append(Direction.LEFT)

            right = self.__has_closing(cell_coord, Direction.RIGHT.value)
            if right:
                directions.append(Direction.RIGHT)

            up = self.__has_closing(cell_coord, Direction.UP.value)
            if up:
                directions.append(Direction.UP)

            down = self.__has_closing(cell_coord, Direction.DOWN.value)
            if down:
                directions.append(Direction.DOWN)

            left_up = self.__has_closing(cell_coord, Direction.LEFT_UP.value)
            if left_up:
                directions.append(Direction.LEFT_UP)

            right_up = self.__has_closing(cell_coord, Direction.RIGHT_UP.value)
            if right_up:
                directions.append(Direction.RIGHT_UP)

            left_down = self.__has_closing(cell_coord, Direction.LEFT_DOWN.value)
            if left_down:
                directions.append(Direction.LEFT_DOWN)

            right_down = self.__has_closing(cell_coord, Direction.RIGHT_DOWN.value)
            if right_down:
                directions.append(Direction.RIGHT_DOWN)

            return directions
        else:
            return []

    def __has_closing(self, cell_coord: CellCoord, step: Step):
        current_cell_coord = CellCoord(cell_coord.x + step.x, cell_coord.y + step.y)
        if current_cell_coord.is_valid() and self.matrix[current_cell_coord.y][current_cell_coord.x] == self.last_cell_state:
            current_cell_coord.x += step.x
            current_cell_coord.y += step.y
            while current_cell_coord.is_valid() and self.matrix[current_cell_coord.y][current_cell_coord.x] == self.last_cell_state:
                current_cell_coord.x += step.x
                current_cell_coord.y += step.y
            if current_cell_coord.is_valid() and self.matrix[current_cell_coord.y][current_cell_coord.x] == self.next_cell_state:
                return True
            else:
                return False

    def print(self):
        for row in self.matrix:
            print(' '.join(map(lambda x: str(x), row)))

    def __eq__(self, other):
        if isinstance(other, DeskState):
            return self.matrix == other.matrix and self.next_cell_state == other.next_cell_state
        return False
