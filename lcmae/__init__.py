import random
from typing import List

from graph.reservation_graph import ReservationGraph, Reservation, ReservationNode
from level import Level
from .agent_factory import AgentFactory
from .agent import Agent


def step_and_divide(agents: List[Agent]) -> (List[Agent], List[Agent]):
    random.shuffle(agents)
    endangered = []
    safe = []
    for agent in agents:
        agent.step()
        if agent.is_safe():
            safe.append(agent)
        else:
            endangered.append(agent)
    return endangered, safe


def agent_broke_deadlock(a: Agent) -> bool:
    return len(a.taken_path) < 2 or a.taken_path[-1].pos() != a.taken_path[-2].pos()


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
    safe = [agent for agent in agents if agent.is_safe()]
    endangered = [agent for agent in agents if not agent.is_safe()]
    # Time is watched independently by agents but this variable makes
    # debugging easier
    t = 0
    deadlock_timer = 0
    while deadlock_timer < 15 and endangered:
        deadlock_timer += 1
        still_endangered, newly_safe = step_and_divide(endangered)
        newly_endangered, still_safe = step_and_divide(safe)
        endangered = still_endangered + newly_endangered
        safe = still_safe + newly_safe
        if any(map(agent_broke_deadlock, safe)) or any(map(agent_broke_deadlock, endangered)):
            deadlock_timer = 0
        t += 1
    return [list(map(ReservationNode.pos, agent.taken_path)) for agent in agents]
