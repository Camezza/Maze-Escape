from dataclasses import dataclass
from typing import Optional, List
from classes.geometry import vec2, line

FRICTION = 1.5

'''
    Objects, collision, etc
'''

@dataclass
class boundingbox:
    radius: int
    boundaries: Optional[List[line]] = None

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
    display: Optional[List[line]] = None # generate a boundingbox relative shape by default

    def __post_init__(self):
        if self.display is None:
            self.display = self.boundingbox.boundaries

'''
    Coordinate occupation
'''
@dataclass
class square:
    position: vec2
    occupation: Optional[polygon] = None

    def setOccupation(self, occupation: object):
        self.occupation = occupation

@dataclass
class terrain:
    dimensions: vec2
    grid: List[List[square]] = None

    '''
        Define grid for own coordinates
    '''
    def generate_grid(self) -> List[List[square]]:
        grid: List[List[square]] = []
        # fill in x axis
        for x in range(self.dimensions.x):
            grid.append([])
            # fill in y axis
            for y in range(self.dimensions.y):
                position = vec2(x, y)
                grid[x].append(square(position))

        return grid

    '''
        Retrieves a square from a defined terrain. Returns None if coordinate doesn't exist
    '''
    def getSquare(self, vec2: vec2) -> square:
        try:
            return self.grid[vec2.x][vec2.y]
        except AttributeError:
            raise Exception('Could not retrieve square that is not in coordinate scope')

    def __post_init__(self):
        self.grid = self.generate_grid()
