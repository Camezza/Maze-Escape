from dataclasses import dataclass
from typing import Optional, List
from classes.geometry import vec2, line
from math import copysign

'''
    Global
'''

FRICTION = 1.5
CARDINAL = [[1, 0],[0, 1],[-1, 0],[0, -1]]
DIAGONAL = [[1, 1],[-1, 1],[-1, -1],[1, -1]]
'''
    Get adjacent coordinates
'''
def adjacentCorner(position: vec2, radius_x: int, radius_y: int) -> List[vec2]:
    coordinates = []
    for x in range(1, abs(radius_x)):
        coordinates.append(position.add(copysign(x, radius_x), radius_y))

        if x == abs(radius_x) - 1:
            for y in range(1, abs(radius_y)):
                coordinates.append(position.add(radius_x, copysign(y, radius_y)))
    return coordinates

def adjacentDirectional(position: vec2, radius: int) -> List[vec2]:
    coordinates = []

    for i in range(4):
        cardinal_coordinate = position.add(CARDINAL[i][0] * radius, CARDINAL[i][1] * radius)
        diagonal_coordinate = position.add(DIAGONAL[i][0] * radius, DIAGONAL[i][1] * radius)
        miscellaneous_coordinates = adjacentCorner(position, DIAGONAL[i][0] * radius, DIAGONAL[i][1] * radius)
        miscellaneous_coordinates.extend([cardinal_coordinate, diagonal_coordinate])
        coordinates.extend(miscellaneous_coordinates)
    
    return coordinates

'''
    Objects, collision, etc
'''

@dataclass
class boundingbox:
    radius: int
    boundaries = None

    def __post_init__(self):
        self.boundaries = {
            'NORTH': line(vec2(self.radius, self.radius), vec2(-self.radius, self.radius)),
            'SOUTH': line(vec2(-self.radius, self.radius), vec2(-self.radius, -self.radius)),
            'EAST': line(vec2(-self.radius, -self.radius), vec2(self.radius, -self.radius)),
            'WEST': line(vec2(self.radius, -self.radius), vec2(self.radius, self.radius)),
        }

    def directional(self, line: vec2) -> List[line]:
        boundaries = []
        direction = line.direction()
        for iterator in direction.split('-'):
            boundaries.append(self.boundaries[iterator])
        return boundaries
            
            

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
    def getSquare(self, position: vec2) -> square:
        try:
            return self.grid[position.x][position.y]
        except AttributeError:
            raise RuntimeError('Could not retrieve square that is not in coordinate scope')

    def getAdjacentSquares(self, position: vec2, radius: int) -> List[square]:
        coordinates = []
        for iterator in range(radius):
            coordinates.extend(adjacentDirectional(position, iterator + 1))

        squares = []
        for offset in coordinates:
            try: # simply push if no error
                square = self.getSquare(offset.floor())
                squares.append(square)
            except:
                pass
        
        return squares
            
    def __post_init__(self):
        self.grid = self.generate_grid()
