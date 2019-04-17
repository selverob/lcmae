from lcmae.agent import Agent
from graph.reservation_graph import ReservationNode
from .closest_frontier import ClosestFrontierEvacuation


class RetargetingEvacuation(ClosestFrontierEvacuation):
    def __init__(self, agent: Agent):
        super().__init__(agent)
        self.distance_with_goal = 0

    def retarget(self):
        super().retarget()
        self.distance_with_goal = 0

    def step(self) -> ReservationNode:
        if self.distance_with_goal >= 2 * self.distance_to_goal:
            self.agent.log("Waiting too long for goal, retargeting")
            old_goal = self.goal
            self.retarget()
            if self.goal != old_goal:
                self.agent.log("Found new target")
            self.replan()
        return super().step()
