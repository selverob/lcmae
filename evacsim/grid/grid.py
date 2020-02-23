from typing import Iterable, Tuple
import arcade

import evacsim.grid.tools as tools
from evacsim.level import Scenario, coords_to_id, id_to_coords, AgentType
from .shape_collection import ShapeCollection


class Grid(arcade.Window):
    def __init__(self, level_map, scenario: Scenario, paths=None, cell_size=5, border=1):
        self.grid_size = (len(level_map), len(level_map[0]))
        self.cell_size = cell_size
        self.border = border
        self.screen_size = (self.grid_size[1] * (cell_size + border) + border,
                            self.grid_size[0] * (cell_size + border) + border)
        super().__init__(self.screen_size[0], self.screen_size[1])
        self.level_map = level_map
        self.scenario = scenario
        self.running = False

        self.tool: tools.Tool = tools.Wall(self)

        self.walls = ShapeCollection()
        self.danger = ShapeCollection()
        self.agents = ShapeCollection()

        self._initialize_walls()
        self._initialize_danger()
        self._initialize_agents()

        if paths is not None:
            self.paths = paths
            self.current_step = 0
        else:
            self.paths = None

        self.status_text = "Drawing walls"
        arcade.set_background_color(arcade.color.WHITE)
        self.set_update_rate(1 / 8)

    def on_draw(self):
        if not self.walls.dirty() and not self.danger.dirty() and not self.agents.dirty():
            return
        arcade.start_render()
        self.walls.draw()
        self.danger.draw()
        self.agents.draw()
        # arcade.draw_text(self.status_text, 0, self.screen_size[1] - 12, arcade.color.BLACK, font_size=12)

    def on_update(self, delta_time: float):
        if self.paths is not None and self.running:
            if self.current_step == len(self.paths[0]):
                self.running = False
                return
            self.step()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if not self.running:
            self.tool.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float,
                      button: int, modifiers: int):
        if not self.running:
            self.tool.on_mouse_drag(x, y, dx, dy, button, modifiers)

    def on_key_press(self, symbol: int, modifiers: int):
        char = chr(symbol)
        if char == "w":
            self.tool = tools.Wall(self)
            self.status_text = "Drawing walls"
        elif char == "d":
            self.tool = tools.Danger(self)
            self.status_text = "Drawing danger zone"
        elif char == "r":
            self.tool = tools.RetargetingAgent(self)
            self.status_text = "Drawing retargeting agents"
        elif char == "f":
            self.tool = tools.FrontierAgent(self)
            self.status_text = "Drawing frontier agents"
        elif char == "s":
            self.tool = tools.StaticAgent(self)
            self.status_text = "Drawing static agents"
        elif char == "p":
            self.tool = tools.PanickedAgent(self)
            self.status_text = "Drawing panicked agents"
        elif char == "h":
            self.tool = tools.CoordPrint(self)
            self.status_text = "Printing click coordinates"
        elif char == "m":
            self.write_out()
        elif char == ' ':
            if self.paths is not None:
                self.running = not self.running

    def pos_for_coords(self, row, col):
        cell_with_border = (self.cell_size + self.border)
        x = col * cell_with_border + self.border + self.cell_size / 2
        y = self.screen_size[1] - (
            row * cell_with_border + self.border + self.cell_size / 2)
        return (x, y)

    def coords_for_pos(self, x: float, y: float) -> Tuple[int, int]:
        row = self.grid_size[0] - y // (self.cell_size + self.border) - 1
        col = x // (self.cell_size + self.border)
        return (row, col)

    def step(self):
        positions = map(lambda p: p[self.current_step], self.paths)
        self._draw_agents_at_positions(positions)
        self.current_step += 1

    def make_scenario(self) -> Scenario:
        s = Scenario([], [])
        for row, col in self.danger.shapes:
            s.danger.append(coords_to_id(self.grid_size[1], row, col))
        for row, col in self.agents.shapes:
            s.agents.append(self.agents.get_meta((row, col)))
        return s

    def _initialize_walls(self):
        wall_tool = tools.Wall(self)
        for row, line in enumerate(self.level_map):
            for col, char in enumerate(line):
                if char == "@":
                    wall_tool.add_object_at_coords(row, col)

    def _initialize_danger(self):
        danger_tool = tools.Danger(self)
        for coords in self.scenario.danger_coords(len(self.level_map[0])):
            danger_tool.add_object_at_coords(*coords)

    def _initialize_agents(self):
        self._draw_agents_at_positions(map(lambda a: a.origin, self.scenario.agents))

    def _draw_agents_at_positions(self, positions: Iterable[int]):
        self.agents = ShapeCollection()
        r_tool = tools.RetargetingAgent(self)
        f_tool = tools.FrontierAgent(self)
        s_tool = tools.StaticAgent(self)
        p_tool = tools.PanickedAgent(self)
        for position, agent in zip(positions, self.scenario.agents):
            t = agent.type
            coords = id_to_coords(self.grid_size[1], position)
            if t == AgentType.RETARGETING:
                r_tool.add_object_at_coords(*coords)
            elif t == AgentType.CLOSEST_FRONTIER:
                f_tool.add_object_at_coords(*coords)
            elif t == AgentType.PANICKED:
                p_tool.add_object_at_coords(*coords)
            elif t == AgentType.STATIC:
                s_tool.add_agent(coords, id_to_coords(self.grid_size[1], agent.goal))

    def write_out(self):
        with open("out.map", "w") as f:
            self.write_map(f)
        with open("out.scen", "w") as f:
            self.make_scenario().write(f)

    def write_map(self, f):
        print("type octile", file=f)
        print(f"height {self.grid_size[0]}", file=f)
        print(f"width {self.grid_size[1]}", file=f)
        print("map", file=f)
        for row in range(self.grid_size[0]):
            row_str = ""
            for col in range(self.grid_size[1]):
                if (row, col) in self.walls:
                    row_str += "@"
                else:
                    row_str += "."
            print(row_str, file=f)
