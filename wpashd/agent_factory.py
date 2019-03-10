import wpashd.evacuation as evac
from level import Level
from graph.reservation_graph import ReservationGraph
from .agent import Agent

class AgentFactory():
    def __init__(self, level: Level, reservations: ReservationGraph, debug=True):
        self.level = level
        self.reservations = reservations
        self.debug = debug
        self.curr_id = -1

    def intelligent_agent(self) -> Agent:
        return self._agent_with_evac_class(evac.RetargetingEvacuation)

    def closest_frontier_agent(self) -> Agent:
        return self._agent_with_evac_class(evac.ClosestFrontierEvacuation)

    def _agent_with_evac_class(self, cls) -> Agent:
        self.curr_id += 1
        return Agent(self.curr_id, self.level, self.reservations, cls, debug=self.debug)
