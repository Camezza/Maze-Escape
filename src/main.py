import pygame
import math
from pygame.locals import *
from geometry import vec2, ray, line, PI
from entities import boundingbox, entity, player
from interface import canvas

pygame.init()
dimensions = vec2(1280, 720)
window = pygame.display.set_mode(dimensions.display()) # Initialise window
minimap = canvas(vec2(50, 50), dimensions, dimensions.divide(0.5, 0.5))

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
    if key[pygame.K_a] or key[pygame.K_d] or key[pygame.K_w] or key[pygame.K_s]:
        velocity = vec2(0, 0)

        if key[pygame.K_a]:
            velocity.x -= 0.02
        if key[pygame.K_d]:
            velocity.x += 0.02
        if key[pygame.K_w]:
            velocity.y -= 0.02
        if key[pygame.K_s]:
            velocity.y += 0.02

        # Gets a new vector based on difference between the player's yaw and applied velocity. Required for directional movement, and PI/2 there to offset 90 degrees
        relative_velocity = velocity.relative(player1.yaw.subtract(math.atan2(velocity.y, velocity.x) + PI/2)) 
        player1.velocity = player1.velocity.add(relative_velocity.x, relative_velocity.y)

    if key[pygame.K_LEFT]:
        player1.yaw = player1.yaw.add(PI/180)
    if key[pygame.K_RIGHT]:
        player1.yaw = player1.yaw.subtract(PI/180)

    for wall in walls:
        pygame.draw.line(window, (255, 255, 255), minimap.relative(wall.start, dimensions).display(), minimap.relative(wall.finish, dimensions).display(), width=5)

    for entity in entities:
        entity.tick()
        
    pygame.draw.circle(window, (255, 255, 63), minimap.relative(player1.position, dimensions).display(), player1.boundingbox.radius, width=0) # draw the player

    render_distance = 200
    render_amount = 30

    minimum = player1.yaw.subtract(player1.fov.radians/2)
    maximum = player1.yaw.add(player1.fov.radians/2)
    iterator = player1.fov.radians/render_amount

    for i in range(render_amount):
        radians = minimum.add(i * iterator).radians
        raycast = ray(player1.position, player1.position.add(math.sin(radians) * render_distance, math.cos(radians) * render_distance))
        pygame.draw.line(window, (255, 255, 30), minimap.relative(raycast.start, dimensions).display(), minimap.relative(raycast.finish, dimensions).display(), width=1)

    pygame.display.update() # Update the window displayed
    window.fill((0, 0, 0))
    
