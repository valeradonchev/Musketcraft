# import pygame
import math
from pygame.sprite import Group
from cannon import Cannon
from settings import C_SPEED, C_RANGE, C_MORALE, C_MORALE_MIN, C_SIGHT
from settings import C_PANIC_TIME, C_PANIC_BAY, C_FIRE_ANGLE, C_GAPY
from settings import CC_GAPX, CC_GAPY, C_MEN_PER, C_MIN_RANGE
from flag import Flag
from pygame import time
import pygame
import random
import numpy as np
from button import Button
from cannoneer import Cannoneer

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
                 fileFlag, fileBall, fileHuman, team, flags, play=True):
        super().__init__()
        self.coords = np.array([x, y], dtype=float)
        self.speed = 0
        self.moving = False
        self.angle = angle
        self.oldAngle = self.angle
        # add infantry to company
        self.cannons = []
        for i in range(sizex):
            """ x displacement from center of Battery based on count
            shiftx increases with count with a period of sizex, creating
            a row of soldiers with a length of sizex
            """
            shifty = C_GAPY * ((i % sizex) - sizex // 2)
            shiftx = 0
            self.cannons.append(Cannon(screen, angle, shiftx, shifty,
                                       file1, file2, fileBall, team,
                                       self.coords))
            for i in range(C_MEN_PER):
                print()
                shiftxCC = shiftx + CC_GAPX * (-1) ** i
                shiftyCC = shifty + CC_GAPY * (-1) ** (i // 2)
                self.add(Cannoneer(screen, angle, shiftxCC, shiftyCC,
                                   fileHuman, self.coords))
        self.flag = Flag(screen, x, y, fileFlag, play)
        flags.append(self.flag)
        self.target = None
        self.maxSize = sizex
        self.panicTime = 0
        # 0,1=click,release to show buttons, 2,3=click,release to select
        self.showOrders = 0
        # self.bayonetButton = Button(screen, "Bayonets")
        self.play = play
        self.team = team
        self.sizex = sizex
        # used to id object for testing, not meant to be seen/used
        self.id = file1

    def unitInit(self, units):
        self.units = units
        [cannon.unitInit(units) for cannon in self.cannons]

    @property
    def size(self):
        # number of Cannoneers currently contained in Battery
        return len(self)

    @property
    def cannonSize(self):
        # number of Cannoneers and Cannons in Battery
        return len(self) + len(self.cannons)

    @property
    def formed(self):
        # count of Cannons in formation
        cannonFormed = sum([cannon.formed for cannon in self.cannons])
        manFormed = sum([man.formed for man in self])
        return cannonFormed + manFormed

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

    @property
    def range(self):
        # distance in pixels which Companies will set enemies as target
        return (C_RANGE - (self.sizex // 2 + 1) * C_GAPY)

    @property
    def morale(self):
        # update chance to flee
        allySize = 0
        enemySize = 0
        for company in self.units:
            if self.distance(company.coords) < C_SIGHT:
                if company.team == self.team:
                    allySize += company.size
                else:
                    enemySize += company.size
        deathMorale = C_MORALE_MIN * (1 - (self.size - 1) / self.maxSize)
        if allySize > 0:
            return C_MORALE + deathMorale * enemySize / allySize

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
            [cannon.stop() for cannon in self.cannons]
            [man.stop() for man in self]
        self.moving = False

    def update(self):
        # move Battery, update Cannons, panic if necessary
        if self.panicTime != 0:
            [cannon.panic() for cannon in self.cannons]
            [man.panic() for man in self]
            if time.get_ticks() - self.panicTime > C_PANIC_TIME:
                self.empty()
                self.cannons = []
        else:
            self.coords += self.velocity
            i = math.ceil(self.size / C_MEN_PER)
            for cannon in self.cannons:
                cannon.update(i, self.allowShoot)
                i -= 1
            [man.update() for man in self]

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
            if self.formed < self.cannonSize:
                self.moving = True
                self.lookAt(flagCoords)
                [cannon.form(self.angle, self.oldAngle, self.coords)
                 for cannon in self.cannons]
                [man.form(self.angle, self.oldAngle, self.coords)
                 for man in self]
            else:
                self.setSpeed(flagCoords)
                if self.speed == C_SPEED:
                    self.lookAt(flagCoords)
                [cannon.setSpeed(self.speed) for cannon in self.cannons]
                [man.setSpeed(self.speed) for man in self]
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

    def findTarget(self):
        # select target
        for target in self.units:
            if (self.distance(target.coords) < C_MIN_RANGE and
                self.team != target.team):
                self.target = None
                [cannon.startPanic() for cannon in self.cannons]
                [man.startPanic() for man in self]
                self.panicTime = time.get_ticks()
                return
            if self.target is None:
                seen = self.distance(target.coords) <= C_SIGHT
                if (seen and target.size > 0 and self.allowShoot and
                    target.team != self.team):
                    self.target = target
                    if self.moving:
                        self.oldAngle = self.angle
                        self.stop()

    def aim(self):
        # select target, turn toward it
        if self.size == 0 or self.panicTime != 0:
            return
        self.findTarget()
        if self.target is None:
            return
        self.lookAt(self.target.coords)
        toTarget = self.distance(self.target.coords)
        dead = self.target.size == 0
        if toTarget > C_SIGHT or dead or not self.allowShoot:
            self.target = None
            self.stop(True)
            for cannon in self.cannons:
                cannon.aim(self.target, self.angle, self.allowShoot)
        elif abs(self.oldAngle - self.angle) > C_FIRE_ANGLE:
            if self.formed < self.cannonSize:
                for cannon in self.cannons:
                    cannon.form(self.angle, self.oldAngle, self.coords)
                for man in self:
                    man.form(self.angle, self.oldAngle, self.coords)
            else:
                self.oldAngle = self.angle
                self.stop(True)
        elif toTarget > self.range:
            self.flag.attackMove = True
            self.setSpeed(self.target.coords)
            for cannon in self.cannons:
                cannon.angle = self.angle
                cannon.setSpeed(self.speed)
            for man in self:
                man.angle = self.angle
                man.setSpeed(self.speed)
        else:
            self.stop(True)
            for cannon in self.cannons:
                cannon.aim(self.target, self.angle, self.allowShoot)

    def getHit(self, bayonet=False):
        # kill own Cannons when shot
        if self.size == 0:
            return
        self.remove(random.choice(self.sprites()))
        morale = self.morale * C_PANIC_BAY ** bayonet
        if random.randint(0, 99) < morale and self.panicTime == 0:
            [cannon.startPanic() for cannon in self.cannons]
            [man.startPanic() for man in self]
            self.panicTime = time.get_ticks()

    def getShelled(self, ball):
        # kill own Cannoneers from Cannon roundshot
        for unit in self:
            if unit.rect.colliderect(ball.rect):
                self.remove(unit)
        if random.randint(0, 99) < self.morale and self.panicTime == 0:
            [cannon.startPanic() for cannon in self]
            [man.startPanic() for man in self]
            self.panicTime = time.get_ticks()

    def orders(self):
        # give orders other than move for Battery
        if not self.play:
            return
        cover = [self.flag.rect, self.flag.moveButton.rect,
                 self.flag.attackButton.rect]
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        if (click and self.showOrders == 0 and
            any([cannon.rect.collidepoint(mouse) for cannon in self.cannons])
            and all([not rect.collidepoint(mouse) for rect in cover])):
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
        [man.blitme() for man in self]
        [cannon.blitme() for cannon in self.cannons]
        if self.size > 0:
            self.flag.blitme()
        # if self.showOrders > 1:
            # self.bayonetButton.blitme()

    def __str__(self):
        return self.id
