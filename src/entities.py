from dataclasses import dataclass
from geometry import vec2, angle
from world import FRICTION

@dataclass
class entity:
    position: vec2
    velocity = vec2(0, 0)

    def applyVelocity(self):
        self.position = self.position.add(self.velocity.x, self.velocity.y)

    def tick(self):
        '''
            Update velocity
        '''
        self.applyVelocity()
        self.velocity = self.velocity.divide(FRICTION, FRICTION)

class player(entity):
    yaw = angle(0)
    pass