from enum import Enum
from operator import attrgetter


class SearchOptimization(Enum):
    breadth_first = 0
    depth_first = 1
    greedy = 2
    a_star = 3


class Result(Enum):
    no_solution = 0
    solution_found = 1
    step_done = 2


class TreeSearch:
    def __init__(self, start_node, end_node, optimization, get_all_connected_nodes, report_open_node, report_closed_node):
        self._end_node = TreeNode(end_node[0],
                                  end_node[1],
                                  previous_node=None,
                                  previous_costs=0,
                                  estimated_costs=0)
        self._optimization = optimization
        self._get_all_connected_nodes = get_all_connected_nodes
        self._report_open_node = report_open_node
        self._report_closed_node = report_closed_node
        
        self._step_cost = 1
        self._open_node_list = [TreeNode(start_node[0],
                                         start_node[1],
                                         previous_node=None,
                                         previous_costs=0,
                                         estimated_costs=abs(self._end_node.x - start_node[0]) + abs(self._end_node.y - start_node[1]))]
        
    def run_step(self):
        if len(self._open_node_list) == 0:
            return Result.no_solution
        
        if self._optimization == SearchOptimization.breadth_first:
            self._open_node_list.sort(key=attrgetter("previous_costs"), reverse=True)
        elif self._optimization == SearchOptimization.depth_first:
            self._open_node_list.sort(key=attrgetter("previous_costs"), reverse=False)
        elif self._optimization == SearchOptimization.greedy:
            self._open_node_list.sort(key=attrgetter("estimated_costs", "total_costs"), reverse=True)
        elif self._optimization == SearchOptimization.a_star:
            self._open_node_list.sort(key=attrgetter("total_costs", "estimated_costs"), reverse=True)
            
        actual_node_to_expand = self._open_node_list.pop()
        
        if actual_node_to_expand == self._end_node:
            return Result.solution_found
        
        self._report_closed_node(actual_node_to_expand.x, actual_node_to_expand.y)

        for x, y in self._get_all_connected_nodes(actual_node_to_expand.x, actual_node_to_expand.y):
            self._report_open_node(x, y)
            node = TreeNode(x, 
                            y, 
                            previous_node=actual_node_to_expand,
                            previous_costs=actual_node_to_expand.previous_costs + self._step_cost,
                            estimated_costs=abs(self._end_node.x - x) + abs(self._end_node.y - y))
            
            if node == self._end_node:
                self._end_node = node
            
            self._open_node_list.append(node)

        return Result.step_done
    
    def get_founded_path(self):
        path = []
        
        actual_node = self._end_node.previous_node
        
        while actual_node is not None:
            path.append((actual_node.x, actual_node.y))
            actual_node = actual_node.previous_node
        
        return path[:-1]

    
class TreeNode:
    def __init__(self, x, y, previous_node, previous_costs, estimated_costs):
        self.x = x
        self.y = y
        self.previous_node = previous_node
        self.previous_costs = previous_costs
        
        self.estimated_costs = estimated_costs
        self.total_costs = previous_costs + estimated_costs
        
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
