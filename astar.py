from pqdict import pqdict

class AStar:
    def __init__(self, graph, agents, coord_func):
        if len(agents) != 1:
            raise ValueError("Only a single agent allowed in A-star")
        self.g = graph
        self.pos = agents[0][0]
        self.goal = agents[0][1]
        self.get_coords = coord_func
        self.movement = self.plan()
    
    def __iter__(self):
        movement = map(lambda x: [x], self.movement)
        return movement.__iter__()
    
    def plan(self):
        closed = set()
        opened = pqdict({self.pos: 0})
        for node in self.g.nodes:
            self.g.nodes[node]["g_cost"] = float("inf")
        self.g.nodes[self.pos]["g_cost"] = 0
        while len(opened) > 0:
            curr = opened.pop()
            if curr == self.goal:
                return self.reconstruct_path()
            closed.add(curr)
            for n in set(self.g[curr].keys()) - closed:
                considered_g_cost = self.g.nodes[curr]["g_cost"] + 1
                if considered_g_cost >= self.g.nodes[n]["g_cost"]:
                    continue
                self.g.nodes[n]["g_cost"] = considered_g_cost
                self.g.nodes[n]["previous"] = curr
                f_cost = considered_g_cost + self.heur_dist(n, self.goal)
                if not n in opened:
                    opened.additem(n, f_cost)
                else:
                    opened[n] = f_cost
                
    def reconstruct_path(self):
        path = [self.goal]
        try:
            while True:
                path.append(self.g.nodes[path[-1]]["previous"])
        except: pass
        path.reverse()
        return path
                
    def heur_dist(self, x, y):
        x_coords = self.get_coords(x)
        y_coords = self.get_coords(y)
        return abs(x_coords[0] - y_coords[0]) + abs(x_coords[1] - y_coords[1])
                

