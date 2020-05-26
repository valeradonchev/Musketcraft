from pygame.sprite import Sprite
from pygame import time
from settings import C_DELAY, C_LOAD, C_AIM, C_END_FIRE
import random
import math
import pygame
"VERY TEMPORARY - START OVER FOR FUNCTIONAL CLASS"


class Cannon(Sprite):
    def __init__(self, screen, angle, file1, file2, coords):
        super().__init__()
        self.screen = screen
        self.ready = file1
        self.firing = file2
        self.costume = self.ready
        self.angle = angle
        self.rect = self.image.get_rect()
        self.rect.center = coords
        self.aimedOn = 0
        self.firedOn = 0

    @property
    def image(self):
        # image rotated to face current Infantry direction
        degrees = self.angle * 180 / math.pi
        return pygame.transform.rotate(self.costume, degrees)

    def fire(self, allowShoot=False, bayonet=False):
        # fire when target isn't None, reload after firing
        if self.aimedOn == 0 and self.firedOn == 0:
            self.aimedOn = time.get_ticks() + random.randint(-C_DELAY, C_DELAY)
        if self.aimedOn != 0 and time.get_ticks() - self.aimedOn > C_AIM:
            self.costume = self.firing
            self.firedOn = time.get_ticks()
            self.aimedOn = 0
        if self.firedOn != 0 and time.get_ticks() - self.firedOn > C_END_FIRE:
            self.costume = self.ready
        if self.firedOn != 0 and time.get_ticks() - self.firedOn > C_LOAD:
            self.firedOn = 0

    def blitme(self):
        # draw Infantry on screen
        self.screen.blit(self.image, self.rect)
