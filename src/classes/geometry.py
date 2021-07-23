import math
from dataclasses import dataclass
from profilehooks import profile

'''
    GLOBAL CONSTANTS    
'''
PI = 22/7
FIRST_COMPONENT_REFERENCE = ['NORTH', '', 'SOUTH']
SECOND_COMPONENT_REFERENCE = ['EAST', '', 'WEST']

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
        self.x += x
        self.y += y

    def subtract(self, x: float, y: float):
        self.x -= x
        self.y -= y

    def multiply(self, x: float, y: float):
        self.x *= x
        self.y *= y

    def divide(self, x: float, y: float):
        self.x /= x
        self.y /= y

    def floor(self):
        self.x = math.floor(self.x)
        self.y = math.floor(self.y)

    def length(self):
        return ((self.x ** 2) + (self.y ** 2)) ** (1/2)

    def distance(self, position):
        return (((position.x - self.x) ** 2) + ((position.y - self.y) ** 2)) ** (1/2)

    def relative(self, angle: angle):
        radius = self.length()
        return vec2(math.sin(angle.radians) * radius, math.cos(angle.radians) * radius)

    def direction(self):
        first_component = int(math.copysign(1, self.y) + 1)
        second_component = int(math.copysign(1, self.x) + 1)

        if self.x == 0:
            return FIRST_COMPONENT_REFERENCE[first_component]
        elif self.y == 0:
            return SECOND_COMPONENT_REFERENCE[second_component]
        elif self.x == 0 and self.y == 0:
            return None
        else:
            return FIRST_COMPONENT_REFERENCE[first_component] + '-' + SECOND_COMPONENT_REFERENCE[second_component]

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
        start = vec2(self.start.x + position.x, self.start.y + position.y)
        finish = vec2(self.finish.x + position.x, self.finish.y + position.y)
        return line(start, finish)

    def scale(self, reference_dimensions: vec2, absolute_dimensions: vec2):
        start = vec2((self.start.x/reference_dimensions.x) * absolute_dimensions.x, (self.start.y/reference_dimensions.y) * absolute_dimensions.y)
        finish = vec2((self.finish.x/reference_dimensions.x) * absolute_dimensions.x, (self.finish.y/reference_dimensions.y) * absolute_dimensions.y)
        return line(start, finish)

    def intercept(self, line):
        '''
            Simple line equation to find where rays intercept. y = mx + b = m(x-c)/a
        '''
        line1_difference = vec2(self.finish.x - self.start.x, self.finish.y - self.start.y)
        line2_difference = vec2(line.finish.x - line.start.x, line.finish.y - line.start.y)
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
        ray1_domain = (x <= self.start.x and x >= self.finish.x) or (x >= self.start.x and x <= self.finish.x)
        ray1_range = (y <= self.start.y and y >= self.finish.y) or (y >= self.start.y and y <= self.finish.y)
        ray2_domain = (x <= line.start.x and x >= line.finish.x) or (x >= line.start.x and x <= line.finish.x)
        ray2_range = (y<= line.start.y and y >= line.finish.y) or (y >= line.start.y and y <= line.finish.y)

        # restrict to ray domain and range
        if ray1_domain and ray2_domain and ray1_range and ray2_range:
            return vec2(x, y)

        return None

    def direction(self):
        direction = vec2(self.finish.x - self.start.x, self.finish.y - self.start.y).direction()
        if direction is None:
            raise RuntimeError('Line doesn\'t have a direction! Are the line\'s start and finish vectors the same value?')
        return direction