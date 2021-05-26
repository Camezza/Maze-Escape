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
        self.x += x
        self.y += y

    def subtract(self, x: int, y: int):
        self.x -= x
        self.y -= y

    def multiply(self, x: int, y: int):
        self.x *= x
        self.y *= y

@dataclass
class ray:
    start: vec2   
    finish: vec2

class line(ray):
    def retreiveIntercept(self, ray: ray):
        '''
            Simple line equation to find where rays intercept. y = mx + b
        '''

        ray1_m = (self.finish.x - self.start.x)/(self.finish.y - self.start.y) # gradient = (x_2-x_1)/(y_2-y_1)
        ray1_b = self.start.y - (ray1_m * self.start.x) # y - mx = vertical offset (can also use y2 and x2)
        ray2_m = (ray.finish.x - ray.start.x)/(ray.finish.y - ray.start.y)
        ray2_b = ray.start.y - (ray2_m * ray.start.x)


        # retreive 
