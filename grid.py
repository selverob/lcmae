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

    def __init__(self, level_map, scenario, cell_size=5, border=1):
        self.grid_size = (len(level_map), len(level_map[0]))
        self.cell_size = cell_size
        self.border = border
        self.screen_size = (self.grid_size[1] * (cell_size + border) +
                            border, self.grid_size[0] * (cell_size + border) + border)
        self.agents = []
        self.__background = self.__get_background(level_map, scenario.danger_coords(self.grid_size[1]))

        super().__init__(self.screen_size[0], self.screen_size[1])
        arcade.set_background_color(WHITE)
        self.set_update_rate(1/3)

    def on_draw(self):
        arcade.start_render()
        self.__background.draw()

    def on_update(self, delta_time):
        pass
    
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

    def __pos_for_coords(self, row, col):
        x = (col * (self.cell_size + self.border) + self.border + self.cell_size/2)
        y = self.screen_size[1] - (row * (self.cell_size + self.border) + self.border + self.cell_size/2)
        return (x, y)

def main():
    print(argv)
    map_path, scen_path = argv[1:]
    lines = []
    with open(map_path) as map_f:
        for _ in range(4): map_f.readline()
        lines = list(map(lambda l: l.strip(), map_f.readlines()))
    scenario = level.Scenario.from_file(scen_path)
    Grid(lines, scenario, cell_size=10, border=2)
    arcade.run()


if __name__ == "__main__":
    main()
