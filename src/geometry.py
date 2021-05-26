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

    def intercept(self, point: vec2):
        pass
