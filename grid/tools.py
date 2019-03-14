import arcade
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Tuple
from level import Scenario, coords_to_id


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

    def check_coord_validity(self, row: int, col: int) -> bool:
        is_valid_row = row >= 0 and row < self.grid.grid_size[0]
        is_valid_col = col >= 0 and col < self.grid.grid_size[1]
        return is_valid_col and is_valid_row

    def filled_rectangle_at(self, row: int, col: int, color: arcade.Color) -> arcade.buffered_draw_commands.Shape:
        pos = self.grid.pos_for_coords(row, col)
        return arcade.create_rectangle_filled(
            pos[0],
            pos[1],
            self.grid.cell_size,
            self.grid.cell_size,
            color)


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
            if not self.check_coord_validity(row, col):
                return
            self.previous_position = (row, col)
            if button == arcade.MOUSE_BUTTON_LEFT:
                self.add_object_at_coords(row, col)
            elif button == arcade.MOUSE_BUTTON_RIGHT:
                self.remove_object_at_coords(row, col)

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
    agent_type: Optional[Scenario.AgentType] = None
    color: Optional[arcade.Color] = None

    def add_object_at_coords(self, row: int, col: int):
        coords = (row, col)
        if coords not in self.grid.walls:
            self.grid.agents[coords] = self.filled_rectangle_at(row, col, type(self).color)
            self.grid.agents.add_meta(coords, self.create_agent_object(row, col))

    def remove_object_at_coords(self, row: int, col: int):
        if (row, col) in self.grid.agents:
            del self.grid.agents[(row, col)]

    def create_agent_object(self, row: int, col: int):
        origin_id = coords_to_id(self.grid.grid_size[1], row, col)
        return Scenario.Agent(type(self).agent_type, origin_id, None)


class RetargetingAgent(Agent):
    agent_type = Scenario.AgentType.RETARGETING
    color = arcade.color.GREEN


class FrontierAgent(Agent):
    agent_type = Scenario.AgentType.CLOSEST_FRONTIER
    color = arcade.color.BLUE


class PanickedAgent(Agent):
    agent_type = Scenario.AgentType.PANICKED
    color = arcade.color.RED


class StaticAgent(Tool):
    State = Enum("State", "ORIGIN TARGET")

    def __init__(self, grid):
        super().__init__(grid)
        self.state = StaticAgent.State.ORIGIN
        self.current_origin = None

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self._left_click(x, y)
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self._right_click(x, y)

    def _left_click(self, x: float, y: float):
        coords = self.grid.coords_for_pos(x, y)
        if not self.check_coord_validity(*coords):
            return
        if self.state is StaticAgent.State.ORIGIN:
            self.current_origin = coords
            self.state = StaticAgent.State.TARGET
        else:
            self.add_agent(self.current_origin, coords)
            self.state = StaticAgent.State.ORIGIN

    def _right_click(self, x: float, y: float):
        pass

    def add_agent(self, origin: Tuple[int, int], target: Tuple[int, int]):
        self.grid.agents[origin] = self.filled_rectangle_at(*origin, arcade.color.ORANGE)
        origin_id = coords_to_id(self.grid.grid_size[1], *origin)
        target_id = coords_to_id(self.grid.grid_size[1], *target)
        self.grid.agents.add_meta(origin, Scenario.Agent(Scenario.AgentType.STATIC, origin_id, target_id))

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float,
                      button: int, modifiers: int):
        pass
