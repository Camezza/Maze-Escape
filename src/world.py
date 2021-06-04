from typing import List
from dataclasses import dataclass
from typing import Optional, List
from geometry import vec2, line

FRICTION = 1.05

'''
    Objects, collision, etc
'''

@dataclass
class boundingbox:
    radius: int
    boundaries: Optional[List[vec2]] = None

    def __post_init__(self):
        if self.boundaries is None: # Most entities don't require specialised bounding box
            self.boundaries = [
                line(vec2(0, 0), vec2(0, self.radius)),
                line(vec2(0, self.radius), vec2(self.radius, self.radius)),
                line(vec2(self.radius, self.radius), vec2(self.radius, 0)),
                line(vec2(self.radius, 0), vec2(0, 0)),
            ]

@dataclass
class object:
    boundingbox: boundingbox

@dataclass
class polygon(object):
    display: Optional[List[line]] = boundingbox.boundaries # generate a boundingbox relative shape by default

'''
    Coordinate & space occupation
'''

@dataclass
class square:
    position: vec2
    occupation: Optional[object] = None

    def setOccupation(self, occupation: object):
        self.occupation = occupation

@dataclass
class terrain:
    dimensions: vec2
    grid: List[List[square]] = None

    '''
        Define grid for own coordinates
    '''
    def generate_grid(self):
        grid: List[List[square]] = []
        # fill in x axis
        for x in range(self.dimensions.x):
            grid.append([])
            # fill in y axis
            for y in range(self.dimensions.y):
                grid[x].append(square(vec2(x, y)))

        return grid

    '''
        Retrieves a square from a defined terrain. Returns None if coordinate doesn't exist
    '''
    def getSquare(self, vec2):
        try:
            return self.grid[vec2.x][vec2.y]
        except AttributeError:
            return None

    def __post_init__(self):
        self.grid = self.generate_grid()
