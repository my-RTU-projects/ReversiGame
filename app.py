from tkinter import *
from tkinter import ttk
from game_state import DeskState, CellState
from game_tree import GameTree
from players import AlphaBetaPlayer, DecisionPlayer, PlayerType
from game import Game


class StateLocation:
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

    def get_out_coord(self):
        return self.x0 + (self.x1 - self.x0) / 2, self.y1

    def get_in_coord(self):
        return self.x0 + (self.x1 - self.x0) / 2, self.y0

    def get_label_coord(self):
        return self.x0 + (self.x1 - self.x0) / 2, self.y1 + 5


class InteractiveFrame(Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = Canvas(self, bg='white')
        self.canvas.bind('<MouseWheel>', self.zoom)
        self.canvas.bind('<ButtonPress-1>', self.scan_mark)
        self.canvas.bind('<B1-Motion>', self.scan_drag)
        self.canvas.pack(side=LEFT, expand=True, fill=BOTH)

    def zoom(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        factor = 1.001 ** event.delta
        self.canvas.scale(ALL, x, y, factor, factor)

    def scan_mark(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def scan_drag(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)


class StateDisplayFrame(InteractiveFrame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

    def draw_state(self, state: DeskState, r: StateLocation):
        x_diff = r.x1 - r.x0
        y_diff = r.y1 - r.y0

        x_borders = [r.x0, r.x0 + x_diff / 4, r.x0 + x_diff / 2, r.x0 + 3 * x_diff / 4, r.x1]
        y_borders = [r.y0, r.y0 + y_diff / 4, r.y0 + y_diff / 2, r.y0 + 3 * y_diff / 4, r.y1]

        self.canvas.create_line(x_borders[0], y_borders[0], x_borders[0], y_borders[4])
        self.canvas.create_line(x_borders[1], y_borders[0], x_borders[1], y_borders[4])
        self.canvas.create_line(x_borders[2], y_borders[0], x_borders[2], y_borders[4])
        self.canvas.create_line(x_borders[3], y_borders[0], x_borders[3], y_borders[4])
        self.canvas.create_line(x_borders[4], y_borders[0], x_borders[4], y_borders[4])

        self.canvas.create_line(x_borders[0], y_borders[0], x_borders[4], y_borders[0])
        self.canvas.create_line(x_borders[0], y_borders[1], x_borders[4], y_borders[1])
        self.canvas.create_line(x_borders[0], y_borders[2], x_borders[4], y_borders[2])
        self.canvas.create_line(x_borders[0], y_borders[3], x_borders[4], y_borders[3])
        self.canvas.create_line(x_borders[0], y_borders[4], x_borders[4], y_borders[4])

        y_shift = r.y0
        for row in state.matrix:
            x_shift = r.x0
            for el in row:
                if el == CellState.BLACK:
                    self.canvas.create_oval(x_shift + 1, y_shift + 1, x_shift + x_diff / 4 - 1,
                                            y_shift + y_diff / 4 - 1, fill='black')
                elif el == CellState.WHITE:
                    self.canvas.create_oval(x_shift + 1, y_shift + 1, x_shift + x_diff / 4 - 1,
                                            y_shift + y_diff / 4 - 1)
                x_shift += x_diff / 4
            y_shift += y_diff / 4


class TreeFrame(StateDisplayFrame):
    def __init__(self, container, tree, estimates, choice, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        if tree is not None:
            self.state_locations = [None] * len(tree.nodes)
            self.draw_tree(tree)
            self.draw_relations(tree)
            self.draw_estimates(estimates)
            self.draw_choice(tree, choice)

    def draw_tree(self, tree: GameTree):
        max_node_count = tree.get_max_count_on_level()
        width = max_node_count * 50
        height = len(tree.count_on_level) * 100

        self.canvas.config(scrollregion=(0, 0, width, height))

        y_shift = 10
        nodes_to_draw = [tree.root_index]
        for node_count in tree.count_on_level:
            if node_count == 0:
                break
            x_margin = (width / node_count - 40) / 2
            x_shift = x_margin

            for i in range(node_count):
                node = nodes_to_draw.pop(0)
                location = StateLocation(x_shift, y_shift, x_shift + 40, y_shift + 40)
                self.draw_state(tree.nodes[node], location)
                self.state_locations[node] = location
                x_shift += 2 * x_margin + 40
                related_nodes = tree.graph.get_related_nodes(node)
                for related_node in related_nodes:
                    if related_node not in nodes_to_draw:
                        nodes_to_draw.append(related_node)
            y_shift += 100

    def draw_relations(self, tree: GameTree):
        for i in range(len(tree.nodes)):
            related_nodes = tree.graph.get_related_nodes(i)

            parent_location = self.state_locations[i]
            x0, y0 = parent_location.get_out_coord()

            for node in related_nodes:
                child_location = self.state_locations[node]
                x1, y1 = child_location.get_in_coord()
                self.canvas.create_line(x0, y0, x1, y1)

    def draw_estimates(self, estimates):
        for i in range(len(estimates)):
            x, y = self.state_locations[i].get_label_coord()
            self.canvas.create_text(x, y, fill="red", text=estimates[i])

    def draw_choice(self, tree, choice):
        parent_location = self.state_locations[tree.root_index]
        x0, y0 = parent_location.get_out_coord()
        child_location = self.state_locations[choice]
        x1, y1 = child_location.get_in_coord()
        self.canvas.create_line(x0, y0, x1, y1, fill="red", width=3)
        self.canvas.create_rectangle(child_location.x0, child_location.y0, child_location.x1, child_location.y1,
                                     width=3, outline='red')


class PlayerInfoFrame(Frame):
    def __init__(self, container, game, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.game = game
        if self.game.first_player.player_type == PlayerType.ALPHA_BETA_BOT:
            self.top_frame = Frame(self)
            self.top_frame.pack(side=TOP, fill=Y, expand=True, padx=5)
            self.label1 = Label(self.top_frame, text='Pirmais spēlētājs (melns)', font=('Segoe', '12', 'bold'))
            self.label1.pack(side=TOP)
            self.frame1 = TreeFrame(self.top_frame, None, None, None, *args, **kwargs)
            self.frame1.pack(side=BOTTOM, fill=Y, expand=True, padx=5)
        if self.game.second_player.player_type == PlayerType.ALPHA_BETA_BOT:
            self.bottom_frame = Frame(self)
            self.bottom_frame.pack(side=BOTTOM, fill=Y, expand=True, padx=5)
            self.label2 = Label(self.bottom_frame, text='Otrais spēlētājs (balts)', font=('Segoe', '12', 'bold'))
            self.label2.pack(side=TOP)
            self.frame2 = TreeFrame(self.bottom_frame, None, None, None, *args, **kwargs)
            self.frame2.pack(side=BOTTOM, fill=Y, expand=True, padx=5)

    def clear(self):
        if self.game.first_player.player_type == PlayerType.ALPHA_BETA_BOT:
            self.frame1.pack_forget()
            self.frame1.destroy()
            self.frame1 = TreeFrame(self.top_frame, None, None, None)
            self.frame1.pack(side=TOP, fill=Y, expand=True, padx=5)
        if self.game.second_player.player_type == PlayerType.ALPHA_BETA_BOT:
            self.frame2.pack_forget()
            self.frame2.destroy()
            self.frame2 = TreeFrame(self.bottom_frame, None, None, None)
            self.frame2.pack(side=BOTTOM, fill=Y, expand=True, padx=5)

    def update(self):
        # Только что походил "черный" игрок
        if self.game.first_player.player_type == PlayerType.ALPHA_BETA_BOT and self.game.next_cell_state_to_apply == CellState.WHITE:
            self.frame1.pack_forget()
            self.frame1.destroy()
            self.frame1 = TreeFrame(
                self.top_frame,
                self.game.first_player.tree,
                self.game.first_player.estimates,
                self.game.first_player.player_choice
            )
            self.frame1.pack(side=TOP, fill=Y, expand=True)
        # Только что походил "белый" игрок
        elif self.game.second_player.player_type == PlayerType.ALPHA_BETA_BOT:
            self.frame2.pack_forget()
            self.frame2.destroy()
            self.frame2 = TreeFrame(
                self.bottom_frame,
                self.game.second_player.tree,
                self.game.second_player.estimates,
                self.game.second_player.player_choice
            )
            self.frame2.pack(side=BOTTOM, fill=Y, expand=True)


class MessageFrame(Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.message = Label(self, text='Patīkamas spēles!', font=('Segoe', '14', 'bold'), fg='green')
        self.message.pack()

    def new_message(self, text):
        self.message['text'] = text
        self.message['fg'] = 'green'

    def new_warning(self, text):
        self.message['text'] = text
        self.message['fg'] = 'red'

    def clear(self):
        self.message['text'] = ""


class ControlFrame(Frame):
    def __init__(self, container, update_func, retry_func, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        self.next_button = Button(
            self,
            text='Turpināt',
            font=('Segoe', '16', 'bold'),
            fg='#FFFFFF',
            bg='#00028c',
            relief='flat',
            command=update_func
        )
        self.next_button.pack(side=RIGHT, fill=X, expand=True, padx=5, pady=5)

        self.restart_button = Button(
            self,
            text='Atkārtot',
            font=('Segoe', '16', 'bold'),
            fg='#00028c',
            bg='#FFFFFF',
            relief='flat',
            command=retry_func
        )
        self.restart_button.pack(side=RIGHT, fill=X, expand=True, padx=5, pady=5)


class DeskFrame(StateDisplayFrame):
    def __init__(self, container, game, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.game = game
        self.player_decision = None
        self.update()

    def update(self):
        if self.game.current_state is not None:
            self.canvas.delete('all')
            self.draw_state(self.game.current_state, StateLocation(100, 100, 500, 500))
            if self.game.is_person_next():
                self.create_decision_buttons()

    def create_decision_buttons(self):
        for coord, directions in self.game.allowed_steps_for_person:
            if self.player_decision is not None and self.player_decision[0] == coord:
                decision_button = self.canvas.create_oval(
                    (coord.x + 1) * 100,
                    (coord.y + 1) * 100,
                    (coord.x + 2) * 100,
                    (coord.y + 2) * 100,
                    fill="green"
                )
            else:
                decision_button = self.canvas.create_oval(
                    (coord.x + 1) * 100,
                    (coord.y + 1) * 100,
                    (coord.x + 2) * 100,
                    (coord.y + 2) * 100,
                    fill="grey",
                    activeoutline="green",
                    activewidth=5
                )

            function = self.__get_func_for_coord(coord.x, coord.y)
            self.canvas.tag_bind(
                decision_button,
                '<Button-1>',
                function
            )

    # Вынужденный колхоз
    def __get_func_for_coord(self, x, y):
        if x == 0 and y == 0:
            return lambda event: self.on_decision_click00()
        if x == 1 and y == 0:
            return lambda event: self.on_decision_click10()
        if x == 2 and y == 0:
            return lambda event: self.on_decision_click20()
        if x == 3 and y == 0:
            return lambda event: self.on_decision_click30()
        if x == 0 and y == 1:
            return lambda event: self.on_decision_click01()
        if x == 3 and y == 1:
            return lambda event: self.on_decision_click31()
        if x == 0 and y == 2:
            return lambda event: self.on_decision_click02()
        if x == 3 and y == 2:
            return lambda event: self.on_decision_click32()
        if x == 0 and y == 3:
            return lambda event: self.on_decision_click03()
        if x == 1 and y == 3:
            return lambda event: self.on_decision_click13()
        if x == 2 and y == 3:
            return lambda event: self.on_decision_click23()
        if x == 3 and y == 3:
            return lambda event: self.on_decision_click33()

    def on_decision_click(self, x, y):
        for allowed in self.game.allowed_steps_for_person:
            if allowed[0].x == x and allowed[0].y == y:
                self.player_decision = allowed
                break
        self.update()

    def on_decision_click00(self):
        self.on_decision_click(0, 0)

    def on_decision_click10(self):
        self.on_decision_click(1, 0)

    def on_decision_click20(self):
        self.on_decision_click(2, 0)

    def on_decision_click30(self):
        self.on_decision_click(3, 0)

    def on_decision_click01(self):
        self.on_decision_click(0, 1)

    def on_decision_click31(self):
        self.on_decision_click(3, 1)

    def on_decision_click02(self):
        self.on_decision_click(0, 2)

    def on_decision_click32(self):
        self.on_decision_click(3, 2)

    def on_decision_click03(self):
        self.on_decision_click(0, 3)

    def on_decision_click13(self):
        self.on_decision_click(1, 3)

    def on_decision_click23(self):
        self.on_decision_click(2, 3)

    def on_decision_click33(self):
        self.on_decision_click(3, 3)


class PlayerChoiceWindow(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Izvēlieties spēlētājus')
        self.geometry("300x200")
        option_frame = Frame(self)
        option_frame.pack(side=TOP, expand=True, fill=BOTH)

        Label(option_frame, text='Pirmais spēlētājs', font=('Segoe', '14')).pack(side=TOP, fill=X, padx=5, pady=5)
        variant1 = StringVar()
        variant1.set('Manuāli')
        player_combobox1 = ttk.Combobox(
            option_frame,
            textvariable=variant1,
            values=('Manuāli', 'Alfa-Beta-1', 'Alfa-Beta-2', 'Alfa-Beta-3', 'Alfa-Beta-4', 'Alfa-Beta-5')
        )
        player_combobox1.pack(side=TOP, fill=X, padx=5, pady=5)

        Label(option_frame, text='Otrais spēlētājs', font=('Segoe', '14')).pack(side=TOP, fill=X, padx=5, pady=5)
        variant2 = StringVar()
        variant2.set('Manuāli')
        player_combobox2 = ttk.Combobox(
            option_frame,
            textvariable=variant2,
            values=('Manuāli', 'Alfa-Beta-1', 'Alfa-Beta-2', 'Alfa-Beta-3', 'Alfa-Beta-4', 'Alfa-Beta-5')
        )
        player_combobox2.pack(side=TOP, fill=X, padx=5, pady=5)

        ok_button = Button(
            self,
            text='Ok',
            font=('Segoe', '12', 'bold'),
            width=12,
            fg='#FFFFFF',
            bg='#111B69',
            relief='flat',
            command=lambda: [
                parent.set_players(self.create_player(variant1.get(), CellState.BLACK),
                                   self.create_player(variant2.get(), CellState.WHITE)),
                self.destroy()
            ]
        )
        ok_button.pack(side=BOTTOM, fill=X, padx=5, pady=5)
        self.bind('<Return>', lambda e: ok_button.invoke())

    def create_player(self, variant, applied_cell_state):
        if variant == 'Manuāli':
            return DecisionPlayer(applied_cell_state, self.master.get_player_decision)
        if variant == 'Alfa-Beta-1':
            return AlphaBetaPlayer(applied_cell_state, 1)
        if variant == 'Alfa-Beta-2':
            return AlphaBetaPlayer(applied_cell_state, 2)
        if variant == 'Alfa-Beta-3':
            return AlphaBetaPlayer(applied_cell_state, 3)
        if variant == 'Alfa-Beta-4':
            return AlphaBetaPlayer(applied_cell_state, 4)
        if variant == 'Alfa-Beta-5':
            return AlphaBetaPlayer(applied_cell_state, 5)


class App(Tk):
    def __init__(self):
        super().__init__()
        self.state('zoomed')
        self.title("Reversi [201RDB177]")

        choice_window = PlayerChoiceWindow(self)
        choice_window.attributes('-topmost', 'true')
        self.wait_window(choice_window)

        self.game = Game(self.player1, self.player2)

        central_frame = Frame(self)
        central_frame.pack(side=LEFT, fill=BOTH, expand=True)

        self.message_frame = MessageFrame(central_frame)
        self.message_frame.pack(side=TOP)

        self.desk_frame = DeskFrame(central_frame, self.game)
        self.desk_frame.pack(side=TOP, fill=BOTH, expand=True)

        right_frame = Frame(self)
        right_frame.pack(side=RIGHT, fill=Y)

        self.curr_player_label = Label(right_frame, text='Tagad lēmumu pieņem pirmais spēlētājs', font=('Segoe', '12'), fg='blue')
        self.curr_player_label.pack(side=TOP, pady=5)

        self.player_info_frame = PlayerInfoFrame(right_frame, self.game)
        self.player_info_frame.pack(side=TOP, fill=BOTH, expand=True)

        self.control_frame = ControlFrame(right_frame, self.update, self.retry)
        self.control_frame.pack(side=BOTTOM, fill=X, padx=0, pady=0)

    def set_players(self, player1, player2):
        self.player1 = player1
        self.player2 = player2

    def update(self):
        if self.game.is_finished:
            self.message_frame.new_message('Spēle pabeigta')
            return

        if self.game.is_person_next():
            if self.desk_frame.player_decision is None and len(self.game.allowed_steps_for_person) > 0:
                self.message_frame.new_warning('Ir jāizvēlas nākamais gājiens')
            else:
                self.game.next()

                self.desk_frame.update()
                self.player_info_frame.update()
                self.message_frame.clear()
                self.desk_frame.player_decision = None
        else:
            self.game.next()
            if self.game.is_finished:
                self.message_frame.new_message('Spēle pabeigta')
                return
            self.desk_frame.update()
            self.player_info_frame.update()
            self.message_frame.clear()

        if self.game.next_cell_state_to_apply == CellState.BLACK:
            self.curr_player_label['text'] = 'Tagad lēmumu pieņem pirmais spēlētājs'
        else:
            self.curr_player_label['text'] = 'Tagad lēmumu pieņem otrais spēlētājs'

    def retry(self):
        self.player1.retry()
        self.player2.retry()
        self.game.new_game(self.player1, self.player2)
        self.desk_frame.update()
        self.player_info_frame.clear()

    def get_player_decision(self):
        return self.desk_frame.player_decision


if __name__ == "__main__":
    app = App()
    app.mainloop()
