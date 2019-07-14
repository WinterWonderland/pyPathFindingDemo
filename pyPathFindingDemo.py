import sys
import random
from enum import Enum
from itertools import product
import contextlib
with contextlib.redirect_stdout(None):
    import pygame


size = width, height = 1024, 768
fps = 30
percentage_of_wall_fields = 0.2

pygame.init()
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

empty_tile = pygame.image.load(r"Textures\TileWhite.png").convert()
wall_tile = pygame.image.load(r"Textures\TileBlack.png").convert()
start_tile = pygame.image.load(r"Textures\TileStart.png").convert()
end_tile = pygame.image.load(r"Textures\TileEnd.png").convert()

class TileType(Enum):
    empty = 0,
    wall = 1,
    start = 2,
    end = 3
    
tile_mapping = {TileType.empty: empty_tile,
                TileType.wall: wall_tile,
                TileType.start: start_tile,
                TileType.end: end_tile}

number_of_tiles_x = int(width / empty_tile.get_width())
number_of_tiles_y = int(height / empty_tile.get_height())

board = [[None for _ in range(number_of_tiles_y)] for _ in range(number_of_tiles_x)]

for x, y in product(range(number_of_tiles_x), range(number_of_tiles_y)):
    if x == 0 or \
            y == 0 or \
            x == number_of_tiles_x - 1 or \
            y == number_of_tiles_y - 1 or \
            random.random() < percentage_of_wall_fields:
        board[x][y] = TileType.wall
    else:
        board[x][y] = TileType.empty

board[random.randint(1, number_of_tiles_x - 2)][random.randint(1, number_of_tiles_y - 2)] = TileType.start
board[random.randint(1, number_of_tiles_x - 2)][random.randint(1, number_of_tiles_y - 2)] = TileType.end
                     
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill([0, 255, 255])
            
    for x, y in product(range(number_of_tiles_x), range(number_of_tiles_y)):
        tile = tile_mapping[board[x][y]]
        
        if tile:
            screen.blit(tile, 
                        tile.get_rect().move(x * tile.get_width(), 
                                             y * tile.get_height())) 

    pygame.display.flip()
    clock.tick(fps)