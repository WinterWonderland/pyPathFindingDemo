import random
from enum import Enum
from itertools import product
import contextlib
with contextlib.redirect_stdout(None):
    import pygame


class TileType(Enum):
    empty = 0,
    wall = 1,
    start = 2,
    end = 3


class Board:
    def __init__(self, width, height, percentage_of_wall_fields, fps):
        
        self._size = self._width, self._height = width , height
        self._fps = fps
        
        pygame.init()
        self._screen = pygame.display.set_mode(self._size)
        self._clock = pygame.time.Clock()

        self._empty_tile = pygame.image.load(r"Textures\TileWhite.png").convert()
        self._wall_tile = pygame.image.load(r"Textures\TileBlack.png").convert()
        self._start_tile = pygame.image.load(r"Textures\TileStart.png").convert()
        self._end_tile = pygame.image.load(r"Textures\TileEnd.png").convert()
        
        self._tile_mapping = {TileType.empty: self._empty_tile,
                              TileType.wall: self._wall_tile,
                              TileType.start: self._start_tile,
                              TileType.end: self._end_tile}
        
        self._number_of_tiles_x = int(self._width / self._empty_tile.get_width())
        self._number_of_tiles_y = int(self._height / self._empty_tile.get_height())

        self._tiles = [[None for _ in range(self._number_of_tiles_y)] for _ in range(self._number_of_tiles_x)]
        
        for x, y in product(range(self._number_of_tiles_x), range(self._number_of_tiles_y)):
            if x == 0 or y == 0 or x == self._number_of_tiles_x - 1 or y == self._number_of_tiles_y - 1 or random.random() < percentage_of_wall_fields:
                self._tiles[x][y] = TileType.wall
            else:
                self._tiles[x][y] = TileType.empty
        
        self._tiles[random.randint(1, self._number_of_tiles_x - 2)][random.randint(1, self._number_of_tiles_y - 2)] = TileType.start
        self._tiles[random.randint(1, self._number_of_tiles_x - 2)][random.randint(1, self._number_of_tiles_y - 2)] = TileType.end
        
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
        
            self._screen.fill([0, 255, 255])
                    
            for x, y in product(range(self._number_of_tiles_x), range(self._number_of_tiles_y)):
                tile = self._tile_mapping[self._tiles[x][y]]
                self._screen.blit(tile, 
                                  tile.get_rect().move(x * tile.get_width(), y * tile.get_height())) 
        
            pygame.display.flip()
            self._clock.tick(self._fps)
