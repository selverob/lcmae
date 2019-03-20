from sys import argv
from typing import List, Tuple
from networkx import Graph
from level import Level


def neighbors_frontier(g: Graph, node: int, frontier: List[int]) -> bool:
    for u in frontier:
        if node in g.neighbors(u):
            return True
    return False


def frontiers_for_lvl(lvl: Level) -> List[List[int]]:
    frontiers: List[List[int]] = []
    for u in lvl.frontier:
        for frontier in frontiers:
            if neighbors_frontier(lvl.g, u, frontier):
                frontier.append(u)
                break
        else:
            frontiers.append([u])
    return frontiers


def manhattan(u: Tuple[int, int], v: Tuple[int, int]) -> int:
    return abs(u[0] - v[0]) + abs(u[1] - v[1])


def closest_node_to(node_coords: Tuple[int, int], frontier_coords: List[Tuple[int, int]]) -> Tuple[int, int]:
    return min(frontier_coords, key=lambda f: manhattan(node_coords, f))


map_path, scen_path = argv[1], argv[2]
lvl = Level(map_path, scen_path)
frontiers = frontiers_for_lvl(lvl)
longest = max(frontiers, key=lambda f: len(f))
frontier_coords = list(map(lvl.id_to_coords, longest))
agent_descs = [f"{agent.origin}s{lvl.coords_to_id(*closest_node_to(lvl.id_to_coords(agent.origin), frontier_coords))}"
               for agent in lvl.scenario.agents]
print(*lvl.scenario.danger)
print(*agent_descs)
