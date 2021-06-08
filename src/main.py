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
from classes.interface import canvas, colourDistanceMultiplier

'''
    GLOBAL DEFINITIONS
'''
# Threading
TICK_FREQUENCY = 20

# Display
WINDOW_DIMENSIONS = vec2(1920, 1080) # Dimensions of the displayed window. Defaults to 1080p, should change dynamically
WORLD_DIMENSIONS = vec2(100, 100) # World coordinate dimensions, affects how objects are oriented on a cartesian map
MINIMAP = canvas(vec2(10, 10), WINDOW_DIMENSIONS, WINDOW_DIMENSIONS.divide(4, 4))
PERSPECTIVE = canvas(vec2(0, 0), WINDOW_DIMENSIONS, WINDOW_DIMENSIONS)
WINDOW = pygame.display.set_mode(WINDOW_DIMENSIONS.display()) # Initialise window

# World
WORLD = terrain(WORLD_DIMENSIONS, WINDOW_DIMENSIONS)
PLAYER = entity(vec2(0, 0), boundingbox(5))
ENTITIES: List[entity] = []

# 3D View
RENDER_DISTANCE = 400
RENDER_RESOLUTION = 60
RAYS: List[line] = None

'''
    MAIN PROCESS
'''

# Processes high level window interaction events from the user.
def eventHandler():
    for event in pygame.event.get(): # Retreive all queued events. Must be ran to display a window
        pass

# Reads combinations of keystrokes and handles them accordingly
def keystrokeHandler():
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
            relative_velocity = velocity.relative(PLAYER.yaw.subtract(math.atan2(velocity.y, velocity.x) + PI/2)) 
            PLAYER.velocity = PLAYER.velocity.add(relative_velocity.x, relative_velocity.y)

        if key[pygame.K_LEFT]:
            PLAYER.yaw = PLAYER.yaw.add(PI/180)
        if key[pygame.K_RIGHT]:
            PLAYER.yaw = PLAYER.yaw.subtract(PI/180)

def entityHandler():
    # Player updates
    RAYS = list(reversed(PLAYER.raycast(RENDER_DISTANCE, RENDER_RESOLUTION)))
    
    # Entity updates
    for entity in ENTITIES:
        entity.tick()

# A soup of all the things that need to be done per tick.
def computation():
    eventHandler()
    keystrokeHandler()
    entityHandler()

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
        warnings.warn(f'Couldn\'t keep up! Running {time_difference} behind expected interval of {TICK_FREQUENCY} ticks per second.', RuntimeWarning)
    

async def main():
    while True:
        await tick()

asyncio.run(main()) # init