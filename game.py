import random
from enum import Enum
from itertools import product
import contextlib
from search_algorithms import TreeSearch, SearchOptimization, Result  # @UnusedImport
with contextlib.redirect_stdout(None):
    import pygame


class TileType(Enum):
    empty = 0
    wall = 1
    start = 2
    end = 3
    open = 4
    closed = 5
    path = 6


class Board:
    def __init__(self, width, height, percentage_of_wall_fields, fps, optimization):
        
        self._size = self._width, self._height = width, height
        self._fps = fps
        
        pygame.init()
        self._screen = pygame.display.set_mode(self._size)
        self._clock = pygame.time.Clock()

        self._empty_tile = pygame.image.load(r"Textures\TileWhite.png").convert()
        self._wall_tile = pygame.image.load(r"Textures\TileBlack.png").convert()
        self._start_tile = pygame.image.load(r"Textures\TileStart.png").convert()
        self._end_tile = pygame.image.load(r"Textures\TileEnd.png").convert()
        self._open_tile = pygame.image.load(r"Textures\TileGreen.png").convert()
        self._closed_tile = pygame.image.load(r"Textures\TileRed.png").convert()
        self._path_tile = pygame.image.load(r"Textures\TileBlue.png").convert()
        
        self._tile_mapping = {TileType.empty: self._empty_tile,
                              TileType.wall: self._wall_tile,
                              TileType.start: self._start_tile,
                              TileType.end: self._end_tile,
                              TileType.open: self._open_tile,
                              TileType.closed: self._closed_tile,
                              TileType.path: self._path_tile}
        
        self._number_of_tiles_x = int(self._width / self._empty_tile.get_width())
        self._number_of_tiles_y = int(self._height / self._empty_tile.get_height())

        self._tiles = [[None for _ in range(self._number_of_tiles_y)] for _ in range(self._number_of_tiles_x)]
        
        for x, y in product(range(self._number_of_tiles_x), range(self._number_of_tiles_y)):
            if x == 0 or y == 0 or x == self._number_of_tiles_x - 1 or y == self._number_of_tiles_y - 1 or random.random() < percentage_of_wall_fields:
                self._tiles[x][y] = TileType.wall
            else:
                self._tiles[x][y] = TileType.empty
        
        self._start_node = (random.randint(1, self._number_of_tiles_x - 2), random.randint(1, self._number_of_tiles_y - 2))
        self._tiles[self._start_node[0]][self._start_node[1]] = TileType.start
        
        self._end_node = (random.randint(1, self._number_of_tiles_x - 2), random.randint(1, self._number_of_tiles_y - 2))
        self._tiles[self._end_node[0]][self._end_node[1]] = TileType.end
        
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
                if self._tiles[x][y] == TileType.empty or self._tiles[x][y] == TileType.end:
                    node_list.append((x, y))

        return node_list
    
    def report_open_node(self, x, y):
        if (x != self._start_node[0] or y != self._start_node[1]) and \
                (x != self._end_node[0] or y != self._end_node[1]):
            self._tiles[x][y] = TileType.open
    
    def report_closed_node(self, x, y):
        if (x != self._start_node[0] or y != self._start_node[1]) and \
                (x != self._end_node[0] or y != self._end_node[1]):
            self._tiles[x][y] = TileType.closed
        
    def run(self):
        finished = False
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
        
            if not finished:
                result = self._search_algorithm.run_step() 
                finished = result in (Result.no_solution, Result.solution_found)
                
                if result == Result.solution_found:
                    for x, y in self._search_algorithm.get_founded_path():
                        self._tiles[x][y] = TileType.path
                        
                self._screen.fill([0, 255, 255])
                        
                for x, y in product(range(self._number_of_tiles_x), range(self._number_of_tiles_y)):
                    tile = self._tile_mapping[self._tiles[x][y]]
                    self._screen.blit(tile, 
                                      tile.get_rect().move(x * tile.get_width(), y * tile.get_height())) 
            
                pygame.display.flip()
                
            self._clock.tick(self._fps)