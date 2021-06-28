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
TICK_FREQUENCY = 60

# Display
WINDOW_DIMENSIONS = vec2(1280, 720) # Dimensions of the displayed window. Defaults to 1080p, should change dynamically
WORLD_DIMENSIONS = vec2(50, 50) # World coordinate dimensions, affects how objects are oriented on a cartesian map
MINIMAP = canvas(vec2(0, 0), WORLD_DIMENSIONS, vec2(WINDOW_DIMENSIONS.y, WINDOW_DIMENSIONS.y))
PERSPECTIVE = canvas(vec2(0, 0), WINDOW_DIMENSIONS, WINDOW_DIMENSIONS)
WINDOW = pygame.display.set_mode(WINDOW_DIMENSIONS.display()) # Initialise window

# Drawing
DRAW_QUEUE: List[illustration] = []
MINIMAP_PRIORITY = 1000
PERSPECTIVE_PRIORITY = 100

# World
WORLD = terrain(WORLD_DIMENSIONS)
PLAYER = entity(vec2(0, 0), boundingbox(5))
ENTITIES: List[entity] = []
LOAD_DISTANCE = 6

# 3D View
RENDER_DISTANCE = 20
RENDER_RESOLUTION = 30
INTERCEPTS = None
RAYS = None


'''
    INITIALISATION
'''

def init():
    '''
        Determine the first set of raycasts
    '''
    global RAYS
    RAYS = PLAYER.raycast(RENDER_DISTANCE, RENDER_RESOLUTION)

    '''
        Generate the world
    '''
    for i in range(WORLD_DIMENSIONS.x):
        WORLD.getSquare(vec2(i, 30)).setOccupation(polygon(boundingbox(0.5)))

    '''
        Define intercepts as an array
    '''
    global INTERCEPTS
    INTERCEPTS = []

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
            velocity.x -= 0.1
        if key[pygame.K_d]:
            velocity.x += 0.1
        if key[pygame.K_w]:
            velocity.y -= 0.1
        if key[pygame.K_s]:
            velocity.y += 0.1

        # Gets a new vector based on difference between the player's yaw and applied velocity. Required for directional movement, and PI/2 there to offset 90 degrees
        relative_velocity = velocity.relative(PLAYER.yaw.subtract(math.atan2(velocity.y, velocity.x) + PI/2)) 
        PLAYER.velocity = PLAYER.velocity.add(relative_velocity.x, relative_velocity.y)

    if key[pygame.K_LEFT]:
        PLAYER.yaw = PLAYER.yaw.add((PI/180) * 10)
    if key[pygame.K_RIGHT]:
        PLAYER.yaw = PLAYER.yaw.subtract((PI/180) * 10)

def entityHandler():
    global RAYS

    # Player updates
    RAYS = list(reversed(PLAYER.raycast(RENDER_DISTANCE, RENDER_RESOLUTION)))

    # PROBLEM: PLAYER.position is being mutated, and therefore the drawing position differs from the raycasts.
    DRAW_QUEUE.append(illustration(pygame.draw.circle, ((255, 255, 0), MINIMAP.relative(PLAYER.position, WORLD_DIMENSIONS).display(), PLAYER.boundingbox.radius), MINIMAP_PRIORITY + 5))
    PLAYER.tick()
    
    # Entity updates
    for entity in ENTITIES:
        entity.tick()

