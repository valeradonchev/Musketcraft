from settings import CV_SPEED, CV_AIM, CV_LOAD, CV_END_FIRE, CV_DELAY
from settings import CV_BAY_CHANCE, CV_RANGE, CV_SIGHT, CV_MORALE
from settings import CV_MORALE_MIN, CV_FIRE_ANGLE, CV_PANIC_TIME, CV_PANIC_BAY
from settings import CV_MED_SHELLED, CV_AMP_SHELLED, CV_ANTI_CAV, CV_ACCEL
import pygame
import math
from pygame.sprite import Sprite
from pygame import time
import random
import numpy as np


class Cavalry(Sprite):
    """Horse-mounted soldier within a Squadron

    Parents
    -------
    pygame.sprite.Sprite

    Attributes
    ----------
    screen : pygame.Surface
        Surface on which Cavalry is drawn
    ready : pygame.image
        image of Cavalry when not shooting
    slashing : pygame.image
        image of Cavalry when slashing
    costume : pygame.image
        current image used by Cavalry
    angle : float
        angle in radians of Cavalry to x-axis
    rect : pygame.rect.Rect
        rectangle of Cavalry Surface
    shiftr : float, > 0
        distance Cavalry keeps from center of Squadron when in formation
    shiftt : float
        angle in radians to x-axis of line from Squadron center to Cavalry
    center : float 1-D numpy.ndarray [2], >= 0
        coords of Cavalry as float to avoid rounding errors
    velocity : float 1-D numpy.ndarray [2]
        velocity of Cavalry in x, y directions
    formed : bool
        whether Cavalry is in formation
    targetxy : float 1-D numpy.ndarray [2], >= 0
        coords where Cavalry is moving to, target[0] = -1 when no target
    target : pygame.Group or None
        enemy which Cavalry is aiming at
    aimedOn : int, > 0
        time in milliseconds when Cavalry aimed, 0 = no time saved
    firedOn : int, > 0
        time in milliseconds when Cavalry fired, 0 = no time saved
    panicAngle : float
        angle in radians in which Cavalry moves when panicking

    Properties
    ----------
    relatCoords : float 1-D numpy.ndarray [2]
        coords of Cavalry relative to Squadron center
    image : pygame.Surface
        image rotated to face current Cavalry direction

    Methods
    -------
    form
        move Cavalry into formation for moving to flag/firing
    setTarget
        set targetxy based on targeted coords, shift from center of Squadron
    move
        point at targetxy, move to targetxy
    distance
        measure straight line distance Cavalry to coords, 0 if negative coords
    lookAt
        point at coordinates
    setSpeed
        set vertical, horizontal speed
    stop
        stop movement
    aim
        set target, point at target
    update
        move Cavalry based on speed, fire at target if possible
    panic
        move Cavalry in randomly determined direction while panicking
    startPanic
        set direction Cavalry moves away in when panicking
    fire
        fire when target isn't None, reload after firing
    blitme
        draw Cavalry on screen

    """

    def __init__(self, screen, angle, shiftx, shifty, size, team,
                 file1, coords, play, defense):
        super().__init__()
        self.screen = screen
        self.ready = file1
        # self.slashing = file2
        self.costume = self.ready
        self.angle = angle
        self.oldAngle = angle
        self.rect = self.image.get_rect()
        self.shiftr = math.hypot(shiftx, shifty)
        self.shiftt = math.atan2(shifty, shiftx)
        self.rect.center = coords + self.relatCoords
        self.coords = np.array(self.rect.center, dtype=float)
        self.velocity = np.array([0, 0], dtype=float)
        self.moving = False
        self.attackMove = True
        self.chargeStart = 0
        # self.formed = False
        self.targetxy = np.array([-1, -1], dtype=float)
        self.target = None
        self.aimedOn = 0
        self.firedOn = 0
        self.panicAngle = 0
        self.panicTime = 0
        self.maxSize = size
        self.size = size
        self.team = team
        self.play = play
        self.defense = defense

    def unitInit(self, units):
        # set allies and enemies
        self.enemies = [unt for grp in units
                        for unt in grp.troops if grp.team != self.team]
        self.allies = [unt for grp in units
                       for unt in grp.troops if grp.team == self.team]

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

    @property
    def allowShoot(self):
        # whether Company will currently aim at targets
        return not self.moving or self.attackMove

    @property
    def morale(self):
        # update chance to flee
        allyDist = self.distanceMany([grp.coords for grp in self.allies])
        allySize = sum([grp.size for grp, d in zip(self.allies, allyDist)
                        if d < CV_SIGHT])
        enemyDist = self.distanceMany([grp.coords for grp in self.enemies])
        enemySize = sum([grp.size for grp, d in zip(self.enemies, enemyDist)
                         if d < CV_SIGHT])
        deathMorale = CV_MORALE_MIN * (1 - (self.size - 1) / self.maxSize)
        if allySize > 0:
            return CV_MORALE + deathMorale * enemySize / allySize
        return 0

    @property
    def range(self):
        # distance in pixels which Companies will set enemies as target
        return CV_SPEED

    @property
    def idle(self):
        # whether AI can move this Company
        return not self.defense and self.target is None and not self.moving

    def distanceMany(self, coords):
        # measure straight line distance Battery to list of coords
        if len(coords) == 0:
            return []
        return np.linalg.norm(self.coords[None, :] - np.array(coords), axis=1)

    def follow(self, fCoords, fSelect, attackMove, angle, change):
        # move Infantry to flag
        altFCoords = fCoords + self.relatCoords
        if not self.moving:
            flagPlaced = (fSelect == 0 and self.distance(altFCoords) > CV_SPEED)
        else:
            flagPlaced = (fSelect == 0 and self.distance(self.targetxy) > CV_SPEED)
        if change:
            self.attackMove = attackMove
        if flagPlaced and (self.target is None or not self.attackMove):
            if not self.moving:
                self.moving = True
                self.angle = angle
                angleDiff = abs(self.oldAngle - self.angle)
                if 0.5 * math.pi < angleDiff < 1.5 * math.pi:
                    self.shiftr *= -1
                self.targetxy = fCoords + self.relatCoords
            self.move()
        elif self.moving:
            self.oldAngle = self.angle
            self.stop()
        if fSelect > 0 and self.moving:
            self.lookAt(fCoords)
            self.stop()

    def setTarget(self, coords):
        # set targetxy based on targetxy coords, shift from center of Company
        self.targetxy = coords + self.relatCoords

    def move(self):
        # point at targetxy, move to targetxy
        self.lookAt(self.targetxy)
        if self.chargeStart == 0:
            speed = CV_SPEED
        else:
            speed = (time.get_ticks() - self.chargeStart) // 100 * CV_ACCEL
        self.setSpeed(min(speed, self.distance(self.targetxy)))

    def distance(self, coords):
        # measure straight line distance Infantry to coords, 0 if no target
        if coords[0] == -1:
            return 0
        return np.linalg.norm(self.coords - coords)

    def lookAt(self, target):
        # point at coordinates
        distance = target - self.coords
        if distance[0] != 0 or distance[1] != 0:
            self.angle = math.atan2(-distance[1], distance[0])

    def setSpeed(self, speed):
        # set vertical, horizontal speed
        self.velocity = np.array([speed * math.cos(self.angle),
                                  -speed * math.sin(self.angle)])

    def stop(self):
        # stop movement
        self.setSpeed(0)
        self.moving = False
        self.attackMove = True
        self.targetxy = np.array([-1, -1])

    def findTarget(self):
        # select target
        if not self.allowShoot:
            self.target = None
            return
        enemyDist = self.distanceMany([grp.coords for grp in self.enemies])
        for target, d in zip(self.enemies, enemyDist):
            if self.target is None:
                seen = d <= CV_SIGHT
                panic = target.panicTime != 0
                if seen and target.size > 0 and self.allowShoot and not panic:
                    self.target = target
                    if self.moving:
                        self.oldAngle = self.angle
                        self.stop()
                    return

    def aim(self):
        # turn toward selected target
        self.findTarget()
        if self.target is None:
            return
        self.lookAt(self.target.coords)
        toTarget = self.distance(self.target.coords)
        dead = self.target.size == 0 or self.target not in self.enemies
        dead = dead or self.target.panicTime != 0
        if toTarget > CV_SIGHT or dead or not self.allowShoot:
            self.target = None
            self.stop()
        elif abs(self.oldAngle - self.angle) > CV_FIRE_ANGLE:
            self.oldAngle = self.angle
            self.stop()
        elif toTarget > self.range:
            if toTarget > CV_RANGE and self.chargeStart == 0:
                self.chargeStart = time.get_ticks()
            self.attackMove = True
            self.targetxy = self.target.coords
            self.move()
        else:
            if self.chargeStart != 0:
                self.hitBayonets()
                self.chargeStart = 0
            self.stop()

    def hitBayonets(self):
        # take losses from defended enemies
        angleDiff = (self.target.angle - self.angle) % (math.pi * 2)
        angleDiff = math.pi - angleDiff
        carre = hasattr(self.target, 'formation')
        carre = carre and self.target.formation == "Carre"
        if -CV_FIRE_ANGLE < angleDiff < CV_FIRE_ANGLE or carre:
            hits = np.random.binomial(self.size, CV_ANTI_CAV / 100)
            self.getHit(hits)

    def update(self):
        # move Infantry based on speed, fire at target if possible
        self.coords += self.velocity
        self.fire()

    def panic(self):
        # move Infantry in randomly determined direction while panicking
        self.target = None
        self.angle = self.panicAngle
        self.setSpeed(CV_SPEED)
        self.update()
        if time.get_ticks() - self.panicTime > CV_PANIC_TIME:
            self.size = 0

    def startPanic(self):
        # set direction Infantry moves away in when panicking
        self.target = None
        self.panicAngle = self.angle + math.pi * random.uniform(.75, 1.25)
        self.panicTime = time.get_ticks()

    def fire(self):
        # fire when target isn't None, reload after firing
        outrange = self.target is None
        outrange = outrange or self.distance(self.target.coords) > self.range
        if outrange or not self.allowShoot:
            self.aimedOn = 0
        if self.aimedOn == 0 and self.target is not None and self.firedOn == 0:
            self.aimedOn = time.get_ticks() + random.randint(-CV_DELAY, CV_DELAY)
        if self.aimedOn != 0 and time.get_ticks() - self.aimedOn > CV_AIM:
            # self.costume = self.slashing
            self.firedOn = time.get_ticks()
            self.aimedOn = 0
            chance = CV_BAY_CHANCE
            hits = np.random.binomial(self.size, min(chance / 100, 1))
            self.target.getHit(hits)
        if self.firedOn != 0 and time.get_ticks() - self.firedOn > CV_END_FIRE:
            self.costume = self.ready
        if self.firedOn != 0 and time.get_ticks() - self.firedOn > CV_LOAD:
            self.firedOn = 0

    def getHit(self, hits, bayonet=False):
        # reduce size by number of hits
        self.size -= hits
        morale = self.morale * CV_PANIC_BAY ** bayonet
        if random.randint(0, 99) < morale and self.panicTime == 0:
            self.startPanic()
        # print(self.size)

    def getShelled(self, hits, angle):
        # reduce size based on hits, angle
        angleDiff = abs(self.angle - angle)
        mult = (CV_MED_SHELLED - math.cos(angleDiff * 2) * CV_AMP_SHELLED) // 1
        self.getHit(hits * mult)

    def blitme(self):
        # draw Infantry on screen
        self.rect = self.image.get_rect()
        self.rect.center = self.coords
        self.screen.blit(self.image, self.rect)
