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
import time
import warnings

# Local modules
from classes.world import terrain, polygon, generateMaze
from classes.geometry import vec2, PI
from classes.entities import boundingbox, entity
from classes.interface import canvas, illustration, palette

'''
    GLOBAL DEFINITIONS
'''
ACTIVE = True

# Threading
TICK_FREQUENCY = 60
TICK_RATE = 1
TICK_RATIO = 1

# Display
WINDOW_DIMENSIONS = vec2(1280, 720) # Dimensions of the displayed window. Defaults to 1080p, should change dynamically
WORLD_DIMENSIONS = vec2(8, 8).add(1, 1) # World coordinate dimensions, affects how objects are oriented on a cartesian map
MINIMAP = canvas(vec2(0, 0), WORLD_DIMENSIONS, vec2(WINDOW_DIMENSIONS.y/4, WINDOW_DIMENSIONS.y/4))
PERSPECTIVE = canvas(vec2(0, 0), WINDOW_DIMENSIONS, WINDOW_DIMENSIONS)
HUD = canvas(WINDOW_DIMENSIONS.divide(2, WINDOW_DIMENSIONS.y).subtract(WINDOW_DIMENSIONS.x/2, 0), WINDOW_DIMENSIONS.divide(1, WINDOW_DIMENSIONS.y * 30 ** -1), WINDOW_DIMENSIONS.divide(1, WINDOW_DIMENSIONS.y * 30 ** -1))
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
PLAYER = entity(vec2(1.5, 1.5), boundingbox(0.1))
LOAD_DISTANCE = 3

# Statistics
LEVEL = 1
MAXIMUM_COUNTDOWN = 30
COUNTDOWN = MAXIMUM_COUNTDOWN
LAST_TICK = 0

# 3D View
RENDER_DISTANCE = LOAD_DISTANCE
RENDER_RESOLUTION = 60
INTERCEPTS = None
VISIBLE_INTERCEPTS = None
RAYS = None

# Misc
RAINBOW = [0, 0, 0]

'''
    GLOBAL FUNCTIONS
'''

# Calculate a multiplier to match a full speed tickrate
def tickRatio():
    ratio = TICK_RATE
    if TICK_RATE > 60:
        ratio = 60

    return TICK_FREQUENCY / ratio

def nextLevel():
    global WORLD, WORLD_DIMENSIONS, COUNTDOWN, LEVEL

    WORLD_DIMENSIONS = WORLD_DIMENSIONS.add(2, 2)

    # Reset the world
    WORLD = terrain(WORLD_DIMENSIONS)
    WORLD.fill()
    WORLD.grid = generateMaze(WORLD.grid, 100)
    WORLD.getSquare(WORLD.dimensions.subtract(1, 2)).setOccupation(polygon('finish', boundingbox(0.1), (0, 255, 0)))

    # Reset player position
    PLAYER.position = vec2(1.5, 1.5)

    # Add thirty seconds to countdown upon completing a level
    COUNTDOWN += 15
    if COUNTDOWN > MAXIMUM_COUNTDOWN: # limit maximum 60
        COUNTDOWN = MAXIMUM_COUNTDOWN

    # Level up
    LEVEL += 1
    if LEVEL > 10:
        pass

def timeBoost():
    global COUNTDOWN
    COUNTDOWN += 5
    if COUNTDOWN > MAXIMUM_COUNTDOWN:
        COUNTDOWN = MAXIMUM_COUNTDOWN

    # Display text???

def updateRainbow():
    pass

'''
    INITIALISATION
'''
def init():
    # Determine the first set of raycasts
    global RAYS
    RAYS = PLAYER.raycast(RENDER_DISTANCE, RENDER_RESOLUTION)

    # Generate the world
    WORLD.fill()
    WORLD.grid = generateMaze(WORLD.grid, 100)
    WORLD.getSquare(WORLD.dimensions.subtract(1, 2)).setOccupation(polygon('finish', boundingbox(0.1), (0, 255, 0)))

    # Define intercepts as an array
    global INTERCEPTS, VISIBLE_INTERCEPTS
    INTERCEPTS = []
    VISIBLE_INTERCEPTS = []

    # Font init
    pygame.font.init()


'''
    MAIN COMPUTATION METHODS
'''

# Processes high level window interaction events from the user.
def eventHandler():
    for event in pygame.event.get(): # Retreive all queued events. Must be ran to display a window (apparently)
        pass

