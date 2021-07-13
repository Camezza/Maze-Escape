from dataclasses import dataclass
from typing import Optional, List
from classes.geometry import vec2, line
import math
import random

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
        coordinates.append(position.add(math.copysign(x, radius_x), radius_y))

        if x == abs(radius_x) - 1:
            for y in range(1, abs(radius_y)):
                coordinates.append(position.add(radius_x, math.copysign(y, radius_y)))
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
    Maze generation
'''
def generateMaze(reference):
    assert len(reference) > 3, f'grid x axis needs to be larger than 3, got {len(reference)}'
    assert len(reference[0]) > 3, f'grid y axis needs to be larger than 3, got {len(reference[0])}' # We can do this as coordinates are regular
    assert len(reference) % 2 != 0 and len(reference[0]) % 2 != 0, 'Grid needs to be an odd value.'

    grid = [[y for y in x] for x in reference]
    dimensions = vec2(len(grid), len(grid[0]))

    start = vec2(1, 1) # offset from wall
    finish = vec2(dimensions.x - 1, dimensions.y - 1) # coordinates start at 0, offset from wall

    # Clear a hole for the start and finish of the maze
    grid[start.x-1][start.y].occupation = None
    grid[finish.x][finish.y-1].occupation = None

    current_position = None
    cache = [start]

    # still have valid places to move
    while len(cache) > 0:
        current_position = cache[len(cache) - 1]
        directional = []
        
        for direction in CARDINAL:
            query = current_position.add(direction[0] * 2, direction[1] * 2) # 2 spaces in each direction
            difference = dimensions.subtract(query.x + 1, query.y + 1)

            # determine if space hasn't been taken yet and is inside the grid
            inside = (difference.x > 0 and difference.y > 0) and (difference.x < dimensions.x and difference.y < dimensions.y)

            if inside and not grid[query.x][query.y].occupation is None:
                directional.append(query)

        valid = None
        # select a random direction
        if len(directional) > 0:
            valid = directional[int(random.randint(0, len(directional)-1))]

        if not valid is None:

            # Remove every square from current position to new position
            difference = valid.subtract(current_position.x, current_position.y).floor()
            if difference.x == 0:
                for y in range(0, difference.y, int(math.copysign(1, difference.y))):
                    query = current_position.add(0, y).floor()
                    grid[query.x][query.y].occupation = None

            elif difference.y == 0:
                for x in range(0, difference.x, int(math.copysign(1, difference.x))):
                    query = current_position.add(x, 0).floor()
                    grid[query.x][query.y].occupation = None

            else:
                raise RuntimeError('Offset either non cardinal or same as starting position.')

            grid[valid.x][valid.y].occupation = None
            cache.append(valid)
            continue

        # No valid directions left; remove last element from cache and backtrack
        cache.pop()

    return grid

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
    def generate(self):
        self.grid = []
        # fill in x axis
        for x in range(self.dimensions.x):
            self.grid.append([])
            # fill in y axis
            for y in range(self.dimensions.y):
                position = vec2(x, y)
                self.grid[x].append(square(position))
    
    def fill(self):
        for x in range(self.dimensions.x):
            for y in range(self.dimensions.y):
                self.getSquare(vec2(x, y)).setOccupation(polygon(boundingbox(0.5)))

    '''
        Retrieves a square from a defined terrain. Returns None if coordinate doesn't exist
    '''
    def getSquare(self, position: vec2) -> square:
        try:
            assert position.x >= 0 and position.y >= 0
            return self.grid[position.x][position.y]
        except (IndexError, AssertionError):
            return None

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
        self.generate()
