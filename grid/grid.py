from typing import Tuple
import arcade
import grid.tools as tools
from .shape_collection import ShapeCollection


class Grid(arcade.Window):
    def __init__(self, level_map, scenario, paths=None, cell_size=5, border=1):
        self.grid_size = (len(level_map), len(level_map[0]))
        self.cell_size = cell_size
        self.border = border
        self.screen_size = (self.grid_size[1] * (cell_size + border) + border,
                            self.grid_size[0] * (cell_size + border) + border + 15)
        super().__init__(self.screen_size[0], self.screen_size[1])
        self.level_map = level_map
        self.running = False

        self.tool = tools.Wall(self)

        self.walls = ShapeCollection()
        self.danger = ShapeCollection()
        self.agents = ShapeCollection()

        # if paths is not None:
        #     self.paths = paths
        #     self.path_idx = 0
        #     self.__update_agents()
        # else:
        #     self.agents = None
        self.set_status("Drawing walls")
        arcade.set_background_color(arcade.color.WHITE)
        self.set_update_rate(1 / 5)

    def on_draw(self):
        if not self.walls.dirty() and not self.danger.dirty() and not self.agents.dirty():
            return
        arcade.start_render()
        self.walls.draw()
        self.danger.draw()
        self.agents.draw()
        arcade.draw_text(self.status_text, 0, self.screen_size[1] - 12, arcade.color.BLACK, font_size=10)

    def on_update(self, delta_time: float):
        pass
        # if self.agents is not None and self.running:
        #     self.path_idx += 1
        #     self.__update_agents()
        #     self.dirty = True

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.tool.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float,
                      button: int, modifiers: int):
        self.tool.on_mouse_drag(x, y, dx, dy, button, modifiers)

    def on_key_press(self, symbol: int, modifiers: int):
        char = chr(symbol)
        if char == "w":
            self.tool = tools.Wall(self)
        elif char == "d":
            self.tool = tools.Danger(self)
        elif char == "r":
            self.tool = tools.RetargetingAgent(self)
        elif char == "f":
            self.tool = tools.FrontierAgent(self)
        elif char == "s":
            self.tool = tools.StaticAgent(self)
        elif char == "p":
            # TODO
            pass
        else:
            print(symbol, char)

    def pos_for_coords(self, row, col):
        cell_with_border = (self.cell_size + self.border)
        x = col * cell_with_border + self.border + self.cell_size/2
        y = self.screen_size[1] - 15 - (
            row * cell_with_border + self.border + self.cell_size/2)
        return (x, y)

    def coords_for_pos(self, x: float, y: float) -> Tuple[int, int]:
        row = self.grid_size[0] - y // (self.cell_size + self.border) - 1
        col = x // (self.cell_size + self.border)
        return (row, col)

    def set_status(self, text: str):
        self.status_text = text
        self.dirty = True
