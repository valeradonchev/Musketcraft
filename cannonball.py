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

    def __init__(self, screen, angle, file, coords, team, units):
        super().__init__()
        self.screen = screen
        self.image = file
        self.angle = angle
        self.coords = coords
        self.velocity = np.array([CB_SPEED * math.cos(self.angle),
                                  -CB_SPEED * math.sin(self.angle)])
        self.rect = self.image.get_rect()
        self.rect.center = self.coords
        self.team = team
        self.units = units
        self.travelled = 0

    def update(self, cannon):
        for company in self.units:
            if any([self.rect.colliderect(unit.rect) for unit in company]):
                if self.team != company.team:
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
