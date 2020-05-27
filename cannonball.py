import pygame
from pygame.sprite import Sprite


class Cannonball(Sprite):
    """Projectile shot by Cannon

    Parents
    -------
    pygame.sprite.Sprite
    """

    def __init__(self, screen, angle, file, coords):
        super().__init__()
        self.screen = screen
        self.image = file
        self.angle = angle
        self.coords = coords
        self.velocity = np.array([speed * math.cos(self.angle),
                                  -speed * math.sin(self.angle)])
