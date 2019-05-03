"""
Evacuation planning based on network flow algorithms.
"""

from __future__ import annotations
from collections import deque
from itertools import groupby
from sys import stderr
from typing import Dict, List, Tuple, NamedTuple
import networkx as nx

from .level import Level
from .graph.reservation_graph import ReservationGraph, ReservationNode, Reservation


class _NodeAdder:
    def __init__(self, g: nx.Graph):
        self.next_id = 0
        self.g = g

    def add(self, label=None) -> int:
        curr_id = self.next_id
        self.g.add_node(curr_id)
        if label:
            self.g.nodes[curr_id]["label"] = label
        self.next_id += 1
        return curr_id

    def node_clones(self, g: nx.Graph, label=None) -> Dict[int, int]:
        return {n: self.add(label=f"{n}-{label}") for n in g.node}


class NodeInfo(NamedTuple):
    id: int
    t: int
    type: int


IN = 0
OUT = 1


def get_info(expansion_records: List[Tuple[Dict[int, int], Dict[int, int]]]) -> Dict[int, NodeInfo]:
    res: Dict[int, NodeInfo] = {}
    for t, (ins, outs) in enumerate(expansion_records):
        for n in ins:
            res[ins[n]] = NodeInfo(n, t, IN)
        for n in outs:
            res[outs[n]] = NodeInfo(n, t, OUT)
    return res


def expand(lvl: Level, time: int) -> Tuple[nx.DiGraph, List[Tuple[Dict[int, int], Dict[int, int]]]]:
    """Time-expand the graph underlying the given level"""
    exp_g = nx.DiGraph()
    adder = _NodeAdder(exp_g)
    source = adder.add("src")
    sink = adder.add("sink")
    inputs = adder.node_clones(lvl.g, "0i")
    node_id_records = []
    outputs: Dict[int, int] = {}
    for agent in lvl.scenario.agents:
        exp_g.add_edge(source, inputs[agent.origin], capacity=1)
    for t in range(0, time):
        outputs = adder.node_clones(lvl.g, f"{t}o")
        for k in inputs:
            exp_g.add_edge(inputs[k], outputs[k], capacity=1)
        node_id_records.append((inputs, outputs))
        if t < time - 1:
            inputs = adder.node_clones(lvl.g, f"{t+1}i")
            for k in inputs:
                exp_g.add_edge(outputs[k], inputs[k], capacity=1)
            for edge in lvl.g.edges:
                exp_g.add_edge(outputs[edge[0]], inputs[edge[1]], capacity=1)
                exp_g.add_edge(outputs[edge[1]], inputs[edge[0]], capacity=1)
        else:
            for k in outputs:
                if lvl.is_safe(k):
                    exp_g.add_edge(outputs[k], sink, capacity=1)
    return (exp_g, node_id_records)


def follow_path(start: int, flow_dict: Dict[int, Dict[int, int]], info: Dict[int, NodeInfo]) -> List[int]:
    """Follow a path of a single agent starting at node `start` through the graph flow"""
    current_node = start
    path = []
    while current_node in info:
        current_info = info[current_node]
        current_dict = flow_dict[current_node]
        if current_info.type == OUT:
            path.append(current_info.id)
        for n in current_dict:
            if current_dict[n] > 0:
                current_node = n
                break
    return path


def reconstruct(lvl: Level, flow_dict: Dict[int, Dict[int, int]], info: Dict[int, NodeInfo]) -> List[List[int]]:
    """Reconstruct agent paths from the given flow and node information"""
    paths: List[List[int]] = [[]] * len(lvl.scenario.agents)
    start_flows = flow_dict[0]
    agent_starts = {agent.origin: i for i, agent in enumerate(lvl.scenario.agents)}
    for n in start_flows:
        if start_flows[n] > 0:
            agent = agent_starts[info[n].id]
            paths[agent] = follow_path(n, flow_dict, info)
    return paths


def extend(path: List[int], t: int) -> List[int]:
    return path + ([path[-1]] * (t - len(path)))


def annotate_with_flow(g: nx.DiGraph, flow_dict: Dict[int, Dict[int, int]]):
    for u in flow_dict:
        flows = flow_dict[u]
        for v in flows:
            g.edges[(u, v)]["flow"] = flows[v]


def drawable_graph(g: nx.DiGraph) -> nx.DiGraph:
    drawable = nx.DiGraph()
    for u, v in g.edges:
        u_label = g.node[u]["label"]
        v_label = g.node[v]["label"]
        drawable.add_edge(u_label, v_label)#, label=g.edges[(u, v)]["flow"])
    return drawable


