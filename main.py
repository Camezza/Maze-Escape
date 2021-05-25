import pygame, sys
from pygame.locals import *

pygame.init()

DISPLAY = pygame.display

window = DISPLAY.set_mode((400, 300)) # Initialise window
DISPLAY.set_caption('Hello World!') # Set the window title

while True: # main game loop
    for event in pygame.event.get(): # Retreive all queued events. Must be ran to display a window
        pass
    # draw simple surface
    surface = pygame.Surface((0, 0))
    rectangle = pygame.Rect((0, 0), (200, 200))
    pygame.draw.rect(window, (255, 255, 255), rectangle)

    pygame.display.update() # Update the window displayed
