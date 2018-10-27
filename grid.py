from enum import Enum
import arcade

class Square():
    def __init__(self, pos, size, color = arcade.color.WHITE, marked=False):
        self.pos = pos
        self.size = size
        self.color = color
        self.marked = marked
    
    def draw(self):
        arcade.draw_rectangle_filled(self.pos[0], self.pos[1], self.size, self.size, self.color)
        if self.marked:
            arcade.draw_point(self.pos[0], self.pos[1], arcade.color.BLACK, self.size/5)


class Grid(arcade.Window):
    __COLORS = [arcade.color.GREEN, arcade.color.BABY_BLUE, arcade.color.TEAL, arcade.color.MODE_BEIGE, arcade.color.NAVY_BLUE, arcade.color.PURPLE, arcade.color.BROWN, arcade.color.GRAY]
    State = Enum("State", "WALLS AGENT_START AGENT_FINISH RUN")

    def __init__(self, grid_size, cell_size=25, border=5):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.border = border
        self.screen_size = (grid_size[1] * (cell_size + border) + border, grid_size[0] * (cell_size + border) + border)
        self.grid = []
        self.state = Grid.State.WALLS
        for row in range(self.grid_size[0]):
            self.grid.append([])
            for col in range(self.grid_size[1]):
                x = col * (self.cell_size + self.border) + self.border + self.cell_size/2
                y = row * (self.cell_size + self.border) + self.border + self.cell_size/2
                self.grid[row].append(Square((x, y), self.cell_size))

        self.agent_count = 0

        super().__init__(self.screen_size[0], self.screen_size[1])
        arcade.set_background_color(arcade.color.BLACK)
    
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
        elif self.state == Grid.State.AGENT_FINISH and button == 1:
            self.add_finish(row, col)
            self.state = Grid.State.AGENT_START
    
    def toggle_wall(self, row, col):
        square = self.grid[row][col]
        if square.color == arcade.color.BLACK:
            square.color = arcade.color.WHITE
        else:
            square.color = arcade.color.BLACK
    
    def add_agent(self, row, col):
        self.grid[row][col].color = Grid.__COLORS[self.agent_count % len(Grid.__COLORS)]
        self.agent_count += 1

    def add_finish(self, row, col):
        square = self.grid[row][col]
        square.color = Grid.__COLORS[self.agent_count - 1 % len(Grid.__COLORS)]
        square.marked = True
    
    #def build_network(self):


def main():
    Grid((10, 10))
    arcade.run()

if __name__ == "__main__":
    main()