import random
from enum import Enum
from itertools import product
from operator import attrgetter
from argparse import ArgumentParser, RawTextHelpFormatter
import contextlib
with contextlib.redirect_stdout(None):
    import pygame


class Game:
    class TileType(Enum):
        empty = 0
        wall = 1
        start = 2
        end = 3
        open = 4
        closed = 5
        path = 6
    
    def __init__(self, width, height, percentage_of_wall_fields, fps, optimization, seed):
        random.seed(seed)
        pygame.init()
        pygame.display.set_caption("pyPathFindingDemo")
        
        self._size = self._width, self._height = width, height
        self._fps = fps
        
        self._screen = pygame.display.set_mode(self._size)
        self._clock = pygame.time.Clock()

        self._empty_tile = pygame.image.load(r"Textures\TileWhite.png").convert()
        self._wall_tile = pygame.image.load(r"Textures\TileBlack.png").convert()
        self._start_tile = pygame.image.load(r"Textures\TileStart.png").convert()
        self._end_tile = pygame.image.load(r"Textures\TileEnd.png").convert()
        self._open_tile = pygame.image.load(r"Textures\TileGreen.png").convert()
        self._closed_tile = pygame.image.load(r"Textures\TileRed.png").convert()
        self._path_tile = pygame.image.load(r"Textures\TileBlue.png").convert()
        
        self._tile_mapping = {Game.TileType.empty: self._empty_tile,
                              Game.TileType.wall: self._wall_tile,
                              Game.TileType.start: self._start_tile,
                              Game.TileType.end: self._end_tile,
                              Game.TileType.open: self._open_tile,
                              Game.TileType.closed: self._closed_tile,
                              Game.TileType.path: self._path_tile}
        
        self._number_of_tiles_x = int(self._width / self._empty_tile.get_width())
        self._number_of_tiles_y = int(self._height / self._empty_tile.get_height())

        self._board = [[None for _ in range(self._number_of_tiles_y)] for _ in range(self._number_of_tiles_x)]
        
        for x, y in product(range(self._number_of_tiles_x), range(self._number_of_tiles_y)):
            if x == 0 or y == 0 or x == self._number_of_tiles_x - 1 or y == self._number_of_tiles_y - 1 or random.random() < percentage_of_wall_fields:
                self._board[x][y] = Game.TileType.wall
            else:
                self._board[x][y] = Game.TileType.empty
        
        self._start_node = (random.randint(1, self._number_of_tiles_x - 2), random.randint(1, self._number_of_tiles_y - 2))
        self._board[self._start_node[0]][self._start_node[1]] = Game.TileType.start
        
        self._end_node = (random.randint(1, self._number_of_tiles_x - 2), random.randint(1, self._number_of_tiles_y - 2))
        self._board[self._end_node[0]][self._end_node[1]] = Game.TileType.end
        
        self._search_algorithm = TreeSearch(self._start_node, 
                                            self._end_node, 
                                            optimization, 
                                            get_all_connected_nodes=self.get_all_connected_empty_tiles,
                                            report_open_node=self.report_open_node,
                                            report_closed_node=self.report_closed_node)
        
    def get_all_connected_empty_tiles(self, x, y):
        node_list = []

        all_connected_tiles = ((x - 1, y),
                               (x + 1, y),
                               (x, y + 1),
                               (x, y - 1))

        for x, y in all_connected_tiles:
            if x > 0 and x < self._number_of_tiles_x - 1 and y > 0 and y < self._number_of_tiles_y - 1:
                if self._board[x][y] == Game.TileType.empty or self._board[x][y] == Game.TileType.end:
                    node_list.append((x, y))

        return node_list
    
    def report_open_node(self, x, y):
        if (x != self._start_node[0] or y != self._start_node[1]) and \
                (x != self._end_node[0] or y != self._end_node[1]):
            self._board[x][y] = Game.TileType.open
    
    def report_closed_node(self, x, y):
        if (x != self._start_node[0] or y != self._start_node[1]) and \
                (x != self._end_node[0] or y != self._end_node[1]):
            self._board[x][y] = Game.TileType.closed
        
    def run(self):
        finished = False
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
        
            if not finished:
                result = self._search_algorithm.run_step() 
                finished = result in (TreeSearch.Result.no_solution, TreeSearch.Result.solution_found)
                
                if result == TreeSearch.Result.solution_found:
                    for x, y in self._search_algorithm.get_founded_path():
                        self._board[x][y] = Game.TileType.path
                        
                self._screen.fill([0, 255, 255])
                        
                for x, y in product(range(self._number_of_tiles_x), range(self._number_of_tiles_y)):
                    tile = self._tile_mapping[self._board[x][y]]
                    self._screen.blit(tile, 
                                      tile.get_rect().move(x * tile.get_width(), y * tile.get_height())) 
            
                pygame.display.flip()
                
            self._clock.tick(self._fps)


