from typing import Tuple
import arcade
from arcade.color import BLACK, WHITE
import level


class Grid(arcade.Window):
    __COLORS = [arcade.color.GREEN, arcade.color.BABY_BLUE, arcade.color.TEAL,
                arcade.color.MODE_BEIGE, arcade.color.NAVY_BLUE,
                arcade.color.PURPLE, arcade.color.BROWN, arcade.color.GRAY]

    def __init__(self, level_map, scenario, paths=None, cell_size=5, border=1):
        self.grid_size = (len(level_map), len(level_map[0]))
        self.cell_size = cell_size
        self.border = border
        self.level_map = level_map
        self.danger = set(scenario.danger_coords(self.grid_size[1]))
        self.screen_size = (self.grid_size[1] * (cell_size + border) + border,
                            self.grid_size[0] * (cell_size + border) + border + 15)
        self.running = False
        self.current_drag_coords = None
        self.__update_walls()
        self.danger_cells = arcade.ShapeElementList()
        self.__add_danger(*self.danger)
        if paths is not None:
            self.paths = paths
            self.path_idx = 0
            self.__update_agents()
        else:
            self.agents = None
        self.set_status("Left click draws danger or starts sim. Middle click prints coord. Right click prints all danger.")
        super().__init__(self.screen_size[0], self.screen_size[1])
        arcade.set_background_color(WHITE)
        self.set_update_rate(1/5)

    def on_draw(self):
        if not self.dirty:
            return
        arcade.start_render()
        self.danger_cells.draw()
        self.walls.draw()
        if self.agents is not None:
            self.agents.draw()
        arcade.draw_text(self.status_text, 0, self.screen_size[1] - 12, arcade.color.BLACK, font_size=10)
        self.dirty = False

    def on_update(self, delta_time: float):
        if self.agents is not None and self.running:
            self.path_idx += 1
            self.__update_agents()
            self.dirty = True

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.running = True
        if button == 1:
            self.__update_drag_coords(x, y)
        elif button == 4:
            d = map(lambda x: level.coords_to_id(self.grid_size[1], *x),
                    self.danger)
            print(*sorted(d))
        elif button == 2:
            print(level.coords_to_id(
                self.grid_size[1], *self.__coords_for_pos(x, y)))
        self.dirty = True

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float,
                      button: int, modifiers: int):
        if button != 1:
            return
        self.__update_drag_coords(x, y)
        self.dirty = True

    def __update_drag_coords(self, x, y):
        row, col = self.__coords_for_pos(x, y)
        if (row, col) != self.current_drag_coords:
            self.current_drag_coords = (row, col)
            is_valid_row = row >= 0 and row < self.grid_size[0]
            is_valid_col = col >= 0 and col < self.grid_size[1]
            if (is_valid_row and
                    is_valid_col and
                    self.level_map[row][col] != "@"):
                self.danger.add(self.current_drag_coords)
                self.__add_danger(self.current_drag_coords)

    def __update_walls(self):
        walls = arcade.ShapeElementList()
        for row, row_data in enumerate(self.level_map):
            for col, character in enumerate(row_data):
                if character == "@":
                    pos = self.__pos_for_coords(row, col)
                    shape = arcade.create_rectangle_filled(pos[0],
                                                           pos[1],
                                                           self.cell_size,
                                                           self.cell_size,
                                                           BLACK)
                    walls.append(shape)
        self.walls = walls

    def __add_danger(self, *danger_coords):
        for coords in danger_coords:
            pos = self.__pos_for_coords(coords[0], coords[1])
            shape = arcade.create_rectangle_filled(pos[0],
                                                   pos[1],
                                                   self.cell_size,
                                                   self.cell_size,
                                                   arcade.color.BABY_PINK)
            self.danger_cells.append(shape)

    def __update_agents(self):
        node_ids = [path[self.path_idx] if self.path_idx < len(path) else path[-1] for path in self.paths]
        self.agents = arcade.ShapeElementList()
        for i, node_id in enumerate(node_ids):
            coords = level.id_to_coords(self.grid_size[1], node_id)
            pos = self.__pos_for_coords(*coords)
            color = Grid.__COLORS[i % len(Grid.__COLORS)]
            shape = arcade.create_rectangle_filled(pos[0],
                                                   pos[1],
                                                   self.cell_size,
                                                   self.cell_size,
                                                   color)
            self.agents.append(shape)

    def __pos_for_coords(self, row, col):
        cell_with_border = (self.cell_size + self.border)
        x = col * cell_with_border + self.border + self.cell_size/2
        y = self.screen_size[1] - 15 - (
            row * cell_with_border + self.border + self.cell_size/2)
        return (x, y)

    def __coords_for_pos(self, x: float, y: float) -> Tuple[int, int]:
        row = self.grid_size[0] - y // (self.cell_size + self.border) - 1
        col = x // (self.cell_size + self.border)
        return (row, col)

    def set_status(self, text: str):
        self.status_text = text
        self.dirty = True
