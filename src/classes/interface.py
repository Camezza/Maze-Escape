from typing import Dict, Tuple
from dataclasses import dataclass, field
from classes.geometry import vec2

'''
    Allows drawing functions to be queued so they can be displayed in correct order
'''
@dataclass
class illustration:
    draw_func: str
    draw_parameters: Tuple

    def draw(self, reference, surface):
        reference[self.draw_func](surface, *self.draw_parameters)

@dataclass
class palette:
    queue: Dict[illustration, int] = None

    def __post_init__(self):
        self.queue = {}

    def append(self, drawing: illustration, priority: int):
        try:
            self.queue[priority].append(drawing)
        except KeyError:
            self.queue[priority] = []
            self.queue[priority].append(drawing)

    def reset(self):
        self.queue = {}

'''
    A class for managing multiple dynamic interfaces on a single window
'''
@dataclass
class canvas:
    position: vec2 # Bottom left corner of the interface
    internal_dimensions: vec2 # The internal dimensions used for aligning absolute positions of objects
    display_dimensions: vec2 # The dimensions of the canvas which is actually displayed on the main window

    def ratio(self, window_dimensions):
        return self.display_dimensions.divide(window_dimensions.x, window_dimensions.y)

    '''
        Get an object's relative position to the canvas
    '''
    def relative(self, object_position: vec2, window_dimensions: vec2):
        # Retrieve a decimal ratio of the object's real coords to virtual canvas coordinates
        # for example: 1000px original, 200px canvas = 0.2 ratio (200/1000)
        canvas_dimension_ratio = self.internal_dimensions.divide(window_dimensions.x, window_dimensions.y) 

        # Squash the object's original position down to match the ratio. (Note this isn't aligned correctly yet, hence the next step)
        canvas_dimension_position = canvas_dimension_ratio.multiply(object_position.x, object_position.y)

        # Now that we have the updated canvas position, we need to retrieve a ratio of it to the internal dimentions of the canvas. This will be used for display.
        canvas_display_ratio = canvas_dimension_position.divide(self.internal_dimensions.x, self.internal_dimensions.y)

        # This ratio can now be applied to the display dimensions, which the user actually sees. However, this isn't relative to the canvas's position yet.
        canvas_display_position = self.display_dimensions.multiply(canvas_display_ratio.x, canvas_display_ratio.y)

        # An offset of the object to the canvas's position. This is the true position of the object.
        final_position = self.position.add(canvas_display_position.x, canvas_display_position.y)
        return final_position

def colourDistanceMultiplier(distance: float, gamma: int):
    relative_colour = gamma/distance
    if distance < 1 or relative_colour > 1:
        return 1
    return relative_colour