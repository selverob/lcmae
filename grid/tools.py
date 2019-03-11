import arcade
from abc import ABC, abstractmethod


class Tool(ABC):
    def __init__(self, grid):
        self.grid = grid

    @abstractmethod
    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        raise NotImplementedError()

    @abstractmethod
    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float,
                      button: int, modifiers: int):
        raise NotImplementedError()


class DraggableTool(Tool):
    def __init__(self, grid):
        self.grid = grid
        self.previous_position = None

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.update_mouse_pos(x, y, button)

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float,
                      button: int, modifiers: int):
        self.update_mouse_pos(x, y, button)

    def update_mouse_pos(self, x: float, y: float, button: int):
        row, col = self.grid.coords_for_pos(x, y)
        if (row, col) != self.previous_position:
            is_valid_row = row >= 0 and row < self.grid.grid_size[0]
            is_valid_col = col >= 0 and col < self.grid.grid_size[1]
            if not is_valid_col or not is_valid_row:
                return
            self.previous_position = (row, col)
            if button == arcade.MOUSE_BUTTON_LEFT:
                self.add_object_at_coords(row, col)
            elif button == arcade.MOUSE_BUTTON_RIGHT:
                self.remove_object_at_coords(row, col)

    def filled_rectangle_at(self, row: int, col: int, color: arcade.Color) -> arcade.buffered_draw_commands.Shape:
        pos = self.grid.pos_for_coords(row, col)
        return arcade.create_rectangle_filled(
            pos[0],
            pos[1],
            self.grid.cell_size,
            self.grid.cell_size,
            color)
    @abstractmethod
    def add_object_at_coords(self, row: int, col: int):
        raise NotImplementedError()

    @abstractmethod
    def remove_object_at_coords(self, row: int, col: int):
        raise NotImplementedError()


class Wall(DraggableTool):
    def add_object_at_coords(self, row: int, col: int):
        self.grid.walls[(row, col)] = self.filled_rectangle_at(row, col, arcade.color.BLACK)
        coords = (row, col)
        if coords in self.grid.danger:
            del self.grid.danger[coords]
        if coords in self.grid.agents:
            del self.grid.agents[coords]

    def remove_object_at_coords(self, row: int, col: int):
        if (row, col) in self.grid.walls:
            del self.grid.walls[(row, col)]


class Danger(DraggableTool):
    def add_object_at_coords(self, row: int, col: int):
        coords = (row, col)
        if coords in self.grid.walls:
            return
        self.grid.danger[coords] = self.filled_rectangle_at(row, col, arcade.color.BABY_PINK)

    def remove_object_at_coords(self, row: int, col: int):
        if (row, col) in self.grid.danger:
            del self.grid.danger[(row, col)]


class Agent(DraggableTool):
    color = None

    def add_object_at_coords(self, row: int, col: int):
        coords = (row, col)
        if coords not in self.grid.walls:
            self.grid.agents[coords] = self.filled_rectangle_at(row, col, type(self).color)

    def remove_object_at_coords(self, row: int, col: int):
        if (row, col) in self.grid.agents:
            del self.grid.agents[(row, col)]


class RetargetingAgent(Agent):
    color = arcade.color.GREEN


class FrontierAgent(Agent):
    color = arcade.color.BLUE


class StaticAgent(Agent):
    color = arcade.color.ORANGE


class DumbAgent(Agent):
    color = arcade.color.RED