# Reads combinations of keystrokes and handles them accordingly
def keystrokeHandler():
    if not ACTIVE:
        return

    key = pygame.key.get_pressed()
    if key[pygame.K_a] or key[pygame.K_d] or key[pygame.K_w] or key[pygame.K_s]:
        velocity = vec2(0, 0)

        if key[pygame.K_a]:
            velocity.x -= 0.008
        if key[pygame.K_d]:
            velocity.x += 0.008
        if key[pygame.K_w]:
            velocity.y -= 0.008
        if key[pygame.K_s]:
            velocity.y += 0.008
        if key[pygame.K_LSHIFT]:
            velocity = velocity.multiply(1.5, 1.5)

        # Gets a new vector based on difference between the player's yaw and applied velocity. Required for directional movement, and PI/2 there to offset 90 degrees
        relative_velocity = velocity.relative(PLAYER.yaw.subtract(math.atan2(velocity.y, velocity.x) + PI/2)).multiply(TICK_RATIO, TICK_RATIO)
        PLAYER.velocity = PLAYER.velocity.add(relative_velocity.x, relative_velocity.y)

    if key[pygame.K_LEFT]:
        PLAYER.yaw = PLAYER.yaw.add((PI/180) * 3 * TICK_RATIO)
    if key[pygame.K_RIGHT]:
        PLAYER.yaw = PLAYER.yaw.subtract((PI/180) * 3 * TICK_RATIO)

def gameHandler():
    global ACTIVE
    if not ACTIVE:
        return

    '''
        Update the countdown
    '''
    global COUNTDOWN, LAST_TICK
    current_tick = time.time()
    if current_tick - LAST_TICK >= 1:
        LAST_TICK = current_tick
        ACTIVE = COUNTDOWN > 0 # Stay active whilst countdown higher than zero
        if ACTIVE:
            COUNTDOWN -= 1

def entityHandler():
    if not ACTIVE:
        return

    global RAYS

    # Player updates
    RAYS = list(reversed(PLAYER.raycast(RENDER_DISTANCE, RENDER_RESOLUTION)))
    DRAW_QUEUE.append(illustration('circle', ((255, 255, 0), MINIMAP.relative(PLAYER.position, WORLD_DIMENSIONS).display(), PLAYER.boundingbox.radius)), MINIMAP_PRIORITY + 5)
    next_square =  WORLD.getSquare(PLAYER.position.add(PLAYER.velocity.x, PLAYER.velocity.y).floor())

    try:
        if next_square.occupation.type == 'wall':
            PLAYER.velocity = vec2(0, 0)
        elif next_square.occupation.type == 'finish':
            nextLevel()
        elif next_square.occupation.type == 'time':
            next_square.occupation = None
            timeBoost()
            
    except AttributeError:
        pass

    PLAYER.tick()

def gfxHandler():
    if not ACTIVE:
        return

    global RAYS
    global INTERCEPTS

    '''
        Retrieve raycast intercepts
    '''
    for raycast_index in range(len(RAYS)):
        raycast = RAYS[raycast_index]
        squares = WORLD.getAdjacentSquares(PLAYER.position.floor(), LOAD_DISTANCE)
        INTERCEPTS.append({
            'parent': [],
            'intercept': [],
        })
        DRAW_QUEUE.append(illustration('line', ((255, 255, 128), MINIMAP.relative(raycast.start, WORLD_DIMENSIONS).display(), MINIMAP.relative(raycast.finish, WORLD_DIMENSIONS).display(), 1)), MINIMAP_PRIORITY + 3)

        '''
            Determine raycast intercepts with squares in render distance
        '''

        for square in squares:

            if square is None or square.occupation is None:
                continue

            for direction, boundary in square.occupation.boundingbox.boundaries.items():
                boundary_offset = boundary.offset(square.position.add(0.5, 0.5))
                intercept = raycast.intercept(boundary_offset)

                if intercept is None:
                    continue

                INTERCEPTS[raycast_index]['intercept'].append(intercept)
                INTERCEPTS[raycast_index]['parent'].append(square.position)

        '''
            Determine the closest intercepts
        '''
        data = INTERCEPTS[raycast_index]
        closest_distance = -1
        closest_intercept_index = None

        VISIBLE_INTERCEPTS.append({
            'parent': None,
            'intercept': None
        })

        for intercept_index in range(len(data['intercept'])):
            distance = PLAYER.position.distance(data['intercept'][intercept_index])

            if closest_intercept_index is None or distance < closest_distance:
                closest_distance = distance
                closest_intercept_index = intercept_index

        if closest_intercept_index is None:
            continue

        VISIBLE_INTERCEPTS[raycast_index]['parent'] = data['parent'][closest_intercept_index]
        VISIBLE_INTERCEPTS[raycast_index]['intercept'] = data['intercept'][closest_intercept_index]

        '''
            Draw the 3D View.
        ''' 
        data = VISIBLE_INTERCEPTS[raycast_index]
        square = WORLD.getSquare(data['parent'])
        distance = PLAYER.position.distance(data['intercept'])
        distance_multiplier = abs(1 - (distance/RENDER_DISTANCE))
        colour = square.occupation.colour
        colour_multiplier = [1, 1, 1]

        # hacky way of ensuring that the program doesn't divide by zero
        if distance == 0:
            distance = 0.01

        # Walls will burn over time
        if square.occupation.type == 'wall':
            colour_multiplier[0] = 1
            colour_multiplier[1] = colour_multiplier[2] = (COUNTDOWN/MAXIMUM_COUNTDOWN)

        dimensions = PERSPECTIVE.relative(vec2(1 - 0.2, 1/distance), vec2(RENDER_RESOLUTION, RENDER_DISTANCE))
        position = PERSPECTIVE.relative(vec2(raycast_index + 0.5, (RENDER_DISTANCE/2) - (1/(distance*2))), vec2(RENDER_RESOLUTION, RENDER_DISTANCE))
        wall = pygame.Rect(position.display(), dimensions.display())
        DRAW_QUEUE.append(illustration('rectangle', ((colour[0] * colour_multiplier[0] * distance_multiplier, colour[1] * colour_multiplier[1] * distance_multiplier, colour[2] * colour_multiplier[2] * distance_multiplier), wall)), PERSPECTIVE_PRIORITY)

        
    '''
        Draw the minimap.

    ###
    ### INSTEAD OF DOING THIS EVERY TICK, PERHAPS ONLY UPDATE EVERY COUPLE OF SECONDS???
    ###
    
    for x in range(WORLD_DIMENSIONS.x):
        for y in range(WORLD_DIMENSIONS.y):
            position = vec2(x, y)
            square = WORLD.getSquare(position)
            
            if square.occupation is None:
                continue

            for direction, boundary in square.occupation.boundingbox.boundaries.items():
                boundary_offset = boundary.offset(square.position.add(square.occupation.boundingbox.radius, square.occupation.boundingbox.radius))
                DRAW_QUEUE.append(illustration('line', ((255, 255, 255), MINIMAP.relative(boundary_offset.start, WORLD_DIMENSIONS).display(), MINIMAP.relative(boundary_offset.finish, WORLD_DIMENSIONS).display(), 1)), MINIMAP_PRIORITY + 2)

    '''
        

