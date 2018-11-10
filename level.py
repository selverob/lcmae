from typing import List, Tuple
import networkx as nx


def coords_to_id(cols, row, col):
    return row * cols + col


def id_to_coords(cols, node_id):
    return (node_id // cols, node_id % cols)


class ParseError(Exception):
    pass


class NoPathFound(Exception):
    pass


class Scenario:
    @staticmethod
    def from_file(path: str):
        with open(path, "r") as f:
            return Scenario(f)

    def __init__(self, f):
        danger_line = f.readline().strip()
        self.danger = list(
            map(int, danger_line.split(" "))) if danger_line != "" else []
        agents_line = f.readline().strip()
        self.agents = list(
            map(int, agents_line.split(" "))) if agents_line != "" else []

    def danger_coords(self, map_cols: int) -> List[Tuple[int, int]]:
        return list(
            map(lambda coord: id_to_coords(map_cols, coord), self.danger))

    def agents_coords(self, map_cols: int) -> List[Tuple[int, int]]:
        return list(
            map(lambda coord: id_to_coords(map_cols, coord), self.agents))


class Level:
    def __init__(self, map_path: str, scenario_path: str):
        with open(map_path) as map_f:
            self.__parse_header(map_f)
            self.__parse_map(map_f)
            self.scenario = Scenario.from_file(scenario_path)
            self.__add_danger()
            # self.__add_goal()
            self.__add_frontier()

    def coords_to_id(self, row, col):
        return coords_to_id(self.cols, row, col)

    def id_to_coords(self, node_id):
        return id_to_coords(self.cols, node_id)

    def __add_danger(self):
        for n in self.scenario.danger:
            self.g.nodes[n]["dangerous"] = True

    # def __add_goal(self):
    #     goal_node = max(self.g.nodes) + 1
    #     self.g.add_node(goal_node)
    # def __add_goal(self):
    #     goal_node = max(self.g.nodes) + 1
    #     self.g.add_node(goal_node)
    #     for node in self.g.nodes:
    #         if not self.g.nodes[node]["dangerous"]:
    #             self.g.add_edge(node, goal_node)
    #     self.goal = goal_node
    #     for node in self.g.nodes:
    #         if not self.g.nodes[node]["dangerous"]:
    #             self.g.add_edge(node, goal_node)
    #     self.goal = goal_node

    def __add_frontier(self):
        self.frontier = []
        for (u, v) in self.g.edges:
            if self.g.nodes[u]["dangerous"] != self.g.nodes[v]["dangerous"]:
                if not self.g.nodes[u]["dangerous"]:
                    self.frontier.append(u)
                else:
                    self.frontier.append(v)

    def __parse_map(self, f):
        grid = f.readlines()
        self.g = nx.Graph()
        self.g.graph["rows"] = self.rows
        self.g.graph["cols"] = self.cols
        for row, row_data in enumerate(grid):
            for col, field in enumerate(row_data.strip()):
                if field == "@":
                    continue
                field_id = coords_to_id(self.cols, row, col)
                self.g.add_node(field_id)
                self.g.nodes[field_id]["dangerous"] = False
                if row != 0 and grid[row-1][col] != "@":
                    self.g.add_edge(
                        field_id, coords_to_id(self.cols, row-1, col))
                if row != self.rows - 1 and grid[row+1][col] != "@":
                    self.g.add_edge(
                        field_id, coords_to_id(self.cols, row+1, col))
                if col != 0 and grid[row][col - 1] != "@":
                    self.g.add_edge(
                        field_id, coords_to_id(self.cols, row, col - 1))
                if col != self.cols - 1 and grid[row][col+1] != "@":
                    self.g.add_edge(
                        field_id, coords_to_id(self.cols, row, col + 1))
        return self.g

    def __parse_header(self, f):
        if f.readline().strip() != "type octile":
            raise ParseError("Invalid map type")
        self.rows = int(f.readline().strip().split(" ")[1])
        self.cols = int(f.readline().strip().split(" ")[1])
        if f.readline().strip() != "map":
            raise ParseError("Invalid map header end")
