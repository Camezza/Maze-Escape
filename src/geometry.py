import math
from dataclasses import dataclass
from typing import List
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

@dataclass
class ray:
    start: vec2
    finish: vec2

'''
    A line ranging from point A to point B. Extends ray class
'''
class line(ray):
    def intercept(self, ray: ray):
        '''
            Simple line equation to find where rays intercept. y = mx + b = m(x-c)/a
        '''
        ray1_difference = self.finish.subtract(self.start.x, self.start.y)
        ray2_difference = ray.finish.subtract(ray.start.x, ray.start.y)
        x = y = None # initialise

        '''
            Determine which to sub for what. Required as programming (unlike maths) isn't dynamic and is required to be predefined
        '''
        if (ray1_difference.y == 0 and ray1_difference.x == 0) or (ray2_difference.y == 0 and ray2_difference.x == 0): # both y = b and x = c
            return None

        elif ray1_difference.y == 0 or ray2_difference.y == 0: # where y = b
            # Lines will never intercept, as both equations equal constants
            if ray1_difference.y == 0 and ray2_difference.y == 0:
                return None

            elif ray1_difference.y == 0:
                m = ray2_difference.y / ray2_difference.x
                b = ray.start.y - (m * ray.start.x)
                x = (self.start.y - b)/m
                y = self.start.y

            elif ray2_difference.y == 0:
                m = ray1_difference.y / ray1_difference.x
                b = self.start.y - (m * self.start.x)
                x = (ray.start.y - b)/m
                y = ray.start.y

        elif ray1_difference.x == 0 or ray2_difference.x == 0: # where x = c
            if ray1_difference.x == 0 and ray2_difference.x == 0:
                return None

            elif ray1_difference.x == 0:
                m = ray2_difference.y / ray2_difference.x
                b = ray.start.y - (m * ray.start.x)
                x = self.start.x
                y = (m * x) + b

            elif ray2_difference.x == 0:
                m = ray1_difference.y / ray1_difference.x
                b = self.start.y - (m * self.start.x)
                x = ray.start.x
                y = (m * x) + b

        # Retreive the domains and ranges
        ray1_x_min = min(self.start.x, self.finish.x)
        ray1_x_max = max(self.start.x, self.finish.x)

        ray1_y_min = min(self.start.y, self.finish.y)
        ray1_y_max = max(self.start.y, self.finish.y)

        ray2_x_min = min(ray.start.x, ray.finish.x)
        ray2_x_max = max(ray.start.x, ray.finish.x)

        ray2_y_min = min(ray.start.y, ray.finish.y)
        ray2_y_max = max(ray.start.y, ray.finish.y)

        # Determine if line intercepts between each ray's domain and range
        ray1Domain: bool = (ray1_x_min <= x and x <= ray1_x_max)
        ray2Domain: bool = (ray2_x_min <= x and x <= ray2_x_max)
        ray1Range: bool = (ray1_y_min <= y and y <= ray1_y_max)
        ray2Range: bool = (ray2_y_min <= y and y <= ray2_y_max)

        # restrict to ray domain and range
        if ray1Domain and ray2Domain and ray1Range and ray2Range:
            return vec2(x, y)

        return None