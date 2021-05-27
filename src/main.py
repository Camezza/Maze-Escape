import pygame, sys
from pygame.locals import *
from geometry import vec2, ray, line
from entities import entity

pygame.init()
window = pygame.display.set_mode((1280, 720)) # Initialise window

'''
    Create the environment
'''
walls = [
    line(vec2(50, 50), vec2(50, 300)),
    line(vec2(50, 300), vec2(300, 300)),
    line(vec2(300, 300), vec2(300, 50)),
    line(vec2(300, 50), vec2(50, 50)),
]

for wall in walls:
    pygame.draw.line(window, (255, 255, 255), (wall.start.x, wall.start.y), (wall.finish.x, wall.finish.y), width=1)

'''
    Create the player
'''

player = entity(vec2(100, 100))

while True: # main game loop
    for event in pygame.event.get(): # Retreive all queued events. Must be ran to display a window
        pass

    key = pygame.key.get_pressed()
    if key[pygame.K_LEFT]:
        player.position = player.position.add(-1, 0)
    if key[pygame.K_RIGHT]:
        player.position = player.position.add(1, 0)
    if key[pygame.K_UP]:
        player.position = player.position.add(0, -1)
    if key[pygame.K_DOWN]:
        player.position = player.position.add(0, 1)

    pygame.draw.circle(window, (255, 255, 63), (player.position.x, player.position.y), 10, width=0) # draw the player
    pygame.display.update() # Update the window displayed
    window.fill((0, 0, 0))
    
