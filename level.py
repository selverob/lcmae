import re
from collections import namedtuple
from enum import Enum
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


AgentType = Enum("AgentType", "RETARGETING CLOSEST_FRONTIER STATIC PANICKED")
Agent = namedtuple("Agent", ["type", "origin", "goal"])


class Scenario:
    agent_re = re.compile("(\\d+)(.)(\\d+)?")
    _typeMap = {"r": AgentType.RETARGETING, "f": AgentType.CLOSEST_FRONTIER, "s": AgentType.STATIC, "p": AgentType.PANICKED}
    _typeChars = {typ: code for code, typ in _typeMap.items()}

    @staticmethod
    def from_file(path: str):
        with open(path, "r") as f:
            s = Scenario([], [])
            danger_line = f.readline().strip()
            s.danger = list(
                map(int, danger_line.split(" "))) if danger_line != "" else []
            agents_line = f.readline().strip().split(" ")
            if agents_line == [""]:
                return s
            for agent_desc in agents_line:
                parsed_desc = Scenario.agent_re.fullmatch(agent_desc)
                s.agents.append(Agent(
                    Scenario._typeMap[parsed_desc[2]],
                    int(parsed_desc[1]),
                    int(parsed_desc[3]) if parsed_desc[3] is not None else None))
            return s

    def __init__(self, danger, agents):
        self.agents: List[Agent] = agents
        self.danger: List[int] = danger

    def danger_coords(self, map_cols: int) -> List[Tuple[int, int]]:
        return list(
            map(lambda coord: id_to_coords(map_cols, coord), self.danger))

    def agents_coords(self, map_cols: int) -> List[Tuple[int, int]]:
        return list(
            map(lambda agent: id_to_coords(map_cols, agent.origin), self.agents))

    def agent_str(self, agent: Agent):
        res = f"{agent.origin}{Scenario._typeChars[agent.type]}"
        if agent.goal is not None:
            res += str(agent.goal)
        return res

    def write(self, f):
        print(*self.danger, file=f)
        print(*map(lambda a: self.agent_str(a), self.agents), file=f)


class Level:
    def __init__(self, map_path: str, scenario_path: str):
        with open(map_path) as map_f:
            self.__parse_header(map_f)
            self.__parse_map(map_f)
            self.scenario = Scenario.from_file(scenario_path)
            self.__add_danger()
            self.__add_frontier()
            for n in self.g.nodes:
                self.g.nodes[n]["reservations"] = set()

    def coords_to_id(self, row, col):
        return coords_to_id(self.cols, row, col)

    def id_to_coords(self, node_id):
        return id_to_coords(self.cols, node_id)

    def is_safe(self, node_id) -> bool:
        return not self.g.nodes[node_id]["dangerous"]

    def __add_danger(self):
        for n in self.scenario.danger:
            if n in self.g.nodes:
                self.g.nodes[n]["dangerous"] = True

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
                if row != 0 and grid[row - 1][col] != "@":
                    self.g.add_edge(
                        field_id, coords_to_id(self.cols, row - 1, col))
                if row != self.rows - 1 and grid[row + 1][col] != "@":
                    self.g.add_edge(
                        field_id, coords_to_id(self.cols, row + 1, col))
                if col != 0 and grid[row][col - 1] != "@":
                    self.g.add_edge(
                        field_id, coords_to_id(self.cols, row, col - 1))
                if col != self.cols - 1 and grid[row][col + 1] != "@":
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
