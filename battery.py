# import pygame
import math
from pygame.sprite import Group
from cannon import Cannon
from settings import C_SPEED, C_RANGE, C_MORALE, C_MORALE_MIN, C_SIGHT
from settings import C_PANIC_TIME, C_PANIC_BAY, C_FIRE_ANGLE
from flag import Flag
from pygame import time
import pygame
import random
import numpy as np
from button import Button

"click on any Cannon - bring up orders: canister, round shot, etc."


class Battery(Group):
    """Small unit of several Cannon controlled by Flag

    Parents
    -------
    pygame.sprite.Group

    Attributes
    ----------
    coords : float 1-D numpy.ndarray [2], >=0
        coords of center of Battery
    speed : float, >=0
        absolute velocity of Battery
    moving : bool
        whether Battery is moving, including marching and forming up
    angle : float
        angle in radians of Battery to x-axis.
    oldAngle : float
        angle in radians of Battery to x-axis saved from last forming up
    flag : Flag
        sprite that user interacts with to give commands to Battery
    target : Battery or None
        enemy Battery which this Battery is aiming at
    maxSize : int, >= 0
        number of Cannon that Battery starts with
    morale : int
        percent chance of Battery entering panic on losing next Cannon
    panicTime : int, >= 0
        time in milliseconds when Battery started panicking
    attackMove : bool
        whether Battery prioritizes aiming at target over moving
    showOrders : int
        stage of selecting orders
    play : bool
        whether Battery can be given orders by player

    Properties
    ----------
    size : int, >= 0
        number of Cannon currently contained in Battery
    formed : int, >= 0
        count of Cannon in formation
    velocity : float 1-D numpy.ndarray [2]
        velocity of Battery in vertical and horizontal axes
    allowShoot : bool
        whether Battery will currently aim at targets
    range : int, >= 0
        distance in pixels which Batteries will set enemies as target

    Methods
    -------
    setSpeed
        set speed to min of default, distance to coords
    distance
        measure straight line distance Battery to coords
    stop
        stop Battery, Cannon
    update
        move Battery, update Cannon, panic if necessary
    follow
        move Battery and Cannon to flag
    lookAt
        set rotation to angle from current center to new point
    aim
        select target, turn toward it
    getHit
        kill own Cannon when shot
    updateMorale
        update chance to flee
    orders
        give orders other than move for Battery
    blitme
        print elements of Battery
    __str__
        return string with name of file for id, used in testing
    """

    def __init__(self, screen, angle, x, y, sizex, file1, file2,
                 fileFlag, flags, play=True):
        super().__init__()
        self.coords = np.array([x, y], dtype=float)
        self.speed = 0
        self.moving = False
        self.angle = angle
        self.oldAngle = self.angle
        # add infantry to company
        for i in range(sizex):
            self.add(Cannon(screen, angle, i, sizex, file1, file2,
                              self.coords))
        self.flag = Flag(screen, x, y, fileFlag, play)
        flags.append(self.flag)
        self.target = None
        self.maxSize = sizex
        self.morale = C_MORALE
        self.panicTime = 0
        # 0,1=click,release to show buttons, 2,3=click,release to select
        self.showOrders = 0
        # self.bayonetButton = Button(screen, "Bayonets")
        self.play = play
        # used to id object for testing, not meant to be seen/used
        self.id = file1

    @property
    def size(self):
        # number of Cannons currently contained in Battery
        return len(self.sprites())

    @property
    def formed(self):
        # count of Cannons in formation
        return sum([infantry.formed for infantry in self])

    @property
    def velocity(self):
        # vertical, horizontal velocity of Battery
        velocityX = self.speed * math.cos(self.angle)
        velocityY = -self.speed * math.sin(self.angle)
        return np.array([velocityX, velocityY], dtype=float)

    @property
    def allowShoot(self):
        # whether Battery will currently aim at targets
        return not self.moving or self.flag.attackMove

    def setSpeed(self, coords):
        # set speed to min of default, distance to coords
        self.speed = min(C_SPEED, self.distance(coords))

    def distance(self, coords):
        # measure straight line distance Battery to coords
        return np.linalg.norm(self.coords - coords)

    def stop(self, moving=False):
        # stop Battery, Cannons
        self.speed = 0
        if self.moving or moving:
            [infantry.stop() for infantry in self]
        self.moving = False

    def update(self):
        # move Battery, update Cannons, panic if necessary
        if self.panicTime != 0:
            [infantry.panic() for infantry in self]
            if time.get_ticks() - self.panicTime > C_PANIC_TIME:
                self.empty()
        else:
            self.coords += self.velocity
            [cannon.update(self.allowShoot) for cannon in self]

    def follow(self, flags):
        # move Battery and Cannons to flag
        idle = all(flag.select == 0 for flag in flags)
        if self.play and self.size > 0 and (idle or self.flag.select > 0):
            self.flag.checkDrag()
        else:
            self.flag.select = 0
        flagCoords = self.flag.coords
        if (self.flag.select == 0 and self.distance(flagCoords) > 0 and
            (self.target is None or not self.flag.attackMove)):
            if self.formed < self.size:
                self.moving = True
                self.lookAt(flagCoords)
                [infantry.form(self.angle, self.oldAngle, self.coords)
                 for infantry in self]
            else:
                self.setSpeed(flagCoords)
                if self.speed == C_SPEED:
                    self.lookAt(flagCoords)
                [infantry.setSpeed(self.speed) for infantry in self]
        elif self.moving:
            self.oldAngle = self.angle
            self.stop()
        if self.flag.select > 0 and self.moving:
            self.lookAt(flagCoords)
            self.stop()

    def lookAt(self, coords):
        # set rotation to angle from current center to new point
        distance = coords - self.coords
        self.angle = (math.atan2(-1 * distance[1], distance[0]))

    def aim(self, group):
        # select target, turn toward it
        if self.size == 0:
            return
        for target in group:
            if self.target is None:
                seen = self.distance(target.coords) <= C_SIGHT
                if seen and target.size > 0 and self.allowShoot:
                    self.target = target
                    if self.moving:
                        self.oldAngle = self.angle
                        self.stop()
        if self.target is None:
            return
        # print(self.distance(self.target.coords))
        self.lookAt(self.target.coords)
        toTarget = self.distance(self.target.coords)
        dead = self.target.size == 0
        if toTarget > C_SIGHT or dead or not self.allowShoot:
            self.target = None
            self.stop(True)
            for infantry in self:
                infantry.aim(self.target, self.angle, self.allowShoot)
        elif (abs(self.oldAngle - self.angle) > C_FIRE_ANGLE or
              (toTarget > C_RANGE and self.oldAngle != self.angle)):
            if self.formed < self.size:
                for infantry in self:
                    infantry.form(self.angle, self.oldAngle, self.coords)
            else:
                self.oldAngle = self.angle
                self.stop(True)
        elif toTarget > C_RANGE:
            self.flag.attackMove = True
            self.setSpeed(self.target.coords)
            [infantry.setSpeed(self.speed) for infantry in self]
        else:
            self.stop(True)
            for infantry in self:
                infantry.aim(self.target, self.angle, self.allowShoot)

    def getHit(self, bayonet=False):
        # kill own Cannons when shot
        if self.size == 0:
            return
        self.remove(random.choice(self.sprites()))
        morale = self.morale * C_PANIC_BAY ** bayonet
        if random.randint(0, 99) < morale and self.panicTime == 0:
            [infantry.startPanic() for infantry in self]
            self.panicTime = time.get_ticks()

    def updateMorale(self, allies, enemies):
        # update chance to flee
        allySize = sum([company.size for company in allies
                        if self.distance(company.coords) < C_SIGHT])
        enemySize = sum([company.size for company in enemies
                         if self.distance(company.coords) < C_SIGHT])
        deathMorale = C_MORALE_MIN * (1 - (self.size - 1) / self.maxSize)
        if allySize > 0:
            self.morale = C_MORALE + deathMorale * enemySize / allySize

    def orders(self):
        # give orders other than move for Battery
        if not self.play:
            return
        cover = [self.flag.rect, self.flag.moveButton.rect,
                 self.flag.attackButton.rect]
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        if (click and self.showOrders == 0 and
            any([cannon.rect.collidepoint(mouse) for cannon in self]) and
            all([not rect.collidepoint(mouse) for rect in cover])):
            self.showOrders = 1
        if self.showOrders == 1 and not click:
            self.showOrders = 2
            # self.bayonetButton.draw(self.coords)
        if self.showOrders == 2 and click:
            self.showOrders = 3
            # if self.bayonetButton.rect.collidepoint(mouse):
            #     self.bayonets = not self.bayonets
        if self.showOrders == 3 and not click:
            self.showOrders = 0

    def blitme(self):
        # print elements of Battery
        [infantry.blitme() for infantry in self]
        if self.size > 0:
            self.flag.blitme()
        # if self.showOrders > 1:
            # self.bayonetButton.blitme()

    def __str__(self):
        return self.id
