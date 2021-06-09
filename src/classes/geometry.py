import math
from dataclasses import dataclass
PI = 22/7

@dataclass
class angle:
    radians: float

    def add(self, radian: float):
        new = self.radians + radian
        if new > (2 * PI): # larger than 360 (2 pi)
            return angle(new - (2 * PI))
        return angle(new)
        
    def subtract(self, radian: float):
        new = self.radians - radian
        if new < 0: # restrict angles less than 0 
            return angle(new + (2 * PI))
        return angle(new)

'''
    A class for management of 2d vectors
'''
@dataclass
class vec2:
    x: float
    y: float

    def add(self, x: float, y: float):
        return vec2(self.x + x, self.y + y)

    def subtract(self, x: float, y: float):
        return vec2(self.x - x, self.y - y)

    def multiply(self, x: float, y: float):
        return vec2(self.x * x, self.y * y)

    def divide(self, x: float, y: float):
        return vec2(self.x / x, self.y / y)

    def length(self):
        return ((self.x ** 2) + (self.y ** 2)) ** (1/2)

    def distance(self, position):
        difference = position.subtract(self.x, self.y)
        return ((difference.x ** 2) + (difference.y ** 2)) ** (1/2)

    def relative(self, angle: angle):
        radius = self.length()
        return vec2(math.sin(angle.radians) * radius, math.cos(angle.radians) * radius)

    def display(self):
        return (self.x, self.y)

'''
    A line ranging from point A to point B. Extends ray class
'''
@dataclass
class line:
    start: vec2
    finish: vec2

    def offset(self, position: vec2):
        start = self.start.add(position.x, position.y)
        finish = self.finish.add(position.x, position.y)
        return line(start, finish)

    def scale(self, reference_dimensions: vec2, absolute_dimensions: vec2):
        start = vec2((self.start.x/reference_dimensions.x) * absolute_dimensions.x, (self.start.y/reference_dimensions.y) * absolute_dimensions.y)
        finish = vec2((self.finish.x/reference_dimensions.x) * absolute_dimensions.x, (self.finish.y/reference_dimensions.y) * absolute_dimensions.y)
        return line(start, finish)

    def intercept(self, line):
        '''
            Simple line equation to find where rays intercept. y = mx + b = m(x-c)/a
        '''
        line1_difference = self.finish.subtract(self.start.x, self.start.y)
        line2_difference = line.finish.subtract(line.start.x, line.start.y)
        x = y = None # initialise

        '''
            Determine which to sub for what. Required as programming (unlike maths) isn't dynamic and is required to be predefined
        '''
        if (line1_difference.y == 0 and line1_difference.x == 0) or (line2_difference.y == 0 and line2_difference.x == 0): # both y = b and x = c
            return None

        elif line1_difference.y == 0 or line2_difference.y == 0: # where y = b
            # Lines will never intercept, as both equations equal constants
            if line1_difference.y == 0 and line2_difference.y == 0:
                return None

            elif line1_difference.y == 0:
                m = line2_difference.y / line2_difference.x
                b = line.start.y - (m * line.start.x)
                x = (self.start.y - b)/m
                y = self.start.y

            elif line2_difference.y == 0:
                m = line1_difference.y / line1_difference.x
                b = self.start.y - (m * self.start.x)
                x = (line.start.y - b)/m
                y = line.start.y

        elif line1_difference.x == 0 or line2_difference.x == 0: # where x = c
            if line1_difference.x == 0 and line2_difference.x == 0:
                return None

            elif line1_difference.x == 0:
                m = line2_difference.y / line2_difference.x
                b = line.start.y - (m * line.start.x)
                x = self.start.x
                y = (m * x) + b

            elif line2_difference.x == 0:
                m = line1_difference.y / line1_difference.x
                b = self.start.y - (m * self.start.x)
                x = line.start.x
                y = (m * x) + b

        # Retreive the domains and ranges
        ray1_x_min = min(self.start.x, self.finish.x)
        ray1_x_max = max(self.start.x, self.finish.x)

        ray1_y_min = min(self.start.y, self.finish.y)
        ray1_y_max = max(self.start.y, self.finish.y)

        ray2_x_min = min(line.start.x, line.finish.x)
        ray2_x_max = max(line.start.x, line.finish.x)

        ray2_y_min = min(line.start.y, line.finish.y)
        ray2_y_max = max(line.start.y, line.finish.y)

        # Determine if line intercepts between each ray's domain and range
        ray1Domain: bool = (ray1_x_min <= x and x <= ray1_x_max)
        ray2Domain: bool = (ray2_x_min <= x and x <= ray2_x_max)
        ray1Range: bool = (ray1_y_min <= y and y <= ray1_y_max)
        ray2Range: bool = (ray2_y_min <= y and y <= ray2_y_max)

        # restrict to ray domain and range
        if ray1Domain and ray2Domain and ray1Range and ray2Range:
            return vec2(x, y)

        return None