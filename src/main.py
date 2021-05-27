import pygame
from pygame.locals import *
from geometry import vec2, line
from entities import boundingbox, entity, player

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

'''
    Create the player
'''
player1 = player(vec2(100, 100), boundingbox(10))
entities = [
    player1
]

while True: # main game loop
    for event in pygame.event.get(): # Retreive all queued events. Must be ran to display a window
        pass

    key = pygame.key.get_pressed()
    if key[pygame.K_a]:
        player1.velocity.x -= 0.02
    if key[pygame.K_d]:
        player1.velocity.x += 0.02
    if key[pygame.K_w]:
        player1.velocity.y -= 0.02
    if key[pygame.K_s]:
        player1.velocity.y += 0.02

    for wall in walls:
        pygame.draw.line(window, (255, 255, 255), (wall.start.x, wall.start.y), (wall.finish.x, wall.finish.y), width=1)

    for entity in entities:
        entity.tick()
        
    pygame.draw.circle(window, (255, 255, 63), (player1.position.x, player1.position.y), player1.boundingbox.radius, width=0) # draw the player
    pygame.display.update() # Update the window displayed
    window.fill((0, 0, 0))
    
