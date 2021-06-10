'''
<+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+>

"Maze Escape" 
- Written by 51896

<+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+>
'''

# Miscellaneous modules
import pygame
import math
from typing import List
from pygame.locals import *

# Modules for threading
import multiprocessing
import asyncio
import time
import warnings
from concurrent.futures import ProcessPoolExecutor

# Local modules
from classes.world import terrain, polygon
from classes.geometry import vec2, line, PI
from classes.entities import boundingbox, entity
from classes.interface import canvas, illustration, colourDistanceMultiplier

'''
    GLOBAL DEFINITIONS
'''
# Threading
TICK_FREQUENCY = 20

# Display
WINDOW_DIMENSIONS = vec2(1280, 720) # Dimensions of the displayed window. Defaults to 1080p, should change dynamically
WORLD_DIMENSIONS = vec2(100, 100) # World coordinate dimensions, affects how objects are oriented on a cartesian map
MINIMAP = canvas(vec2(0, 0), WORLD_DIMENSIONS, vec2(WINDOW_DIMENSIONS.y, WINDOW_DIMENSIONS.y))
PERSPECTIVE = canvas(vec2(0, 0), WINDOW_DIMENSIONS, WINDOW_DIMENSIONS)
WINDOW = pygame.display.set_mode(WINDOW_DIMENSIONS.display()) # Initialise window

# Drawing
DRAW_QUEUE: List[illustration] = []

# World
WORLD = terrain(WORLD_DIMENSIONS, WINDOW_DIMENSIONS)
PLAYER = entity(vec2(0, 0), boundingbox(5))
ENTITIES: List[entity] = []

# 3D View
RENDER_DISTANCE = 20
RENDER_RESOLUTION = 30
RAYS = None

'''
    GLOBAL FUNCTIONS
'''
def toWorldCoordinates(position: vec2) -> vec2: # converts window to world coordinates
    return vec2((position.x/WINDOW_DIMENSIONS.x) * WORLD_DIMENSIONS.x, (position.y/WINDOW_DIMENSIONS.y) * WORLD_DIMENSIONS.y)
def toWindowCoordinates(position: vec2) -> vec2: # converts world to window coordinates (used for drawing, intercepts, collsions, etc.)
    return vec2((position.x/WORLD_DIMENSIONS.x) * WINDOW_DIMENSIONS.x, (position.y/WORLD_DIMENSIONS.y) * WINDOW_DIMENSIONS.y)

'''
    INITIALISATION
'''

def init():
    global RAYS
    RAYS = PLAYER.raycast(RENDER_DISTANCE, RENDER_RESOLUTION)
    WORLD.getSquare(vec2(30, 30)).setOccupation(polygon(boundingbox(0.5)))

'''
    MAIN COMPUTATION METHODS
'''

# Processes high level window interaction events from the user.
def eventHandler():
    for event in pygame.event.get(): # Retreive all queued events. Must be ran to display a window (apparently)
        pass

# Reads combinations of keystrokes and handles them accordingly
def keystrokeHandler():
        key = pygame.key.get_pressed()
        if key[pygame.K_a] or key[pygame.K_d] or key[pygame.K_w] or key[pygame.K_s]:
            velocity = vec2(0, 0)

            if key[pygame.K_a]:
                velocity.x -= 1
            if key[pygame.K_d]:
                velocity.x += 1
            if key[pygame.K_w]:
                velocity.y -= 1
            if key[pygame.K_s]:
                velocity.y += 1

            # Gets a new vector based on difference between the player's yaw and applied velocity. Required for directional movement, and PI/2 there to offset 90 degrees
            relative_velocity = velocity.relative(PLAYER.yaw.subtract(math.atan2(velocity.y, velocity.x) + PI/2)) 
            PLAYER.velocity = PLAYER.velocity.add(relative_velocity.x, relative_velocity.y)

        if key[pygame.K_LEFT]:
            PLAYER.yaw = PLAYER.yaw.add((PI/180) * 10)
        if key[pygame.K_RIGHT]:
            PLAYER.yaw = PLAYER.yaw.subtract((PI/180) * 10)

def entityHandler():
    # Player updates
    global RAYS
    RAYS = list(reversed(PLAYER.raycast(RENDER_DISTANCE, RENDER_RESOLUTION)))

    # PROBLEM: PLAYER.position is being mutated, and therefore the drawing position differs from the raycasts.
    DRAW_QUEUE.append(illustration(pygame.draw.circle, ((255, 255, 0), MINIMAP.relative(PLAYER.position, WORLD_DIMENSIONS).display(), PLAYER.boundingbox.radius)))
    PLAYER.tick()
    
    # Entity updates
    for entity in ENTITIES:
        entity.tick()

def terrainHandler():
    '''
        Check for player raycast intercepts and display accordingly.
    '''
    for raycast in RAYS:
        DRAW_QUEUE.append(illustration(pygame.draw.line, ((255, 255, 128), MINIMAP.relative(raycast.start, WORLD_DIMENSIONS).display(), MINIMAP.relative(raycast.finish, WORLD_DIMENSIONS).display(), 1)))
        square = WORLD.getSquare(toWorldCoordinates(PLAYER.position).floor())

        if square is None or square.occupation is None:
            continue

        for boundary in square.occupation.boundingbox.boundaries:
            boundary_offset = boundary.offset(square.position.subtract(square.occupation.boundingbox.radius, square.occupation.boundingbox.radius))
            intercept = raycast.intercept(boundary_offset)

            if intercept is None:
                continue

            DRAW_QUEUE.append(illustration(pygame.draw.circle, ((255, 255, 0), intercept.display(), 5, 5)))

    '''
        Draw the minimap.
    '''
    for x in range(WORLD_DIMENSIONS.x):
        for y in range(WORLD_DIMENSIONS.y):
            position = vec2(x, y)
            square = WORLD.getSquare(position)
            
            if square.occupation is None:
                continue

            for boundary in square.occupation.boundingbox.boundaries:
                boundary_offset = boundary.offset(square.position)
                DRAW_QUEUE.append(illustration(pygame.draw.line, ((255, 255, 255), boundary_offset.start.display(), boundary_offset.finish.display(), 5)))

def drawHandler():
    WINDOW.fill((0, 0, 0)) # Clear the current screen

    global DRAW_QUEUE
    for runnable in DRAW_QUEUE:
        runnable.draw(WINDOW)

    DRAW_QUEUE = []
    pygame.display.update() # Update the window displayed
    
                
# A soup of all the things that need to be done per tick.
def computation():
    eventHandler()
    keystrokeHandler()
    terrainHandler()
    entityHandler()
    drawHandler()

'''
    THREAD HANDLER
'''

def tick():
    # Record initial time before code execution
    time_initial = time.time()

    # Fat CPU computation
    computation()

    # Record time after code execution and compare difference to ticks.
    time_post = time.time()
    time_difference = time_post - time_initial
    if time_difference < (1/TICK_FREQUENCY):
        time.sleep((1/TICK_FREQUENCY) - time_difference) # pause execution until the tick is done
    else:
        warnings.warn(f'Couldn\'t keep up! Running {round(time_difference, 2)}s behind expected interval of {TICK_FREQUENCY} ticks per second. ({int((time_difference * TICK_FREQUENCY) * 100)}% slower)', RuntimeWarning)
    
def threadHandler():
    while True:
        tick()
        
if __name__ == '__main__':
    init()
    threadHandler()