class TreeSearch:
    class SearchOptimization(Enum):
        breadth_first = 0
        depth_first = 1
        greedy = 2
        a_star = 3
    
    class Result(Enum):
        no_solution = 0
        solution_found = 1
        step_done = 2
        
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
    
    def __init__(self, start_node, end_node, optimization, get_all_connected_nodes, report_open_node, report_closed_node):
        self._end_node = TreeSearch.TreeNode(end_node[0],
                                             end_node[1],
                                             previous_node=None,
                                             previous_costs=0,
                                             estimated_costs=0)
        self._optimization = optimization
        self._get_all_connected_nodes = get_all_connected_nodes
        self._report_open_node = report_open_node
        self._report_closed_node = report_closed_node
        
        self._step_cost = 1
        self._open_node_list = [TreeSearch.TreeNode(start_node[0],
                                                    start_node[1],
                                                    previous_node=None,
                                                    previous_costs=0,
                                                    estimated_costs=abs(self._end_node.x - start_node[0]) + abs(self._end_node.y - start_node[1]))]
        
    def run_step(self):
        if len(self._open_node_list) == 0:
            return TreeSearch.Result.no_solution
        
        if self._optimization == TreeSearch.SearchOptimization.breadth_first:
            self._open_node_list.sort(key=attrgetter("previous_costs"), reverse=True)
        elif self._optimization == TreeSearch.SearchOptimization.depth_first:
            self._open_node_list.sort(key=attrgetter("previous_costs"), reverse=False)
        elif self._optimization == TreeSearch.SearchOptimization.greedy:
            self._open_node_list.sort(key=attrgetter("estimated_costs", "total_costs"), reverse=True)
        elif self._optimization == TreeSearch.SearchOptimization.a_star:
            self._open_node_list.sort(key=attrgetter("total_costs", "estimated_costs"), reverse=True)
            
        actual_node_to_expand = self._open_node_list.pop()
        
        if actual_node_to_expand == self._end_node:
            return TreeSearch.Result.solution_found
        
        self._report_closed_node(actual_node_to_expand.x, actual_node_to_expand.y)

        for x, y in self._get_all_connected_nodes(actual_node_to_expand.x, actual_node_to_expand.y):
            self._report_open_node(x, y)
            node = TreeSearch.TreeNode(x, 
                                       y, 
                                       previous_node=actual_node_to_expand,
                                       previous_costs=actual_node_to_expand.previous_costs + self._step_cost,
                                       estimated_costs=abs(self._end_node.x - x) + abs(self._end_node.y - y))
            
            if node == self._end_node:
                self._end_node = node
            
            self._open_node_list.append(node)

        return TreeSearch.Result.step_done
    
    def get_founded_path(self):
        path = []
        
        actual_node = self._end_node.previous_node
        
        while actual_node is not None:
            path.append((actual_node.x, actual_node.y))
            actual_node = actual_node.previous_node
        
        return path[:-1]


if __name__ == "__main__":
    argument_parser = ArgumentParser(description="""
pyPathFindingDemo:
    - pyPathFindingDemo is a little python program which implements some tree search algorithms to solve a path finding problem visualized with the pygame framework.
    - Create a randomly generated playground with walls, start and end point and search a path from start to end with the given optimization strategy.
    - See readme.md for more informations.""", 
                                     epilog="https://github.com/WinterWonderland/pyPathFindingDemo",
                                     formatter_class=RawTextHelpFormatter)
    argument_parser.add_argument("--width",
                                 metavar="",
                                 type=int,
                                 default=1920,
                                 help="The width of the game window (minimum=32, default=1920 [Full HD])")
    argument_parser.add_argument("--height",
                                 metavar="",
                                 type=int,
                                 default=1080,
                                 help="The width of the game window (minimum=32, default=1080 [Full HD])")
    argument_parser.add_argument("--walls",
                                 metavar="",
                                 type=float,
                                 default=1 / 3,
                                 help="Percentage of wall tiles to generate (minimum=0, maximum=1, default=1/3)")
    argument_parser.add_argument("--fps",
                                 metavar="",
                                 type=int,
                                 default=25,
                                 help="The target frames per second to run the simulation (default=25)")
    argument_parser.add_argument("--optimization",
                                 metavar="",
                                 type=str,
                                 choices=("breadth", "depth", "greedy", "a_star"),
                                 default="a_star",
                                 help="The optimization strategy for the search algorithm [breadth, depth, greedy, a_star] (default=a_star)")
    argument_parser.add_argument("--seed",
                                 metavar="",
                                 type=int,
                                 default=None,
                                 help="A seed for the random number generator to get identical play boards")
    args = argument_parser.parse_args()
    
    if args.optimization == "breadth":
        optimization = TreeSearch.SearchOptimization.breadth_first
    elif args.optimization == "depth":
        optimization = TreeSearch.SearchOptimization.depth_first
    elif args.optimization == "greedy":
        optimization = TreeSearch.SearchOptimization.greedy
    elif args.optimization == "a_star":
        optimization = TreeSearch.SearchOptimization.a_star
        
    board = Game(width=args.width,
                 height=args.height, 
                 percentage_of_wall_fields=args.walls, 
                 fps=args.fps,
                 optimization=optimization,
                 seed=args.seed)
    board.run()
