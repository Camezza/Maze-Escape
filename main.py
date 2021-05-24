import pygame, sys
from pygame.locals import *

pygame.init()
pygame.display.set_mode((400, 300)) # Initialise window
pygame.display.set_caption('Hello World!') # Set the window title

while True: # main game loop
    for event in pygame.event.get(): # Retreive all queued events. Must be ran to display a window
        if event == KEYDOWN:
            pygame.display.toggle_fullscreen()
    pygame.display.update() # Update the window displayed