def flow_at_time(lvl: Level, t: int):
    """Find the maximum flow in a graph expanded for t"""
    exp_g, node_ids = expand(lvl, t)
    flow_val, flow_dict = nx.maximum_flow(exp_g, 0, 1)
    return flow_val, flow_dict, node_ids


class FlowAgent():
    def __init__(self, level: Level, reservations: ReservationGraph, agents: List[FlowAgent], id: int, original_path: List[int], debug: bool):
        self.level = level
        self.reservations = reservations
        self.agents = agents
        self.id = id
        self.debug = debug
        self.queue = deque(original_path)
        self.path: List[int] = []

    def step(self):
        if self.done():
            return self._stay()
        rn = ReservationNode(self.queue[0], len(self.path) + 1)
        if self.reservable(rn):
            self.path.append(self.queue.popleft())
            self.reservations.reserve(Reservation(rn, self.id, 1))
            self.reservations.reserve(Reservation(rn.incremented_t(), self.id, 0))
        else:
            self._handle_block(rn)

    def _stay(self):
        pos = self.path[-1]
        self.path.append(pos)
        rn = ReservationNode(pos, len(self.path))
        self.reservations.reserve(Reservation(rn, self.id, 0))
        self.reservations.reserve(Reservation(rn.incremented_t(), self.id, 0))

    def _handle_block(self, rn):
        reservation = self.reservations.get(rn)
        a = self.agents[reservation.agent]
        deadlocked = len(a.queue) > 0 and a.queue[0] == self.path[-1] and self.queue[0] == a.path[-1]
        if deadlocked:
            a.queue, self.queue = self.queue, a.queue
            return self._stay()
        if not a.done() or rn.pos() != a.path[-1]:
            return self._stay()
        if self.debug:
            print(f"Swapping {self.id} and {a.id} (blocked at {a.path[-1]}, t={len(self.path) + 1})", file=stderr)
        self.queue.popleft()
        a.queue = self.queue
        self.queue = deque([a.path[-1]])
        self._stay()

    def done(self):
        return len(self.queue) == 0 #or (self.path and self.queue[0] == self.path[-1])

    def reservable(self, node: ReservationNode) -> bool:
        reservation = self.reservations.get(node)
        return reservation is None or reservation.agent == self.id


def postprocess_paths(lvl: Level, paths: List[List[int]], debug: bool) -> List[List[int]]:
    """Makes agents trying to move into occupied vertices wait for another turn."""
    reservations = ReservationGraph(lvl.g)
    agents: List[FlowAgent] = []
    for i, path in enumerate(paths):
        agents.append(FlowAgent(lvl, reservations, agents, i, path, debug))
    i = 0
    while any(map(lambda a: not a.done(), agents)):
        for agent in agents:
            agent.step()
    return [agent.path for agent in agents]


class Solution(NamedTuple):
    flow: int
    flow_dict: Dict
    node_ids: List[Tuple[Dict[int, int], Dict[int, int]]]
    t: int


def plan_evacuation(lvl: Level, postprocess=False, debug=True) -> List[List[int]]:
    best_sol = Solution(0, {}, [], 0)
    highest_wrong = 0
    t = len(lvl.scenario.agents)
    while True:
        if debug:
            print(f"Trying {t} as makespan", file=stderr)
        flow_val, flow_dict, node_ids = flow_at_time(lvl, t)
        if flow_val == len(lvl.scenario.agents):
            best_sol = Solution(flow_val, flow_dict, node_ids, t)
            break
        else:
            highest_wrong = t
            t += t // 2

    while True:
        if debug:
            print("Range:", highest_wrong, best_sol.t, file=stderr)
        t = highest_wrong + (best_sol.t - highest_wrong) // 2
        flow_val, flow_dict, node_ids = flow_at_time(lvl, t)
        if debug:
            print(f"t={t} maxflow={flow_val}", file=stderr)
        if flow_val == len(lvl.scenario.agents):
            best_sol = Solution(flow_val, flow_dict, node_ids, t)
            if t == highest_wrong + 1:
                break
        else:
            highest_wrong = t
            if t == best_sol.t - 1:
                break
    paths = reconstruct(lvl, best_sol.flow_dict, get_info(best_sol.node_ids))
    if postprocess:
        unblocked_paths = postprocess_paths(lvl, paths, debug)
        i = 2
        while True:
            if debug:
                print(f"Postprocessing iteration {i}", file=stderr)
            dedup = [list(map(lambda t: t[0], groupby(path))) for path in unblocked_paths]
            new_paths = postprocess_paths(lvl, dedup, debug)
            if new_paths == unblocked_paths:
                break
            unblocked_paths = new_paths
            i += 1
        return unblocked_paths
    else:
        return list(map(lambda p: extend(p, best_sol.t), paths))
