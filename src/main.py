import pygame
import math
from pygame.locals import *
from geometry import vec2, ray, line, PI
from entities import boundingbox, entity, player
from interface import canvas

pygame.init()
dimensions = vec2(1280, 720)
window = pygame.display.set_mode(dimensions.display()) # Initialise window
minimap = canvas(vec2(10, 10), dimensions, dimensions.divide(1.5, 1.5))
camera = canvas(vec2(0, 0), dimensions, dimensions)

'''
    Create the environment
'''
walls = [
    line(vec2(0, 0), vec2(0, 300)),
    line(vec2(0, 300), vec2(300, 300)),
    line(vec2(300, 300), vec2(300, 0)),
    line(vec2(300, 0), vec2(0, 0)),
]

'''
    Create the player
'''
player1 = player(vec2(100, 100), boundingbox(10))
entities = [
    player1
]
    

'''
    Update loop
'''
while True:
    '''
        Retrieve queued input events
    '''
    for event in pygame.event.get(): # Retreive all queued events. Must be ran to display a window
        pass

    '''
        Retrieve keystrokes
    '''
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

    '''

    '''
    rays = player1.retrieveRays(400, 90)
    for i in range(len(rays)):
        raycast = rays[i]
        pygame.draw.line(window, (255, 255, 128), minimap.relative(raycast.start, dimensions).display(), minimap.relative(raycast.finish, dimensions).display(), width=math.ceil(minimap.ratio(dimensions).length() * 1))

        for wall in walls:
            intercept = wall.intercept(raycast)

            if intercept != None:
                distance = player1.position.distance(intercept)
                bar_dimensions = vec2((dimensions.x * (1/len(rays))-4), dimensions.y * (10/distance))
                position = vec2(dimensions.x * (i/len(rays)), (dimensions.y / 2) -  bar_dimensions.y/2)
                rect = pygame.Rect(position.x, position.y, bar_dimensions.x, bar_dimensions.y)
                pygame.draw.rect(window, (255, 255, 255), rect)
                pygame.draw.circle(window, (255, 255, 0), minimap.relative(intercept, dimensions).display(), minimap.ratio(dimensions).length() * 4)

    '''
        Display minimap
    '''

    for wall in walls:
        colour = (255, 255, 255) # white
        start = minimap.relative(wall.start, dimensions).display()
        finish = minimap.relative(wall.finish, dimensions).display()
        width = math.ceil(minimap.ratio(dimensions).length() * 5)
        pygame.draw.line(window, colour, start, finish, width=width)

    for entity in entities:
        entity.tick()
        
    pygame.draw.circle(window, (255, 255, 60), minimap.relative(player1.position, dimensions).display(), minimap.ratio(dimensions).length() * player1.boundingbox.radius) # draw the player

    pygame.display.update() # Update the window displayed
    window.fill((0, 0, 0))