def gfxHandler():
    global RAYS
    global INTERCEPTS

    '''
        Retrieve raycast intercepts
    '''
    for raycast_index in range(len(RAYS)):
        raycast = RAYS[raycast_index]
        squares = WORLD.getAdjacentSquares(PLAYER.position.floor(), LOAD_DISTANCE)
        INTERCEPTS.append([])
        DRAW_QUEUE.append(illustration(pygame.draw.line, ((255, 255, 128), MINIMAP.relative(raycast.start, WORLD_DIMENSIONS).display(), MINIMAP.relative(raycast.finish, WORLD_DIMENSIONS).display(), 1), MINIMAP_PRIORITY + 3))

        for square in squares:

            #rect = pygame.Rect(MINIMAP.relative(square.position.add(0.5, 0.5), WORLD_DIMENSIONS).display(), (MINIMAP.ratio(WORLD_DIMENSIONS).x, MINIMAP.ratio(WORLD_DIMENSIONS).y))
            #DRAW_QUEUE.append(illustration(pygame.draw.rect, ((255, 0, 255), rect), MINIMAP_PRIORITY + 10))

            if square is None or square.occupation is None:
                continue

            for direction, boundary in square.occupation.boundingbox.boundaries.items():
                boundary_offset = boundary.offset(square.position.add(square.occupation.boundingbox.radius, square.occupation.boundingbox.radius))
                intercept = raycast.intercept(boundary_offset)

                if intercept is None:
                    continue

                INTERCEPTS[raycast_index].append(intercept)
    '''
        Draw graphics based on intercepts closest to player
    '''

    for group in INTERCEPTS:
        closest_distance = -1
        closest_intercept= None

        for intercept in group:
            distance = PLAYER.position.distance(intercept)

            if closest_intercept is None or distance < closest_distance:
                closest_distance = distance
                closest_intercept = intercept

        if closest_intercept is None:
            continue

        DRAW_QUEUE.append(illustration(pygame.draw.circle, ((255, 0, 0), MINIMAP.relative(closest_intercept, WORLD_DIMENSIONS).display(), 5, 5), MINIMAP_PRIORITY + 4))
        #DRAW_QUEUE.append(illustration(pygame.draw.rect, ((pygame.rect(vec2())))))

    '''
        Draw the minimap.
    '''
    for x in range(WORLD_DIMENSIONS.x):
        for y in range(WORLD_DIMENSIONS.y):
            position = vec2(x, y)
            square = WORLD.getSquare(position)
            
            if square.occupation is None:
                continue

            for direction, boundary in square.occupation.boundingbox.boundaries.items():
                boundary_offset = boundary.offset(square.position.add(square.occupation.boundingbox.radius, square.occupation.boundingbox.radius))
                DRAW_QUEUE.append(illustration(pygame.draw.line, ((255, 255, 255), MINIMAP.relative(boundary_offset.start, WORLD_DIMENSIONS).display(), MINIMAP.relative(boundary_offset.finish, WORLD_DIMENSIONS).display(), 1), MINIMAP_PRIORITY + 2))

def interfaceHandler():
    DRAW_QUEUE.append(illustration(pygame.draw.rect, ((0, 0, 0), pygame.Rect(MINIMAP.position.x, MINIMAP.position.y, MINIMAP.display_dimensions.x, MINIMAP.display_dimensions.y)), MINIMAP_PRIORITY + 1))
    pass

def drawHandler():
    WINDOW.fill((0, 0, 0)) # Clear the current screen

    global DRAW_QUEUE
    while len(DRAW_QUEUE) > 0:
        highest_priority = -1 # the lowest number has the highest priority
        highest_priority_index = -1

        for index in range(len(DRAW_QUEUE)):
            runnable = DRAW_QUEUE[index]

            # Higher priority drawable found
            if highest_priority < 0 or runnable.priority < highest_priority:
                highest_priority = runnable.priority
                highest_priority_index = index

        # Draw the highest priority first
        DRAW_QUEUE[highest_priority_index].draw(WINDOW)
        DRAW_QUEUE.pop(highest_priority_index)

    pygame.display.update() # Update the window displayed

def resetHandler():
    global RAYS
    global INTERCEPTS
    global DRAW_QUEUE

    RAYS = []
    INTERCEPTS = []
    DRAW_QUEUE = []
    
                
# A soup of all the things that need to be done per tick.
def computation():
    eventHandler()
    keystrokeHandler()
    entityHandler()
    gfxHandler()
    interfaceHandler()
    drawHandler()
    resetHandler()

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
        warnings.warn(f'Couldn\'t keep up! Running {round(time_difference, 2)}s behind expected interval of {TICK_FREQUENCY} ticks per second. ({int((time_difference * TICK_FREQUENCY) * 100)}% slower)', RuntimeWarning, stacklevel=4)
    
def threadHandler():
    while True:
        tick()
        
if __name__ == '__main__':
    init()
    threadHandler()