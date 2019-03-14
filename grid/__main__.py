#! /usr/bin/env python3

from sys import argv
import arcade
from level import Level
from grid.grid import Grid


def parse_paths(path: str):
    result = []
    with open(path) as f:
        lines = f.readlines()
        if lines[-1] == [""]:
            lines = lines[:-1]
        for line in lines:
            result.append(list(map(int, line.strip().split(" "))))
    return result


def check_paths(paths, level):
    path_len = len(paths[0])
    for p in paths:
        if len(p) != path_len:
            print("Not all paths have equal sizes")
            exit(1)
    for t in range(path_len):
        s = set()
        for p in paths:
            s.add(p[t])
        if len(s) != len(paths):
            print(f"Collision at time {t}")
    for agent, p in enumerate(paths):
        if level.scenario.agents[agent].origin != p[0]:
            print("Agent starts at a point different from the scenario")
        for i in range(1, len(p)):
            if p[i - 1] not in level.g[p[i]] and p[i - 1] != p[i]:
                print(f"Non-adjacent movement of agent {agent} at time {i}")


def main():
    map_path, scen_path = argv[1], argv[2]
    lvl = Level(map_path, scen_path)
    paths = None
    if len(argv) == 4:
        paths = parse_paths(argv[3])
        check_paths(paths, lvl)
    lines = []
    with open(map_path) as map_f:
        for _ in range(4):
            map_f.readline()
        lines = list(map(lambda l: l.strip(), map_f.readlines()))
    Grid(lines, lvl.scenario, paths, cell_size=10, border=0)
    arcade.run()


if __name__ == "__main__":
    main()
