import math
from typing import Optional
from dataclasses import dataclass
from geometry import vec2, angle, PI, line
from world import FRICTION, boundingbox

@dataclass
class entity:
    position: vec2
    boundingbox: boundingbox
    fov: Optional[angle] = angle(PI/2)
    
    yaw = angle(0)
    velocity = vec2(0, 0)

    '''
        Physics
    '''
    def retrieveRays(self, render_distance: int, render_amount: int):
        rays = []
        iterator = self.fov.radians / render_amount
        minimum = self.yaw.subtract(self.fov.radians/2)
        for i in range(render_amount):
            radians = minimum.add(i * iterator).radians
            raycast = line(self.position, self.position.add(math.sin(radians) * render_distance, math.cos(radians) * render_distance))
            rays.append(raycast)

        return rays

    '''
        Update
    '''
    def tick(self):
        self.position = self.position.add(self.velocity.x, self.velocity.y) # Update velocity
        self.velocity = self.velocity.divide(FRICTION, FRICTION) # Apply friction constant to current velocity

class player(entity):
    pass