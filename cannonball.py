import pygame
from pygame.sprite import Sprite
import numpy as np
from settings import CB_SPEED, C_RANGE
import math


class Cannonball(Sprite):
    """Projectile shot by Cannon

    Parents
    -------
    pygame.sprite.Sprite
    """

    def __init__(self, screen, angle, file, coords, enemies):
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

    def update(self, cannon):
        for company in self.enemies:
            if any([self.rect.colliderect(nt.rect) for nt in company.troops]):
                company.getShelled(self)
        self.coords += self.velocity
        self.travelled += CB_SPEED
        if self.travelled > C_RANGE:
            cannon.shot = None

    def blitme(self):
        # draw Cannon on screen
        self.rect = self.image.get_rect()
        self.rect.center = self.coords
        self.screen.blit(self.image, self.rect)
