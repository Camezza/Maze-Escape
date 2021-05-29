from dataclasses import dataclass
from geometry import vec2

'''
    A class for managing multiple dynamic interfaces on a single window
'''
@dataclass
class canvas:
    position: vec2 # Bottom left corner of the interface
    internal_dimensions: vec2 # The internal dimensions used for aligning absolute positions of objects
    display_dimensions: vec2 # The dimensions of the canvas which is actually displayed on the main window

    '''
        Get an object's relative position to the canvas
    '''
    def relative(self, object_position: vec2, window_dimensions: vec2):
        canvas_dimension_ratio = self.internal_dimensions.divide(window_dimensions.x, window_dimensions.y) # Retrieve a decimal ratio of the object's real coords to virtual canvas coordinates
        canvas_dimension_position = canvas_dimension_ratio.multiply(object_position.x, object_position.y)
        canvas_display_ratio = self.display_dimensions.multiply(canvas_dimension_ratio.x, canvas_dimension_ratio.y) # Get the relative display position from canvas's actual position
        real_position = self.position.add(canvas_display_ratio.x, canvas_display_ratio.y)
        return real_position