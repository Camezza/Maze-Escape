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
import asyncio
import time
import warnings

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
MINIMAP = canvas(vec2(10, 10), WINDOW_DIMENSIONS, WINDOW_DIMENSIONS.divide(4, 4))
PERSPECTIVE = canvas(vec2(0, 0), WINDOW_DIMENSIONS, WINDOW_DIMENSIONS)
WINDOW = pygame.display.set_mode(WINDOW_DIMENSIONS.display()) # Initialise window

# Drawing
DRAW_QUEUE: List[illustration] = []

# World
WORLD = terrain(WORLD_DIMENSIONS, WINDOW_DIMENSIONS)
PLAYER = entity(vec2(0, 0), boundingbox(5))
ENTITIES: List[entity] = []

# 3D View
RENDER_DISTANCE = 400
RENDER_RESOLUTION = 60
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
    WORLD.getSquare(vec2(10, 10)).setOccupation(polygon(boundingbox(5)))
    WORLD.getSquare(vec2(30, 30)).setOccupation(polygon(boundingbox(10)))

'''
    MAIN PROCESS
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
    PLAYER.tick()
    DRAW_QUEUE.append(illustration(pygame.draw.circle, (WINDOW, (255, 255, 0), PLAYER.position.display(), PLAYER.boundingbox.radius)))
    
    # Entity updates
    for entity in ENTITIES:
        entity.tick()

def terrainHandler():
    # Find where each player raycast intercepts with terrain and display
    for raycast in RAYS: 
        for x in range(WORLD_DIMENSIONS.x):
            for y in range(WORLD_DIMENSIONS.y):
                world_position = vec2(x, y)
                square = WORLD.getSquare(world_position)

                if square.occupation is None:
                    continue

                for boundary in square.occupation.boundingbox.boundaries:
                    boundary_position = toWindowCoordinates(square.position)
                    boundary_offset = boundary.offset(boundary_position.subtract(square.occupation.boundingbox.radius, square.occupation.boundingbox.radius))
                    intercept = raycast.intercept(boundary_offset)
                    DRAW_QUEUE.append(illustration(pygame.draw.line, (WINDOW, (255, 255, 255), boundary_offset.start.display(), boundary_offset.finish.display(), 2)))

def drawHandler():
    WINDOW.fill((0, 0, 0)) # Clear the current screen

    global DRAW_QUEUE
    for runnable in DRAW_QUEUE:
        runnable.draw()

    DRAW_QUEUE = []
    pygame.display.update() # Update the window displayed
    
                
# A soup of all the things that need to be done per tick.
def computation():
    eventHandler()
    keystrokeHandler()
    entityHandler()
    #terrainHandler()
    drawHandler()

'''
    THREAD HANDLER
'''

async def tick():
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
    

async def main():
    init()
    while True:
        await tick()

asyncio.run(main()) # init