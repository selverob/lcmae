from sys import stderr
from typing import Dict, List, Tuple
from collections import namedtuple
import networkx as nx
from level import Level

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

NodeInfo = namedtuple("NodeInfo", ["id", "t", "type"])
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
    exp_g = nx.DiGraph()
    adder = _NodeAdder(exp_g)
    source = adder.add("src")
    sink = adder.add("sink")
    inputs = adder.node_clones(lvl.g, "0i")
    #final_outputs = {n: adder.add(f"{n}-fo") for n in lvl.g.node if lvl.is_safe(n)}
    #for fo in final_outputs:
    #    exp_g.add_edge(final_outputs[fo], sink, capacity=1)
    node_id_records = []
    outputs: Dict[int, int] = {}
    for agent_pos in lvl.scenario.agents:
        exp_g.add_edge(source, inputs[agent_pos], capacity=1)
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
    paths: List[List[int]] = [[]] * len(lvl.scenario.agents)
    start_flows = flow_dict[0]
    agent_starts = {start: agent for agent, start in enumerate(lvl.scenario.agents)}
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
        drawable.add_edge(u_label, v_label, label=g.edges[(u, v)]["flow"])
    return drawable

def evacuation_for_time(lvl: Level, t: int):
    exp_g, node_ids = expand(lvl, t)
    flow_val, flow_dict = nx.maximum_flow(exp_g, 0, 1)
    print(t, flow_val, file=stderr)
    return flow_val, flow_dict, node_ids

def plan_evacuation(lvl: Level) -> List[List[int]]:
    Solution = namedtuple("Solution", ["flow", "flow_dict", "node_ids", "t"])
    best_sol = Solution(0, None, None, 0)
    highest_wrong = 0
    t = len(lvl.scenario.agents)
    while True:
        flow_val, flow_dict, node_ids = evacuation_for_time(lvl, t)
        if flow_val == len(lvl.scenario.agents):
            best_sol = Solution(flow_val, flow_dict, node_ids, t)
            break
        else:
            highest_wrong = t
            t += t // 2

    while True:
        print("Range:", highest_wrong, best_sol.t, file=stderr)
        t = highest_wrong + (best_sol.t - highest_wrong) // 2
        flow_val, flow_dict, node_ids = evacuation_for_time(lvl, t)
        if flow_val == len(lvl.scenario.agents):
            best_sol = Solution(flow_val, flow_dict, node_ids, t)
            if t == highest_wrong + 1:
                break
        else:
            highest_wrong = t
            if t == best_sol.t - 1:
                break
    paths = reconstruct(lvl, best_sol.flow_dict, get_info(best_sol.node_ids))
    return list(map(lambda p: extend(p, best_sol.t), paths))
