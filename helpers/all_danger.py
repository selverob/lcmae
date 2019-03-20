from sys import argv
from typing import List
from level import Level


def non_walls_from(level: Level, start: int, every=1) -> List[int]:
    non_walls = []
    for n in range(min_danger, level.g.graph["rows"] * level.g.graph["cols"], every):
        if n in level.g.nodes:
            non_walls.append(n)
    return non_walls


if __name__ == "__main__":
    lvl = Level(argv[1], "empty.scen")
    min_danger = int(argv[2])
    print(*non_walls_from(lvl, min_danger), sep=" ")
    agents = map(lambda a: f"{a}r", non_walls_from(lvl, min_danger, int(argv[3])))
    print(*list(agents), sep=" ")