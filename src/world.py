from typing import List
from dataclasses import dataclass
from typing import Optional
from geometry import vec2, line

FRICTION = 1.05

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
class square:
    position: vec2
    occupation: Optional[object] = None

@dataclass
class wall(object):
    boundingbox: boundingbox
    pass

