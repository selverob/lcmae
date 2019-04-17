import random
from typing import List

from graph.reservation_graph import ReservationGraph, Reservation, ReservationNode
from level import Level
from .agent_factory import AgentFactory


def plan_evacuation(level: Level, random_seed=42, debug=True) -> List[List[int]]:
    random.seed(random_seed)
    reservations = ReservationGraph(level.g)
    factory = AgentFactory(level, reservations, debug=debug)
    agents = [factory.from_scenario(agent) for agent in level.scenario.agents]
    for agent in agents:
        for i in range(agent.lookahead):
            n = agent.pos.incremented_t(i)
            reservations.reserve(Reservation(n, agent.id, 2))
            agent.next_path.append(n)
    safe = set([agent.id for agent in agents if agent.is_safe()])
    endangered = set([agent.id for agent in agents if not agent.is_safe()])
    # Time is watched independently by agents but this variable makes
    # debugging easier
    t = 0
    deadlock_timer = 0
    while deadlock_timer < 15 and endangered:
        deadlock_timer += 1
        endangered_order = list(endangered)
        newly_safe = []
        newly_endangered = []
        random.shuffle(endangered_order)
        for i in endangered_order:
            agents[i].step()
            if len(agents[i].taken_path) < 2 or agents[i].taken_path[-1].pos() != agents[i].taken_path[-2].pos():
                deadlock_timer = 0
            if agents[i].is_safe():
                newly_safe.append(i)
        safe_order = list(safe)
        random.shuffle(safe_order)
        for i in safe_order:
            agents[i].step()
            if len(agents[i].taken_path) < 2 or agents[i].taken_path[-1].pos() != agents[i].taken_path[-2].pos():
                deadlock_timer = 0
            if not agents[i].is_safe():
                newly_endangered.append(i)
        for a in newly_safe:
            endangered.remove(a)
            safe.add(a)
        for a in newly_endangered:
            safe.remove(a)
            endangered.add(a)
        t += 1
    return [list(map(ReservationNode.pos, agent.taken_path)) for agent in agents]
