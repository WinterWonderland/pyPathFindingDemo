import sys
from itertools import product
import contextlib
import random
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

number_of_tiles_x = int(width / empty_tile.get_width())
number_of_tiles_y = int(height / empty_tile.get_height())

for x, y in product(range(number_of_tiles_x), range(number_of_tiles_y)):
    if x == 0 or \
            y == 0 or \
            x == number_of_tiles_x - 1 or \
            y == number_of_tiles_y - 1 or \
            random.random() < percentage_of_wall_fields:
        screen.blit(wall_tile, 
                    wall_tile.get_rect().move(x * wall_tile.get_width(), 
                                              y * wall_tile.get_height()))
    else:
        screen.blit(empty_tile, 
                    empty_tile.get_rect().move(x * empty_tile.get_width(), 
                                               y * empty_tile.get_height()))

screen.blit(start_tile, 
            start_tile.get_rect().move(random.randint(1, number_of_tiles_x - 1) * start_tile.get_width(), 
                                       random.randint(1, number_of_tiles_y - 1) * start_tile.get_height()))

screen.blit(end_tile, 
            end_tile.get_rect().move(random.randint(1, number_of_tiles_x - 1) * end_tile.get_width(), 
                                     random.randint(1, number_of_tiles_y - 1) * end_tile.get_height()))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    pygame.display.flip()
    clock.tick(fps)