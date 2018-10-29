from enum import Enum
import arcade
from arcade.color import BLACK, WHITE
import networkx as nx
import matplotlib.pyplot as plt
from random_walker import RandomWalker
from astar import AStar


class Square():
    def __init__(self, pos, size, color=WHITE, marked=False):
        self.pos = pos
        self.size = size
        self.color = color
        self.marked = marked

    def draw(self):
        arcade.draw_rectangle_filled(
            self.pos[0], self.pos[1], self.size, self.size, self.color)
        if self.marked:
            arcade.draw_point(self.pos[0], self.pos[1], BLACK, self.size/5)


class Agent():
    def __init__(self, start, color):
        self.start = start
        self.pos = start
        self.color = color
        self.finish = None


class Grid(arcade.Window):
    __COLORS = [arcade.color.GREEN, arcade.color.BABY_BLUE, arcade.color.TEAL, arcade.color.MODE_BEIGE,
                arcade.color.NAVY_BLUE, arcade.color.PURPLE, arcade.color.BROWN, arcade.color.GRAY]
    State = Enum("State", "WALLS AGENT_START AGENT_FINISH RUN DONE")

    def __init__(self, grid_size, algorithm_class, drawing_timeout=500, cell_size=25, border=5):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.border = border
        self.screen_size = (grid_size[1] * (cell_size + border) +
                            border, grid_size[0] * (cell_size + border) + border)
        self.grid = []
        self.agents = []
        self.state = Grid.State.WALLS
        self.algorithm_class = algorithm_class
        self.pathfinder = None
        for row in range(self.grid_size[0]):
            self.grid.append([])
            for col in range(self.grid_size[1]):
                x = col * (self.cell_size + self.border) + \
                    self.border + self.cell_size/2
                y = row * (self.cell_size + self.border) + \
                    self.border + self.cell_size/2
                self.grid[row].append(Square((x, y), self.cell_size))

        super().__init__(self.screen_size[0], self.screen_size[1])
        arcade.set_background_color(BLACK)

    def on_draw(self):
        arcade.start_render()
        for row in self.grid:
            for sq in row:
                sq.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        row = y // (self.cell_size + self.border)
        col = x // (self.cell_size + self.border)
        if row >= self.grid_size[0] or col >= self.grid_size[1]:
            return
        if self.state == Grid.State.WALLS and button == 1:
            self.toggle_wall(row, col)
        elif self.state == Grid.State.WALLS and button == 4:
            self.state = Grid.State.AGENT_START
        elif self.state == Grid.State.AGENT_START and button == 1:
            self.add_agent(row, col)
            self.state = Grid.State.AGENT_FINISH
        elif self.state == Grid.State.AGENT_START and button == 4:
            self.state = Grid.State.RUN
            self.run()
        elif self.state == Grid.State.AGENT_FINISH and button == 1:
            self.add_finish(row, col)
            self.state = Grid.State.AGENT_START

    def toggle_wall(self, row, col):
        square = self.grid[row][col]
        if square.color == BLACK:
            square.color = WHITE
        else:
            square.color = BLACK

    def add_agent(self, row, col):
        color = Grid.__COLORS[len(self.agents) % len(Grid.__COLORS)]
        self.grid[row][col].color = color
        self.agents.append(Agent((row, col), color))

    def add_finish(self, row, col):
        square = self.grid[row][col]
        square.color = Grid.__COLORS[len(self.agents) - 1 % len(Grid.__COLORS)]
        square.marked = True
        self.agents[-1].finish = (row, col)

    def on_update(self, delta_time):
        if self.state != Grid.State.RUN:
            return
        try:
            new_positions = next(self.pathfinder)
            # It's necessary to first blank all the agent squares, because
            # otherwise it'd be possible that we'd blank a square that
            # could have already been painted over with another agent's color.
            for agent in self.agents:
                pos = agent.pos
                self.grid[pos[0]][pos[1]].color = WHITE
            for agent_idx, node_id in enumerate(new_positions):
                pos = self.__id_to_coords(node_id)
                agent = self.agents[agent_idx]
                agent.pos = pos
                self.grid[pos[0]][pos[1]].color = agent.color
        except StopIteration:
            self.state = Grid.State.DONE

    def run(self):
        agents = [(self.__coords_to_id(*agent.start),
                   self.__coords_to_id(*agent.finish)) for agent in self.agents]
        self.pathfinder = self.algorithm_class(
            self.__build_network(), agents, self.__id_to_coords).__iter__()
        self.set_update_rate(1/3)

    def _clear_grid(self):
        for agent in self.agents:
            pos = agent.pos
            self.grid[pos[0]][pos[1]].color = WHITE

    def __build_network(self):
        g = nx.Graph()
        for row, row_data in enumerate(self.grid):
            for col, square in enumerate(row_data):
                if square.color == BLACK:
                    continue
                square_id = self.__coords_to_id(row, col)
                g.add_node(square_id)
                if row != 0 and self.grid[row-1][col].color != BLACK:
                    g.add_edge(square_id, self.__coords_to_id(row-1, col))
                if row != self.grid_size[0] - 1 and self.grid[row+1][col].color != BLACK:
                    g.add_edge(square_id, self.__coords_to_id(row+1, col))
                if col != 0 and self.grid[row][col - 1].color != BLACK:
                    g.add_edge(square_id, self.__coords_to_id(row, col - 1))
                if col != self.grid_size[1] - 1 and self.grid[row][col+1].color != BLACK:
                    g.add_edge(square_id, self.__coords_to_id(row, col + 1))
        return g

    def __coords_to_id(self, row, col):
        return row * self.grid_size[1] + col

    def __id_to_coords(self, node_id):
        return (node_id // self.grid_size[1], node_id % self.grid_size[1])


def main():
    Grid((10, 10), AStar)
    arcade.run()


if __name__ == "__main__":
    main()
