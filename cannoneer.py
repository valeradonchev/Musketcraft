from settings import I_SPEED, I_GAPX, I_GAPY
import pygame
import math
from pygame.sprite import Sprite
from pygame import time
import random
import numpy as np


class Cannoneer(Sprite):
    """Soldier manning Cannon in Battery

    Parents
    -------
    pygame.sprite.Sprite

    Attributes
    ----------
    screen : pygame.Surface
        Surface on which Infantry is drawn
    ready : str
        path to image of Infantry when not shooting
    firing : str
        path to image of Infantry when shooting
    angle : float
        angle in radians of Infantry to x-axis
    rect : pygame.rect.Rect
        rectangle of Infantry Surface
    shiftr : float, > 0
        distance Infantry keeps from center of Company when in formation
    shiftt : float
        angle in radians to x-axis of line from Company center to Infantry
    center : float 1-D numpy.ndarray [2], >= 0
        coords of Infantry as float to avoid rounding errors
    velocity : float 1-D numpy.ndarray [2]
        velocity of Infantry in x, y directions
    formed : bool
        whether Infantry is in formation
    targetxy : float 1-D numpy.ndarray [2], >= 0
        coords where Infantry is moving to, target[0] = -1 when no target
    target : pygame.Group or None
        enemy which Infantry is aiming at
    aimedOn : int, > 0
        time in milliseconds when Infantry aimed, 0 = no time saved
    firedOn : int, > 0
        time in milliseconds when Infantry fired, 0 = no time saved
    panicAngle : float
        angle in radians in which Infantry moves when panicking

    Properties
    ----------
    orig : pygame.Surface
        original image of infantry from which rotations are derived
    relatCoords : float 1-D numpy.ndarray [2]
        coords of Infantry relative to Company center
    image : pygame.Surface
        image rotated to face current Infantry direction

    Methods
    -------
    form
        move Infantry into formation for moving to flag/firing
    setTarget
        set targetxy based on targeted coords, shift from center of Company
    move
        point at targetxy, move to targetxy
    distance
        measure straight line distance Infantry to coords, 0 if negative coords
    lookAt
        point at coordinates
    setSpeed
        set vertical, horizontal speed
    stop
        stop movement
    aim
        set target, point at target
    update
        move Infantry based on speed, fire at target if possible
    panic
        move Infantry in randomly determined direction while panicking
    startPanic
        set direction Infantry moves away in when panicking
    fire
        fire when target isn't None, reload after firing
    blitme
        draw Infantry on screen

    """

    def __init__(self, screen, angle, shiftx, shifty, file, coords):
        super().__init__()
        self.screen = screen
        self.ready = file
        self.costume = self.ready
        self.angle = angle
        self.rect = self.image.get_rect()
        self.shiftr = math.hypot(shiftx, shifty)
        self.shiftt = math.atan2(shifty, shiftx)
        self.rect.center = coords + self.relatCoords
        self.center = np.array(self.rect.center, dtype=float)
        self.velocity = np.array([0, 0], dtype=float)
        self.formed = False
        self.targetxy = np.array([-1, -1], dtype=float)
        self.panicAngle = 0

    @property
    def relatCoords(self):
        # coords of Infantry relative to Company center
        angle = self.shiftt - self.angle
        return np.array([self.shiftr * math.cos(angle),
                         self.shiftr * math.sin(angle)], dtype=float)

    @property
    def image(self):
        # image rotated to face current Infantry direction
        degrees = self.angle * 180 / math.pi
        return pygame.transform.rotate(self.costume, degrees)

    def form(self, angle, oldAngle, coords):
        # move Infantry into formation for moving to flag/firing
        if self.formed:
            return
        if self.targetxy[0] == -1:
            angleDiff = abs(oldAngle - angle)
            if 0.5 * math.pi < angleDiff < 1.5 * math.pi:
                self.shiftr *= -1
            self.angle = angle
            self.setTarget(coords)
        if self.distance(self.targetxy) > 0:
            self.move()
        else:
            self.stop()
            self.formed = True
            self.angle = angle

    def setTarget(self, coords):
        # set targetxy based on targetxy coords, shift from center of Company
        self.targetxy = coords + self.relatCoords

    def move(self):
        # point at targetxy, move to targetxy
        self.lookAt(self.targetxy)
        self.setSpeed(min(I_SPEED, self.distance(self.targetxy)))

    def distance(self, coords):
        # measure straight line distance Infantry to coords, 0 if no target
        if coords[0] == -1:
            return 0
        return np.linalg.norm(self.center - coords)

    def lookAt(self, target):
        # point at coordinates
        distance = target - self.center
        self.angle = math.atan2(-distance[1], distance[0])

    def setSpeed(self, speed):
        # set vertical, horizontal speed
        self.velocity = np.array([speed * math.cos(self.angle),
                                  -speed * math.sin(self.angle)])

    def stop(self):
        # stop movement
        self.setSpeed(0)
        self.formed = False
        self.targetxy = np.array([-1, -1])

    def update(self, allowShoot=False, bayonet=False):
        # move Infantry based on speed, fire at target if possible
        self.center += self.velocity

    def panic(self):
        # move Infantry in randomly determined direction while panicking
        self.angle = self.panicAngle
        self.setSpeed(I_SPEED)
        self.update()

    def startPanic(self):
        # set direction Infantry moves away in when panicking
        self.panicAngle = self.angle + math.pi * random.uniform(.75, 1.25)

    def blitme(self):
        # draw Infantry on screen
        self.rect = self.image.get_rect()
        self.rect.center = self.center
        self.screen.blit(self.image, self.rect)
        # return self.rect
