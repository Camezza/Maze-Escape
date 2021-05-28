from dataclasses import dataclass
from geometry import vec2, angle, PI
from world import FRICTION

@dataclass
class boundingbox:
    radius: int

@dataclass
class entity:
    position: vec2
    boundingbox: boundingbox
    
    velocity = vec2(0, 0)
    yaw = angle(0)

    def applyVelocity(self):
        self.position = self.position.add(self.velocity.x, self.velocity.y)

    def tick(self):
        '''
            Update velocity
        '''
        self.applyVelocity()
        self.velocity = self.velocity.divide(FRICTION, FRICTION)

class player(entity):
    fov = angle(PI/2)
    pass