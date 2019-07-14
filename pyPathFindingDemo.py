import sys
import contextlib
with contextlib.redirect_stdout(None):
    import pygame


size = width, height = 1024, 768
black = 0, 0, 0
fps = 30

pygame.init()
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
            
    screen.fill(black)
            
    pygame.display.flip()
    clock.tick(fps)