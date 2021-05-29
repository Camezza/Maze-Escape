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

    def relative(self, angle: angle):
        radius = ((self.x ** 2) + (self.y ** 2)) ** (1/2)
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
            Simple line equation to find where rays intercept. y = mx + b
        '''
        ray1_m = (self.finish.x - self.start.x)/(self.finish.y - self.start.y) # gradient = (x_2-x_1)/(y_2-y_1)
        ray1_b = self.start.y - (ray1_m * self.start.x) # y - mx = vertical offset (can also use y2 and x2)
        ray2_m = (ray.finish.x - ray.start.x)/(ray.finish.y - ray.start.y)
        ray2_b = ray.start.y - (ray2_m * ray.start.x)
        x = (ray2_b - ray1_b)/(ray1_m - ray2_m)
        y = (ray1_m * x) + ray1_b # sub x into original equation 

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