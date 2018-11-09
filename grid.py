#! /usr/bin/env python3

import arcade
from arcade.color import BLACK, WHITE
import networkx as nx
import cProfile
import level
from sys import argv

class Grid(arcade.Window):
    __COLORS = [arcade.color.GREEN, arcade.color.BABY_BLUE, arcade.color.TEAL, arcade.color.MODE_BEIGE,
                arcade.color.NAVY_BLUE, arcade.color.PURPLE, arcade.color.BROWN, arcade.color.GRAY]

    def __init__(self, level_map, scenario, paths=None, cell_size=5, border=1):
        self.grid_size = (len(level_map), len(level_map[0]))
        self.cell_size = cell_size
        self.border = border
        self.screen_size = (self.grid_size[1] * (cell_size + border) +
                            border, self.grid_size[0] * (cell_size + border) + border)
        self.background = self.__get_background(level_map, scenario.danger_coords(self.grid_size[1]))
        if paths != None:
            self.paths = paths
            self.path_idx = 0
            self.__update_agents()
        else:
            self.agents = None
        super().__init__(self.screen_size[0], self.screen_size[1])
        arcade.set_background_color(WHITE)
        self.set_update_rate(1/3)

    def on_draw(self):
        arcade.start_render()
        self.background.draw()
        if self.agents != None:
            self.agents.draw()

    def on_update(self, delta_time):
        if self.agents != None:
            self.path_idx += 1
            self.__update_agents()
    
    def on_mouse_press(self, x, y, button, modifiers):
        row = self.grid_size[0] - y // (self.cell_size + self.border) - 1
        col = x // (self.cell_size + self.border)
        print(row, col, level.coords_to_id(self.grid_size[1], row, col))

    def __get_background(self, level_map, danger):
        bg = arcade.ShapeElementList()
        for row, row_data in enumerate(level_map):
            for col, character in enumerate(row_data):
                if character == "@":
                    pos = self.__pos_for_coords(row, col)
                    shape = arcade.create_rectangle_filled(pos[0], pos[1], self.cell_size, self.cell_size, BLACK)
                    bg.append(shape)
        for coords in danger:
            pos = self.__pos_for_coords(coords[0], coords[1])
            shape = arcade.create_rectangle_filled(pos[0], pos[1], self.cell_size, self.cell_size, arcade.color.RED)
            bg.append(shape)
        return bg

    def __update_agents(self):
        node_ids = [path[self.path_idx] if self.path_idx < len(path) else path[-1] for path in self.paths]
        self.agents = arcade.ShapeElementList()
        for i, node_id in enumerate(node_ids):
            coords = level.id_to_coords(self.grid_size[1], node_id)
            pos = self.__pos_for_coords(*coords)
            color = Grid.__COLORS[i % len(Grid.__COLORS)]
            shape = arcade.create_rectangle_filled(pos[0], pos[1], self.cell_size, self.cell_size, color)
            self.agents.append(shape)

    def __pos_for_coords(self, row, col):
        x = (col * (self.cell_size + self.border) + self.border + self.cell_size/2)
        y = self.screen_size[1] - (row * (self.cell_size + self.border) + self.border + self.cell_size/2)
        return (x, y)

def parse_paths(path):
    result = []
    with open(path) as f:
        lines = f.readlines()
        if lines[-1] == [""]: lines = lines[:-1]
        for line in lines:
            result.append(list(map(lambda s: int(s), line.strip().split(" "))))
    return result
        

def main():
    map_path, scen_path = argv[1], argv[2]
    paths = None
    if len(argv) == 4:
        paths = parse_paths(argv[3])
    lines = []
    with open(map_path) as map_f:
        for _ in range(4): map_f.readline()
        lines = list(map(lambda l: l.strip(), map_f.readlines()))
    scenario = level.Scenario.from_file(scen_path)
    Grid(lines, scenario, paths, cell_size=10, border=2)
    arcade.run()


if __name__ == "__main__":
    main()
