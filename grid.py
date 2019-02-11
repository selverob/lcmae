#! /usr/bin/env python3

from typing import Tuple
import arcade
from arcade.color import BLACK, WHITE
import level
from sys import argv, exit


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
                            self.grid_size[0] * (cell_size + border) + border)
        self.running = False
        self.__update_walls()
        self.__update_danger()
        if paths is not None:
            self.paths = paths
            self.path_idx = 0
            self.__update_agents()
        else:
            self.agents = None
        self.current_drag_coords = None
        super().__init__(self.screen_size[0], self.screen_size[1])
        arcade.set_background_color(WHITE)
        self.set_update_rate(1/3)

    def on_draw(self):
        arcade.start_render()
        self.walls.draw()
        self.danger_cells.draw()
        if self.agents is not None:
            self.agents.draw()

    def on_update(self, delta_time: float):
        if self.agents is not None and self.running:
            self.path_idx += 1
            self.__update_agents()

    def on_mouse_press(self, x: float,  y: float, button: int, modifiers: int):
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

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float,
                      button: int, modifiers: int):
        if button != 1:
            return
        self.__update_drag_coords(x, y)

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
                self.__update_danger()

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

    def __update_danger(self):
        danger_cells = arcade.ShapeElementList()
        for coords in self.danger:
            pos = self.__pos_for_coords(coords[0], coords[1])
            shape = arcade.create_rectangle_filled(pos[0],
                                                   pos[1],
                                                   self.cell_size,
                                                   self.cell_size,
                                                   arcade.color.BABY_PINK)
            danger_cells.append(shape)
        self.danger_cells = danger_cells

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
        y = self.screen_size[1] - (
            row * cell_with_border + self.border + self.cell_size/2)
        return (x, y)

    def __coords_for_pos(self, x: float, y: float) -> Tuple[int, int]:
        row = self.grid_size[0] - y // (self.cell_size + self.border) - 1
        col = x // (self.cell_size + self.border)
        return (row, col)


def parse_paths(path: str):
    result = []
    with open(path) as f:
        lines = f.readlines()
        if lines[-1] == [""]:
            lines = lines[:-1]
        for line in lines:
            result.append(list(map(lambda s: int(s), line.strip().split(" "))))
    return result

def check_paths(paths):
    l = len(paths[0])
    for p in paths:
        if len(p) != l:
            print("Not all paths have equal sizes")
            exit(1)
    for t in range(l):
        s = set()
        for p in paths:
            s.add(p[t])
        if len(s) != len(paths):
            print(f"Collision at time {t}")

def main():
    map_path, scen_path = argv[1], argv[2]
    paths = None
    if len(argv) == 4:
        paths = parse_paths(argv[3])
    check_paths(paths)
    lines = []
    with open(map_path) as map_f:
        for _ in range(4):
            map_f.readline()
        lines = list(map(lambda l: l.strip(), map_f.readlines()))
    scenario = level.Scenario.from_file(scen_path)
    Grid(lines, scenario, paths, cell_size=10, border=2)
    arcade.run()


if __name__ == "__main__":
    main()
