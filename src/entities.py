import math
from dataclasses import dataclass
from geometry import vec2, angle, PI, ray
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
    fov = angle(PI/2)

    '''
        Physics
    '''
    def retrieveRays(self, render_distance: int, render_amount: int):
        rays = []
        iterator = self.fov.radians / render_amount
        minimum = self.yaw.subtract(self.fov.radians/2)
        for i in range(render_amount):
            radians = minimum.add(i * iterator).radians
            raycast = ray(self.position, self.position.add(math.sin(radians) * render_distance, math.cos(radians) * render_distance))
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