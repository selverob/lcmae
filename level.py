import networkx as nx

def coords_to_id(cols, row, col):
    return row * cols + col

def id_to_coords(cols, node_id):
    return (node_id // cols, node_id % cols)

class ParseError(Exception):
    pass

class Scenario:
    @staticmethod
    def from_file(path):
        with open(path, "r") as f:
            return Scenario(f)

    def __init__(self, f):
        danger_line = f.readline().strip()
        self.danger = list(map(int, danger_line.split(" "))) if danger_line != "" else []
        agents_line = f.readline().strip()
        self.agents = list(map(int, agents_line.split(" "))) if agents_line != "" else []
    
    def danger_coords(self, map_cols):
        return list(map(lambda coord: id_to_coords(map_cols, coord), self.danger))
    
    def agents_coords(self, map_cols):
        return list(map(lambda coord: id_to_coords(map_cols, coord), self.agents))


def parse(f):
    rows, cols = __parse_header(f)
    grid = f.readlines()
    g = nx.Graph()
    g.graph["rows"] = rows
    g.graph["cols"] = cols
    for row, row_data in enumerate(grid):
        for col, field in enumerate(row_data.strip()):
            if field == "@":
                continue
            field_id = coords_to_id(cols, row, col)
            g.add_node(field_id)
            g.nodes[field_id]["dangerous"] = False
            if row != 0 and grid[row-1][col] != "@":
                g.add_edge(field_id, coords_to_id(cols, row-1, col))
            if row != rows - 1 and grid[row+1][col] != "@":
                g.add_edge(field_id, coords_to_id(cols, row+1, col))
            if col != 0 and grid[row][col - 1] != "@":
                g.add_edge(field_id, coords_to_id(cols, row, col - 1))
            if col != cols - 1 and grid[row][col+1] != "@":
                g.add_edge(field_id, coords_to_id(cols, row, col + 1))
    return g

def __parse_header(f):
    if f.readline().strip() != "type octile":
        raise ParseError("Invalid map type")
    x = int(f.readline().strip().split(" ")[1])
    y = int(f.readline().strip().split(" ")[1])
    if f.readline().strip() != "map":
        raise ParseError("Invalid map header end")
    return (x, y)
