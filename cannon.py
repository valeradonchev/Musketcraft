from settings import C_SPEED, C_RANGE, C_AIM, C_LOAD, C_SIGHT, C_MORALE_MIN
from settings import C_END_FIRE, C_DELAY, C_ACCURACY, C_MORALE, C_FIRE_ANGLE
from settings import C_PANIC_TIME, C_MEN_PER, C_MED_SHELLED, C_AMP_SHELLED
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
    ready : pygame.image
        image of Cannon when not shooting
    firing : pygame.image
        image of Cannon when shooting
    ball : pygame.image
        image of Cannonball
    costume : pygame.image
        current image used by Cannon
    angle : float
        angle in radians of Cannon to x-axis
    rect : pygame.rect.Rect
        rectangle of Cannon Surface
    shiftr : float, > 0
        distance Cannon keeps from center of Battery when in formation
    shiftt : float
        angle in radians to x-axis of line from Battery center to Cannon
    coords : float 1-D numpy.ndarray [2], >= 0
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

    def __init__(self, screen, angle, shiftx, shifty, size, file1, file2,
                 file3, team, coords, defense):
        super().__init__()
        self.screen = screen
        self.ready = file1
        self.firing = file2
        self.ball = file3
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
        self.targetxy = np.array([-1, -1], dtype=float)
        self.target = None
        self.aimedOn = 0
        self.firedOn = 0
        self.panicAngle = 0
        self.panicTime = 0
        self.shot = None
        self.size = size * C_MEN_PER
        self.maxSize = self.size
        self.team = team
        self.defense = defense

    def unitInit(self, units):
        # set allies and enemies
        self.enemies = [unt for grp in units
                        for unt in grp.troops if grp.team != self.team]
        self.allies = [unt for grp in units
                       for unt in grp.troops if grp.team == self.team]

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

    @property
    def allowShoot(self):
        # whether Company will currently aim at targets
        return not self.moving or self.attackMove

    @property
    def morale(self):
        # update chance to flee
        allyDist = self.distanceMany([grp.coords for grp in self.allies])
        allySize = sum([grp.size for grp, d in zip(self.allies, allyDist)
                        if d < C_SIGHT])
        enemyDist = self.distanceMany([grp.coords for grp in self.enemies])
        enemySize = sum([grp.size for grp, d in zip(self.enemies, enemyDist)
                         if d < C_SIGHT])
        deathMorale = C_MORALE_MIN * (1 - (self.size - 1) / self.maxSize)
        if allySize > 0:
            return C_MORALE + deathMorale * enemySize / allySize
        return 0

    @property
    def range(self):
        # distance in pixels which Companies will set enemies as target
        return C_RANGE

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
            flagPlaced = (fSelect == 0 and self.distance(altFCoords) > C_SPEED)
        else:
            flagPlaced = (fSelect == 0 and self.distance(self.targetxy) > C_SPEED)
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
                seen = d <= C_SIGHT
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
        if toTarget > C_SIGHT or dead or not self.allowShoot:
            self.target = None
            self.stop()
        elif abs(self.oldAngle - self.angle) > C_FIRE_ANGLE:
            self.oldAngle = self.angle
            self.stop()
        elif toTarget > self.range:
            self.attackMove = True
            self.targetxy = self.target.coords
            self.move()
        else:
            self.stop()

    def update(self):
        # move Cannon based on speed, fire at target if possible
        self.coords += self.velocity
        self.fire()
        if self.shot is not None:
            self.shot.update(self)

    def panic(self):
        # move Cannon in randomly determined direction while panicking
        self.target = None
        self.angle = self.panicAngle
        self.setSpeed(C_SPEED)
        self.update()
        if time.get_ticks() - self.panicTime > C_PANIC_TIME:
            self.size = 0

    def startPanic(self):
        # set direction Cannon moves away in when panicking
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
            self.aimedOn = time.get_ticks() + random.randint(-C_DELAY, C_DELAY)
        if self.aimedOn != 0 and time.get_ticks() - self.aimedOn > C_AIM:
            self.costume = self.firing
            self.firedOn = time.get_ticks()
            self.aimedOn = 0
            angle = self.angle + random.uniform(-C_ACCURACY, C_ACCURACY)
            self.shot = Cannonball(self.screen, angle, self.ball,
                                   np.copy(self.coords), self.enemies,
                                   math.ceil(self.size / C_MEN_PER))
        if self.firedOn != 0 and time.get_ticks() - self.firedOn > C_END_FIRE:
            self.costume = self.ready
        if self.firedOn != 0 and time.get_ticks() - self.firedOn > C_LOAD:
            self.firedOn = 0

    def getHit(self, hits, bayonet=False):
        # reduce size by number of hits
        self.size -= hits
        morale = self.morale
        if (random.randint(0, 99) < morale or bayonet) and self.panicTime == 0:
            self.startPanic()

    def getShelled(self, hits, angle):
        # reduce size based on hits, angle
        angleDiff = abs(self.angle - angle)
        loss = (C_MED_SHELLED - math.cos(angleDiff * 2) * C_AMP_SHELLED) // 1
        self.getHit(loss, False)

    def blitme(self):
        # draw Cannon on screen
        self.rect = self.image.get_rect()
        self.rect.center = self.coords
        self.screen.blit(self.image, self.rect)
        if self.shot is not None:
            self.shot.blitme()
