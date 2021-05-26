from dataclasses import dataclass
from typing import List

'''
    A class for management of 2d vectors
'''
@dataclass
class vec2:
    x: int
    y: int

    def add(self, x: int, y: int):
        return vec2(self.x + x, self.y + y)

    def subtract(self, x: int, y: int):
        return vec2(self.x - x, self.y - y)

    def multiply(self, x: int, y: int):
        return vec2(self.x * x, self.y * y)

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
        x_min = min(self.start.x, self.finish.x, ray.start.x, ray.finish.x)
        x_max = max(self.start.x, self.finish.x, ray.start.x, ray.finish.x)

        y_min = min(self.start.y, self.finish.y, ray.start.y, ray.finish.y)
        y_max = max(self.start.y, self.finish.y, ray.start.y, ray.finish.y)

        # restrict to ray domain and range
        if (x_min <= x and x <= x_max) and (y_min <= y and y <= y_max):
            return vec2(x, y)
        return None