def interfaceHandler():
    WINDOW.fill((0, 0, 0)) # Clear the current screen

    if ACTIVE:
        countdown = pygame.font.SysFont('Arial Unicode MS', 32).render(f'Time remaining: {COUNTDOWN}', False, (255, 255, 255))
        level = pygame.font.SysFont('Arial Unicode MS', 32).render(f'Level {LEVEL}', False, (255, 255, 255))
        WINDOW.blit(countdown, HUD.relative(vec2((WINDOW_DIMENSIONS.x / 2) - (countdown.get_width() / 2), 0), WINDOW_DIMENSIONS).display()) # Center text in HUD
        WINDOW.blit(level, HUD.relative(vec2(WINDOW_DIMENSIONS.x - level.get_width(), 0), WINDOW_DIMENSIONS).display())

        #DRAW_QUEUE.append(illustration('rectangle', ((255, 255, 255), pygame.Rect(HUD.position.x, HUD.position.y, HUD.display_dimensions.x, HUD.display_dimensions.y))), MINIMAP_PRIORITY + 1)
        #DRAW_QUEUE.append(illustration('rectangle', ((0, 0, 0), pygame.Rect(MINIMAP.position.x, MINIMAP.position.y, MINIMAP.display_dimensions.x, MINIMAP.display_dimensions.y))), MINIMAP_PRIORITY + 1)
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
    global TICK_RATIO, ACTIVE
    TICK_RATIO = tickRatio()

    current_time = time.time()
    eventHandler()
    print(f'eventHandler time: {round(time.time() - current_time, 4) * 1000}ms')
    current_time = time.time()
    keystrokeHandler()
    print(f'keystrokeHandler time: {round(time.time() - current_time, 4) * 1000}ms')
    current_time = time.time()
    gameHandler()
    print(f'gameHandler time: {round(time.time() - current_time, 4) * 1000}ms')
    current_time = time.time()
    entityHandler()
    print(f'entityHandler time: {round(time.time() - current_time, 4) * 1000}ms')
    current_time = time.time()
    gfxHandler()
    print(f'gfxtHandler time: {round(time.time() - current_time, 4) * 1000}ms')
    current_time = time.time()
    interfaceHandler()
    print(f'interfaceHandler time: {round(time.time() - current_time, 4) * 1000}ms')
    current_time = time.time()
    drawHandler()
    print(f'drawHandler time: {round(time.time() - current_time, 4) * 1000}ms\n')
    current_time = time.time()
    resetHandler()

'''
    THREAD HANDLER
'''

def tick():
    global TICK_RATE

    # Record initial time before code execution
    time_initial = time.time()

    # Fat CPU computation
    computation()

    # Record time after code execution and compare difference to ticks.
    time_post = time.time()
    time_ratio = (1/TICK_FREQUENCY) # expected tick time
    time_difference = time_post - time_initial # actual tick time

    if time_difference < time_ratio:
        time.sleep(time_ratio - time_difference) # pause execution until the tick is done
    else:
        pass
        #warnings.warn(f'Couldn\'t keep up! Running {round(time_difference, 2)}s behind expected interval of {TICK_FREQUENCY} ticks per second. ({int((time_difference * TICK_FREQUENCY) * 100)}% slower)', RuntimeWarning, stacklevel=4)

    TICK_RATE = (time_ratio/time_difference) * TICK_FREQUENCY
    
def threadHandler():
    while True:
        tick()
        
if __name__ == '__main__':
    init()
    threadHandler()