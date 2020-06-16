from settings import C_SPEED, C_RANGE, C_AIM, C_LOAD
from settings import C_END_FIRE, C_DELAY, C_ACCURACY
import pygame
import math
from pygame.sprite import Sprite
from pygame import time
import random
import numpy as np
from cannonball import Cannonball


class Cannon(Sprite):
    """Cannon within a battery

    Parents
    -------
    pygame.sprite.Sprite

    Attributes
    ----------
    screen : pygame.Surface
        Surface on which Cannon is drawn
    ready : str
        path to image of Cannon when not shooting
    firing : str
        path to image of Cannon when shooting
    angle : float
        angle in radians of Cannon to x-axis
    rect : pygame.rect.Rect
        rectangle of Cannon Surface
    shiftr : float, > 0
        distance Cannon keeps from center of Battery when in formation
    shiftt : float
        angle in radians to x-axis of line from Battery center to Cannon
    center : float 1-D numpy.ndarray [2], >= 0
        coords of Cannon as float to avoid rounding errors
    velocity : float 1-D numpy.ndarray [2]
        velocity of Cannon in x, y directions
    formed : bool
        whether Cannon is in formation
    targetxy : float 1-D numpy.ndarray [2], >= 0
        coords where Cannon is moving to, target[0] = -1 when no target
    target : pygame.Group or None
        enemy which Cannon is aiming at
    aimedOn : int, > 0
        time in milliseconds when Cannon aimed, 0 = no time saved
    firedOn : int, > 0
        time in milliseconds when Cannon fired, 0 = no time saved
    panicAngle : float
        angle in radians in which Cannon moves when panicking

    Properties
    ----------
    orig : pygame.Surface
        original image of Cannon from which rotations are derived
    relatCoords : float 1-D numpy.ndarray [2]
        coords of Cannon relative to Battery center
    image : pygame.Surface
        image rotated to face current Cannon direction

    Methods
    -------
    form
        move Cannon into formation for moving to flag/firing
    setTarget
        set targetxy based on targeted coords, shift from center of Battery
    move
        point at targetxy, move to targetxy
    distance
        measure straight line distance Cannon to coords, 0 if negative coords
    lookAt
        point at coordinates
    setSpeed
        set vertical, horizontal speed
    stop
        stop movement
    aim
        set target, point at target
    update
        move Cannon based on speed, fire at target if possible
    panic
        move Cannon in randomly determined direction while panicking
    startPanic
        set direction Cannon moves away in when panicking
    fire
        fire when target isn't None, reload after firing
    blitme
        draw Cannon on screen

    """

    def __init__(self, screen, angle, shiftx, shifty, file1, file2,
                 file3, team, coords):
        super().__init__()
        self.screen = screen
        self.ready = file1
        self.firing = file2
        self.ball = file3
        self.costume = self.ready
        self.angle = angle
        self.rect = self.image.get_rect()
        self.shiftr = math.hypot(shiftx, shifty)
        self.shiftt = math.atan2(shifty, shiftx)
        self.rect.center = coords + self.relatCoords
        self.coords = np.array(self.rect.center, dtype=float)
        self.velocity = np.array([0, 0], dtype=float)
        self.formed = False
        self.targetxy = np.array([-1, -1], dtype=float)
        self.target = None
        self.aimedOn = 0
        self.firedOn = 0
        self.panicAngle = 0
        self.shot = None

    @property
    def relatCoords(self):
        # coords of Cannon relative to Battery center
        angle = self.shiftt - self.angle
        return np.array([self.shiftr * math.cos(angle),
                         self.shiftr * math.sin(angle)], dtype=float)

    @property
    def image(self):
        # image rotated to face current Cannon direction
        degrees = self.angle * 180 / math.pi
        return pygame.transform.rotate(self.costume, degrees)

    def form(self, angle, oldAngle, coords):
        # move Cannon into formation for moving to flag/firing
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
        # set targetxy based on targetxy coords, shift from center of Battery
        self.targetxy = coords + self.relatCoords

    def move(self):
        # point at targetxy, move to targetxy
        self.lookAt(self.targetxy)
        self.setSpeed(min(C_SPEED, self.distance(self.targetxy)))

    def distance(self, coords):
        # measure straight line distance Cannon to coords, 0 if no target
        if coords[0] == -1:
            return 0
        return np.linalg.norm(self.coords - coords)

    def lookAt(self, target):
        # point at coordinates
        distance = target - self.coords
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

    def aim(self, target, angle=0, allowShoot=False):
        # set target, point at target
        if target is None:
            self.target = None
            self.angle = angle
            return
        if self.target is None:
            if self.distance(target.coords) <= C_RANGE and target.size > 0:
                self.target = target
        if self.target is not None:
            self.lookAt(self.target.coords)
            toTarget = self.distance(self.target.coords)
            if toTarget > C_RANGE or not allowShoot:
                self.target = None
                self.angle = angle
            else:
                self.lookAt(self.target.coords)

    def update(self, enemies, i=0, allowShoot=False):
        # move Cannon based on speed, fire at target if possible
        self.coords += self.velocity
        if i > 0:
            self.fire(enemies, allowShoot)
        else:
            self.costume = self.ready
        if self.shot is not None:
            self.shot.update(self)

    def panic(self):
        # move Cannon in randomly determined direction while panicking
        self.aim(None)
        self.angle = self.panicAngle
        self.setSpeed(C_SPEED)
        self.update()

    def startPanic(self):
        # set direction Cannon moves away in when panicking
        self.aim(None)
        self.panicAngle = self.angle + math.pi * random.uniform(.75, 1.25)

    def fire(self, enemies, allowShoot=False):
        # fire when target isn't None, reload after firing
        if self.target is None or not allowShoot:
            self.aimedOn = 0
        if self.aimedOn == 0 and self.target is not None and self.firedOn == 0:
            self.aimedOn = time.get_ticks() + random.randint(-C_DELAY, C_DELAY)
        if self.aimedOn != 0 and time.get_ticks() - self.aimedOn > C_AIM:
            self.costume = self.firing
            self.firedOn = time.get_ticks()
            self.aimedOn = 0
            angle = self.angle + random.uniform(-C_ACCURACY, C_ACCURACY)
            self.shot = Cannonball(self.screen, angle, self.ball,
                                   np.copy(self.coords), enemies)
        if self.firedOn != 0 and time.get_ticks() - self.firedOn > C_END_FIRE:
            self.costume = self.ready
        if self.firedOn != 0 and time.get_ticks() - self.firedOn > C_LOAD:
            self.firedOn = 0

    def blitme(self):
        # draw Cannon on screen
        self.rect = self.image.get_rect()
        self.rect.center = self.coords
        self.screen.blit(self.image, self.rect)
        if self.shot is not None:
            self.shot.blitme()
