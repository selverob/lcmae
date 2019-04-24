import arcade
from typing import List, Optional

from evacsim.level import Level
from .grid import Grid


def start(lvl: Level, map_path: str, paths: Optional[List[List[int]]], cell_size=10, border=0):
    """Set up grid interface and start arcade's event loop."""
    lines: List[str] = []
    with open(map_path) as map_f:
        for _ in range(4):
            map_f.readline()
        lines = list(map(lambda l: l.strip(), map_f.readlines()))
    Grid(lines, lvl.scenario, paths, cell_size=cell_size, border=border)
    arcade.run()
