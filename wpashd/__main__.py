import random
from sys import stderr, argv
from graph.reservation_graph import ReservationGraph, Reservation, ReservationNode
from wpashd.agent import Agent
from level import Level

def plan_evacuation(level, random_seed=42):
    random.seed(random_seed)
    reservations = ReservationGraph(level.g)
    agents = [Agent(i, level, reservations) for i in range(len(level.scenario.agents))]
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
    #while deadlock_timer < 15:
    while t < 100:
        print(f"Safe: {safe}", file=stderr)
        print(f"Endangered: {endangered}", file=stderr)
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
        for agent in newly_safe:
            endangered.remove(agent)
            safe.add(agent)
        for agent in newly_endangered:
            safe.remove(agent)
            endangered.add(agent)
        t += 1
    return [list(map(ReservationNode.pos, agent.taken_path)) for agent in agents]


def main():
    map_path, scen_path = argv[1], argv[2]
    lvl = Level(map_path, scen_path)
    for n in lvl.g.nodes:
        lvl.g.nodes[n]["reservations"] = set()
    if len(lvl.frontier) == 0:
        print("No passage to safety exists!", file=stderr)
        exit(2)
    paths = plan_evacuation(lvl)
    for agent_id, path in enumerate(paths):
        num_strings = ["{:02d}".format(n) for n in path]
        print(*num_strings)
        if path[-1] in lvl.scenario.danger:
            print("Agent", agent_id, "could not evacuate. He dead.",
                  file=stderr)


if __name__ == "__main__":
    main()
