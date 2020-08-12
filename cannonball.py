import pygame
from pygame.sprite import Sprite
import numpy as np
from settings import CB_SPEED, C_RANGE, CB_MULT
import math


class Cannonball(Sprite):
    """Projectile shot by Cannon

    Parents
    -------
    pygame.sprite.Sprite

    Attributes
    ----------
    screen : pygame.Surface
        Surface on which Infantry is drawn
    image : pygame.image
        current image used by Cannonball
    angle : float
        angle in radians of Cannonball to x-axis
    coords  : float 1-D numpy.ndarray [2], >= 0
        coords of Cannonball as float to avoid rounding errors
    velocity : float 1-D numpy.ndarray [2]
        velocity of Cannonball in x, y directions
    rect : pygame.rect.Rect
        rectangle of Cannonball Surface
    travelled : float, >= 0
        distance travelled by Cannonball
    enemies : list of Battery, Company, Squadron
        list of all units with different team value

    Methods
    -------
    update
        move Cannonball, kill enemies in contact, remove at max distance
    blitme
        draw Cannonball on screen
    """

    def __init__(self, screen, angle, file, coords, enemies, size):
        super().__init__()
        self.screen = screen
        self.image = file
        self.angle = angle
        self.coords = coords
        self.velocity = np.array([CB_SPEED * math.cos(self.angle),
                                  -CB_SPEED * math.sin(self.angle)])
        self.rect = self.image.get_rect()
        self.rect.center = self.coords
        self.travelled = 0
        self.enemies = enemies
        self.size = size

    def update(self, cannon):
        # move Cannonball, kill enemies in contact, remove at max distance
        for company in self.enemies:
            if self.rect.colliderect(company.rect):
                company.getShelled(self.size, self.angle)
                self.enemies.remove(company)
        self.coords += self.velocity
        self.travelled += CB_SPEED
        if self.travelled > C_RANGE * CB_MULT:
            cannon.shot = None

    def blitme(self):
        # draw Cannonball on screen
        self.rect = self.image.get_rect()
        self.rect.center = self.coords
        self.screen.blit(self.image, self.rect)
