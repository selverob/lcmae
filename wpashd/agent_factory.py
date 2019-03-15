import wpashd.evacuation as evac
from level import Level, Scenario
from graph.reservation_graph import ReservationGraph
from graph.nx_graph import NxNode
from .agent import Agent


class AgentFactory():
    def __init__(self, level: Level, reservations: ReservationGraph, debug=True):
        self.level = level
        self.reservations = reservations
        self.debug = debug
        self.curr_id = -1

    def retargeting_agent(self) -> Agent:
        return self._agent_with_evac_class(evac.RetargetingEvacuation)

    def closest_frontier_agent(self) -> Agent:
        return self._agent_with_evac_class(evac.ClosestFrontierEvacuation)

    def panicked_agent(self) -> Agent:
        return self._agent_with_evac_class(evac.PanicEvacuation)

    def static_target_agent(self, target: int) -> Agent:
        return self._agent_with_evac_class(lambda agent: evac.FixedTargetEvacuation(agent, NxNode(target)))

    def _agent_with_evac_class(self, cls) -> Agent:
        self.curr_id += 1
        return Agent(self.curr_id, self.level, self.reservations, cls, debug=self.debug)

    def from_scenario(self, scn_agent: Scenario.Agent) -> Agent:
        t = scn_agent.type
        if t == Scenario.AgentType.RETARGETING:
            return self.retargeting_agent()
        elif t == Scenario.AgentType.CLOSEST_FRONTIER:
            return self.closest_frontier_agent()
        elif t == Scenario.AgentType.STATIC:
            return self.static_target_agent(scn_agent.goal)
        elif t == Scenario.AgentType.PANICKED:
            return self.panicked_agent()
