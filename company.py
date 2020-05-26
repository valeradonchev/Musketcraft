# import pygame
import math
from pygame.sprite import Group
from infantry import Infantry
from settings import I_SPEED, I_RANGE, I_MORALE, I_MORALE_MIN, I_SIGHT
from settings import I_PANIC_TIME, I_GAPY, I_PANIC_BAY
from flag import Flag
from pygame import time
import pygame
import random
import numpy as np
from button import Button

"click on any Infantry - bring up orders: bayonets, carre, etc."


class Company(Group):
    """Small unit of several Infantry controlled by Flag

    Parents
    -------
    pygame.sprite.Group

    Attributes
    ----------
    coords : float 1-D numpy.ndarray [2], >=0
        coords of center of Company
    speed : float, >=0
        absolute velocity of Company
    moving : bool
        whether Company is moving, including marching and forming up
    angle : float
        angle in radians of Company to x-axis.
    oldAngle : float
        angle in radians of Company to x-axis saved from last forming up
    flag : Flag
        sprite that user interacts with to give commands to Company
    target : Company or None
        enemy Company which this Company is aiming at
    maxSize : int, >= 0
        number of Infantry that Company starts with
    sizey : int, >= 0
        number of rows of infantry
    morale : int
        percent chance of Company entering panic on losing next Infantry
    panicTime : int, >= 0
        time in milliseconds when Company started panicking
    attackMove : bool
        whether Company prioritizes aiming at target over moving
    showOrders : int
        stage of selecting orders
    bayonetButton : Button
        button user presses to command Company to charge enemy with bayonets
    bayonets : bool
        whether Infantry will charge enemies with bayonets
    play : bool
        whether Company can be given orders by player

    Properties
    ----------
    size : int, >= 0
        number of Infantry currently contained in Company
    formed : int, >= 0
        count of Infantry in formation
    velocity : float 1-D numpy.ndarray [2]
        velocity of Company in vertical and horizontal axes
    allowShoot : bool
        whether Company will currently aim at targets
    range : int, >= 0
        distance in pixels which Companies will set enemies as target

    Methods
    -------
    setSpeed
        set speed to min of default, distance to coords
    distance
        measure straight line distance Company to coords
    stop
        stop Company, Infantry
    update
        move Company, update Infantry, panic if necessary
    follow
        move Company and Infantry to flag
    lookAt
        set rotation to angle from current center to new point
    aim
        select target, turn toward it
    getHit
        kill own Infantry when shot
    updateMorale
        update chance to flee
    orders
        give orders other than move for Company
    blitme
        print elements of Company
    __str__
        return string with name of file for id, used in testing
    """

    def __init__(self, screen, angle, x, y, sizex, sizey, file1, file2, file3,
                 fileFlag, flags, play=True):
        super().__init__()
        self.coords = np.array([x, y], dtype=float)
        self.speed = 0
        self.moving = False
        self.angle = angle
        self.oldAngle = self.angle
        # add infantry to company
        for i in range(sizex * sizey):
            self.add(Infantry(screen, angle, i, sizex, sizey, file1, file2, file3,
                              self.coords))
        self.flag = Flag(screen, x, y, fileFlag, play)
        flags.append(self.flag)
        self.target = None
        self.maxSize = sizex * sizey
        self.sizey = sizey
        self.morale = I_MORALE
        self.panicTime = 0
        # 0,1=click,release to show buttons, 2,3=click,release to select
        self.showOrders = 0
        self.bayonetButton = Button(screen, "Bayonets")
        self.bayonets = False
        self.play = play
        # used to id object for testing, not meant to be seen/used
        self.id = file1

    @property
    def size(self):
        # number of Infantry currently contained in Company
        return len(self.sprites())

    @property
    def formed(self):
        # count of Infantry in formation
        return sum([infantry.formed for infantry in self])

    @property
    def velocity(self):
        # vertical, horizontal velocity of Company
        velocityX = self.speed * math.cos(self.angle)
        velocityY = -self.speed * math.sin(self.angle)
        return np.array([velocityX, velocityY], dtype=float)

    @property
    def allowShoot(self):
        # whether Company will currently aim at targets
        return not self.moving or self.flag.attackMove

    @property
    def range(self):
        # distance in pixels which Companies will set enemies as target
        if self.bayonets:
            return I_SPEED
        return (I_RANGE - (self.sizey // 2 + 1) * I_GAPY)

    def setSpeed(self, coords):
        # set speed to min of default, distance to coords
        self.speed = min(I_SPEED, self.distance(coords))

    def distance(self, coords):
        # measure straight line distance Company to coords
        return np.linalg.norm(self.coords - coords)

    def stop(self, moving=False):
        # stop Company, Infantry
        self.speed = 0
        if self.moving or moving:
            [infantry.stop() for infantry in self]
        self.moving = False

    def update(self):
        # move Company, update Infantry, panic if necessary
        if self.panicTime != 0:
            [infantry.panic() for infantry in self]
            if time.get_ticks() - self.panicTime > I_PANIC_TIME:
                self.empty()
        else:
            self.coords += self.velocity
            [infantry.update(self.allowShoot, self.bayonets) for infantry in self]

    def follow(self, flags):
        # move Company and Infantry to flag
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
                if self.speed == I_SPEED:
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
                seen = self.distance(target.coords) <= I_SIGHT
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
        if toTarget > I_SIGHT or dead or not self.allowShoot:
            self.target = None
            self.stop(True)
            [infantry.aim(self.target, self.angle, self.allowShoot) for infantry in self]
        elif self.oldAngle != self.angle:
            if self.formed < self.size:
                [infantry.form(self.angle, self.oldAngle, self.coords) for infantry in self]
            else:
                self.oldAngle = self.angle
                self.stop(True)
        elif toTarget > self.range:
            self.flag.attackMove = True
            self.setSpeed(self.target.coords)
            [infantry.setSpeed(self.speed) for infantry in self]
        else:
            self.stop(True)
            [infantry.aim(self.target, self.angle, self.allowShoot) for infantry in self]

    def getHit(self, bayonet=False):
        # kill own Infantry when shot
        if self.size == 0:
            return
        self.remove(random.choice(self.sprites()))
        morale = self.morale * I_PANIC_BAY ** bayonet
        if random.randint(0, 99) < morale and self.panicTime == 0:
            [infantry.startPanic() for infantry in self]
            self.panicTime = time.get_ticks()

    def updateMorale(self, allies, enemies):
        # update chance to flee
        allySize = sum([company.size for company in allies
                        if self.distance(company.coords) < I_SIGHT])
        enemySize = sum([company.size for company in enemies
                         if self.distance(company.coords) < I_SIGHT])
        deathMorale = I_MORALE_MIN * (1 - (self.size - 1) / self.maxSize)
        if allySize > 0:
            self.morale = I_MORALE + deathMorale * enemySize / allySize

    def orders(self):
        # give orders other than move for Company
        if not self.play:
            return
        cover = [self.flag.rect, self.flag.moveButton.rect,
                 self.flag.attackButton.rect]
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        if (click and self.showOrders == 0 and
            any([infantry.rect.collidepoint(mouse) for infantry in self]) and
            all([not rect.collidepoint(mouse) for rect in cover])):
            self.showOrders = 1
        if self.showOrders == 1 and not click:
            self.showOrders = 2
            self.bayonetButton.draw(self.coords)
        if self.showOrders == 2 and click:
            self.showOrders = 3
            if self.bayonetButton.rect.collidepoint(mouse):
                self.bayonets = not self.bayonets
        if self.showOrders == 3 and not click:
            self.showOrders = 0

    def blitme(self):
        # print elements of Company
        [infantry.blitme() for infantry in self]
        if self.size > 0:
            self.flag.blitme()
        if self.showOrders > 1:
            self.bayonetButton.blitme()

    def __str__(self):
        return self.id
