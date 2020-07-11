from settings import I_SPEED, I_RANGE, I_AIM, I_LOAD, I_CHANCE
from settings import I_END_FIRE, I_DELAY, I_BAY_CHANCE
import pygame
import math
from pygame.sprite import Sprite
from pygame import time
import random
import numpy as np
"test SummonEvent"
"computer control"
"retarget to closest"
"troops can't move through each other"

"cavalry should be injured without charge"
"carre should take time to form, ai not form if has target?"

"sort out values in Settings"
"update documentation"
"slow rotation speed"
"Add multi control"
"util module for simple functions"
"add volley fire"

"Carre - no move, effective vs. cavalry, weak vs. infantry"
"morale - true lifebar"
"bayonet - high chance of enemy routing, attacker high chance to die if not"


class Infantry(Sprite):
    """Foot soldier within a company

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

    def __init__(self, screen, angle, i, size, shiftx, shifty, file1, file2,
                 file3, coords):
        super().__init__()
        self.screen = screen
        self.ready = file1
        self.firing = file2
        self.bayonet = file3
        self.costume = self.ready
        self.angle = angle
        self.formationAngle = 0
        self.rect = self.image.get_rect()
        self.shiftr = math.hypot(shiftx, shifty)
        self.shiftt = math.atan2(shifty, shiftx)
        self.rect.center = coords + self.relatCoords
        self.center = np.array(self.rect.center, dtype=float)
        self.oldCenter = self.center
        self.oldCostume = self.costume
        self.velocity = np.array([0, 0], dtype=float)
        self.formed = False
        self.targetxy = np.array([-1, -1], dtype=float)
        self.target = None
        self.aimedOn = 0
        self.firedOn = 0
        self.panicAngle = 0
        self.formation = "Line"
        self.i = i
        self.size = size

    @property
    def relatCoords(self):
        # coords of Infantry relative to Company center
        angle = self.shiftt - self.angle
        return np.array([self.shiftr * math.cos(angle),
                         self.shiftr * math.sin(angle)], dtype=float)

    @property
    def image(self):
        # image rotated to face current Infantry direction
        degrees = (self.angle + self.formationAngle) * 180 / math.pi
        return pygame.transform.rotate(self.costume, degrees)

    def formCarre(self, sizex, sizey):
        if self.i // sizey == sizex - 1:
            self.formation = "Carre"
        if self.i // sizey == 0:
            self.formationAngle = math.pi
            self.formation = "Carre"
        if self.i % sizey == 0:
            self.formationAngle = math.pi / 2
            self.formation = "Carre"
        if self.i % sizey == sizey - 1:
            self.formationAngle = 3 * math.pi / 2
            self.formation = "Carre"

    def formLine(self):
        self.formationAngle = 0
        self.formation = "Line"

    def form(self, angle, oldAngle, coords):
        # move Infantry into formation for moving to flag/firing
        if self.formed:
            return
        if self.targetxy[0] == -1:
            angleDiff = abs(oldAngle - angle)
            if 0.5 * math.pi < angleDiff < 1.5 * math.pi:
                self.shiftr *= -1
                self.i = self.size - self.i - 1
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

    def aim(self, target, angle=0, allowShoot=False, dist=I_RANGE):
        # set target, point at target
        if target is None:
            self.target = None
            self.angle = angle
            return
        if self.target is None:
            self.target = target
        if self.target is not None:
            self.lookAt(self.target.coords)
            if (dist > I_RANGE or not allowShoot or
                (self.formation == "Carre" and dist > I_SPEED)):
                self.target = None
                self.angle = angle
            else:
                self.lookAt(self.target.coords)

    def update(self, allowShoot=False, bayonet=False, dist=I_RANGE):
        # move Infantry based on speed, fire at target if possible
        self.center += self.velocity
        self.fire(allowShoot, bayonet, dist)

    def panic(self):
        # move Infantry in randomly determined direction while panicking
        self.aim(None)
        self.angle = self.panicAngle
        self.setSpeed(I_SPEED)
        self.update()

    def startPanic(self):
        # set direction Infantry moves away in when panicking
        self.aim(None)
        self.panicAngle = self.angle + math.pi * random.uniform(.75, 1.25)

    def fire(self, allowShoot=False, bayonet=False, dist=I_RANGE):
        # fire when target isn't None, reload after firing
        if self.target is None or not allowShoot:
            self.aimedOn = 0
        if self.aimedOn == 0 and self.target is not None and self.firedOn == 0:
            self.aimedOn = time.get_ticks() + random.randint(-I_DELAY, I_DELAY)
        if self.aimedOn != 0 and time.get_ticks() - self.aimedOn > I_AIM:
            self.costume = self.firing
            # if bayonet:
            #     self.costume = self.bayonet
            self.firedOn = time.get_ticks()
            self.aimedOn = 0
            chance = I_CHANCE * I_RANGE / dist * max(1, self.target.size // 3)
            if dist < I_SPEED:
                self.costume = self.bayonet
                chance = I_BAY_CHANCE
            if random.randint(0, 99) < chance:
                self.target.getHit(bayonet)
        if self.firedOn != 0 and time.get_ticks() - self.firedOn > I_END_FIRE:
            self.costume = self.ready
        if self.firedOn != 0 and time.get_ticks() - self.firedOn > I_LOAD:
            self.firedOn = 0

    def blitme(self):
        # draw Infantry on screen
        self.rect = self.image.get_rect()
        self.rect.center = self.center
        self.screen.blit(self.image, self.rect)
        # return self.rect
