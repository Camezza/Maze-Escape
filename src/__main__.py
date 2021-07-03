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
from classes.world import terrain, polygon, generateMaze
from classes.geometry import vec2, line, PI
from classes.entities import boundingbox, entity
from classes.interface import canvas, illustration, palette, colourDistanceMultiplier

'''
    GLOBAL DEFINITIONS
'''
# Threading
TICK_FREQUENCY = 60

# Display
WINDOW_DIMENSIONS = vec2(1280, 720) # Dimensions of the displayed window. Defaults to 1080p, should change dynamically
WORLD_DIMENSIONS = vec2(16, 16).add(1, 1) # World coordinate dimensions, affects how objects are oriented on a cartesian map
MINIMAP = canvas(vec2(0, 0), WORLD_DIMENSIONS, vec2(WINDOW_DIMENSIONS.y, WINDOW_DIMENSIONS.y))
PERSPECTIVE = canvas(vec2(0, 0), WINDOW_DIMENSIONS, WINDOW_DIMENSIONS)
WINDOW = pygame.display.set_mode(WINDOW_DIMENSIONS.display()) # Initialise window

# Drawing
DRAW_REFERENCE = {
    'rectangle': pygame.draw.rect,
    'circle': pygame.draw.circle,
    'line': pygame.draw.line,

}
DRAW_QUEUE = palette()
MINIMAP_PRIORITY = 1000
PERSPECTIVE_PRIORITY = 100

# World
WORLD = terrain(WORLD_DIMENSIONS)
PLAYER = entity(vec2(0, 0), boundingbox(5))
ENTITIES: List[entity] = []
LOAD_DISTANCE = 3

# 3D View
RENDER_DISTANCE = LOAD_DISTANCE
RENDER_RESOLUTION = 30
INTERCEPTS = None
VISIBLE_INTERCEPTS = None
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
    WORLD.fill()
    WORLD.grid = generateMaze(WORLD.grid)

    '''
        Define intercepts as an array
    '''
    global INTERCEPTS
    global VISIBLE_INTERCEPTS
    INTERCEPTS = []
    VISIBLE_INTERCEPTS = []

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
            velocity.x -= 0.03
        if key[pygame.K_d]:
            velocity.x += 0.03
        if key[pygame.K_w]:
            velocity.y -= 0.03
        if key[pygame.K_s]:
            velocity.y += 0.03

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
    DRAW_QUEUE.append(illustration('circle', ((255, 255, 0), MINIMAP.relative(PLAYER.position, WORLD_DIMENSIONS).display(), PLAYER.boundingbox.radius)), MINIMAP_PRIORITY + 5)
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
    current_time = time.time()
    for raycast_index in range(len(RAYS)):
        raycast = RAYS[raycast_index]
        squares = WORLD.getAdjacentSquares(PLAYER.position.floor(), LOAD_DISTANCE)
        INTERCEPTS.append([])
        DRAW_QUEUE.append(illustration('line', ((255, 255, 128), MINIMAP.relative(raycast.start, WORLD_DIMENSIONS).display(), MINIMAP.relative(raycast.finish, WORLD_DIMENSIONS).display(), 1)), MINIMAP_PRIORITY + 3)

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

    print(f'Took intercepts {round(time.time() - current_time, 2) * 1000}ms to process')
    current_time = time.time()
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

        VISIBLE_INTERCEPTS.append(closest_intercept)
        DRAW_QUEUE.append(illustration('circle', ((255, 0, 0), MINIMAP.relative(closest_intercept, WORLD_DIMENSIONS).display(), 5, 5)), MINIMAP_PRIORITY + 4)
        #DRAW_QUEUE.append(illustration(pygame.draw.rect, ((pygame.rect(vec2())))))

    print(f'Took player-closest intercepts {round(time.time() - current_time, 2) * 1000}ms to process')
    current_time = time.time()
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
                DRAW_QUEUE.append(illustration('line', ((255, 255, 255), MINIMAP.relative(boundary_offset.start, WORLD_DIMENSIONS).display(), MINIMAP.relative(boundary_offset.finish, WORLD_DIMENSIONS).display(), 1)), MINIMAP_PRIORITY + 2)

    print(f'Took minimap {round(time.time() - current_time, 2) * 1000}ms to process')
    current_time = time.time()
    print('\n')

    '''
        Draw the 3D View.
    '''
    for i in range(len(VISIBLE_INTERCEPTS)):
        

def interfaceHandler():
    WINDOW.fill((0, 0, 0)) # Clear the current screen
    DRAW_QUEUE.append(illustration('rectangle', ((0, 0, 0), pygame.Rect(MINIMAP.position.x, MINIMAP.position.y, MINIMAP.display_dimensions.x, MINIMAP.display_dimensions.y))), MINIMAP_PRIORITY + 1)
    pass

def drawHandler():
    global DRAW_QUEUE

    while len(DRAW_QUEUE.queue.items()) > 0:
        highest_priority = -1 # the lowest number has the highest priority
        for priority, runnable in DRAW_QUEUE.queue.items():
            if highest_priority < 0 or priority < highest_priority:
                highest_priority = priority

        for runnable in DRAW_QUEUE.queue[highest_priority]:
            runnable.draw(DRAW_REFERENCE, WINDOW)

        DRAW_QUEUE.queue.pop(highest_priority, None)

    pygame.display.update() # Update the window displayed

def resetHandler():
    global RAYS
    global INTERCEPTS
    global VISIBLE_INTERCEPTS
    global DRAW_QUEUE

    RAYS = []
    INTERCEPTS = []
    VISIBLE_INTERCEPTS = []
    DRAW_QUEUE.reset()
    
                
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