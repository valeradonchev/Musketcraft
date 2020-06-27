# import pygame
import math
from cavalry import Cavalry
from settings import CV_SPEED, CV_MORALE, CV_MORALE_MIN, CV_FIRE_ANGLE
from settings import CV_PANIC_TIME, CV_PANIC_BAY, CV_GAPX, CV_GAPY, CV_SIGHT
from settings import CV_ANTI_CAV, CV_ACCEL, CV_RANGE
from settings import blueCav, greenCav
from flag import Flag
from pygame import time
import pygame
import random
import numpy as np
from button import Button

"click on any Infantry - bring up orders: bayonets, carre, etc."


class Squadron():
    """Small unit of several Infantry controlled by Flag

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
        number of rows of Infantry
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

    def __init__(self, screen, angle, x, y, sizex, sizey, team, flags,
                 play=True, defense=False):
        super().__init__()
        if team == "green":
            file1, file2, fileFlag = greenCav
        elif team == "blue":
            file1, file2, fileFlag = blueCav
        self.coords = np.array([x, y], dtype=float)
        self.speed = 0
        self.moving = False
        self.angle = angle
        self.oldAngle = self.angle
        self.troops = []
        # add infantry to company
        for i in range(sizex * sizey):
            """ x, y displacement from center of Company based on count
            shiftx increases with count with a period of sizex, creating
            a row of soldiers with a length of sizex
            shifty increases when count increases by sizex, starting
            a new row of soldiers every sizex soldiers
            """
            shifty = CV_GAPY * ((i % sizey) - sizey // 2)
            shiftx = CV_GAPX * ((i // sizey) - sizex // 2)
            self.troops.append(Cavalry(screen, angle, shiftx, shifty, file1,
                                       file2, self.coords))
        self.flag = Flag(screen, (x, y), fileFlag, play)
        flags.append(self.flag)
        self.target = None
        self.maxSize = sizex * sizey
        self.sizey = sizey
        self.panicTime = 0
        # 0,1=click,release to show buttons, 2,3=click,release to select
        self.showOrders = 0
        # self.bayonetButton = Button(screen, "Bayonets")
        # self.bayonets = False
        self.play = play
        self.team = team
        # used to id object for testing, not meant to be seen/used
        self.id = file1
        self.chargeStart = 0
        self.defense = defense

    def unitInit(self, units):
        self.enemies = [grp for grp in units if grp.team != self.team]
        self.allies = [grp for grp in units if grp.team == self.team]

    @property
    def size(self):
        # number of Infantry currently contained in Company
        return len(self.troops)

    @property
    def formed(self):
        # count of Infantry in formation
        return sum([infantry.formed for infantry in self.troops])

    @property
    def idle(self):
        return not self.defense and self.target is None and not self.moving

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
        return CV_SPEED

    @property
    def aimVars(self):
        # variables that are passed to Cavalry for aim funciton
        return self.target, self.angle, self.allowShoot

    @property
    def formVars(self):
        # variables that are passed to Cavalry for form function
        return self.angle, self.oldAngle, self.coords

    @property
    def morale(self):
        # update chance to flee
        allySize = sum([grp.size for grp in self.allies
                        if self.distance(grp.coords) < CV_SIGHT])
        enemySize = sum([grp.size for grp in self.enemies
                         if self.distance(grp.coords) < CV_SIGHT])
        deathMorale = CV_MORALE_MIN * (1 - (self.size - 1) / self.maxSize)
        if allySize > 0:
            return CV_MORALE + deathMorale * enemySize / allySize
        return 0

    def setSpeed(self, coords):
        # set speed to min of default, distance to coords
        if self.chargeStart == 0:
            speed = CV_SPEED
        else:
            speed = (time.get_ticks() - self.chargeStart) // 100 * CV_ACCEL
        self.speed = min(speed, self.distance(coords))

    def distance(self, coords):
        # measure straight line distance Company to coords
        return np.linalg.norm(self.coords - coords)

    def stop(self):
        # stop Company, Infantry
        self.speed = 0
        [infantry.stop() for infantry in self.troops]
        self.moving = False

    def update(self):
        # move Company, update Infantry, panic if necessary
        if self.panicTime != 0:
            [infantry.panic() for infantry in self.troops]
            if time.get_ticks() - self.panicTime > CV_PANIC_TIME:
                self.troops = []
        else:
            self.coords += self.velocity
            [infantry.update(self.allowShoot) for infantry in self.troops]

    def follow(self, flags):
        # move Company and Infantry to flag
        if self.play and self.size > 0:
            self.flag.checkDrag(flags, self.coords)
        flagCoords = self.flag.coords
        flagPlaced = self.flag.select == 0 and self.distance(flagCoords) > 0
        if flagPlaced and (self.target is None or not self.flag.attackMove):
            self.chargeStart = 0
            if self.formed < self.size:
                self.moving = True
                self.lookAt(flagCoords)
                [infantry.form(*self.formVars) for infantry in self.troops]
            else:
                self.setSpeed(flagCoords)
                self.lookAt(flagCoords)
                [infantry.setSpeed(self.speed) for infantry in self.troops]
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
        for target in self.enemies:
            if self.target is None:
                seen = self.distance(target.coords) <= CV_SIGHT
                if seen and target.size > 0 and self.allowShoot:
                    self.target = target
                    if self.moving:
                        self.oldAngle = self.angle
                        self.stop()

    def aim(self):
        # select target, turn toward it
        if self.size == 0:
            return
        self.findTarget()
        if self.target is None:
            return
        self.lookAt(self.target.coords)
        toTarget = self.distance(self.target.coords)
        dead = self.target.size == 0
        if toTarget > CV_SIGHT or dead or not self.allowShoot:
            self.target = None
            self.stop()
            [cavalry.aim(*self.aimVars) for cavalry in self.troops]
        elif abs(self.oldAngle - self.angle) > CV_FIRE_ANGLE:
            if self.formed < self.size:
                [cavalry.form(*self.formVars) for cavalry in self.troops]
            else:
                self.oldAngle = self.angle
                self.stop()
        elif toTarget > self.range:
            if toTarget > CV_RANGE and self.chargeStart == 0:
                self.chargeStart = time.get_ticks()
            self.flag.attackMove = True
            self.setSpeed(self.target.coords)
            for cavalry in self.troops:
                cavalry.angle = self.angle
                cavalry.setSpeed(self.speed)
        else:
            if self.chargeStart != 0:
                self.hitBayonets()
                self.chargeStart = 0
            self.stop()
            [cavalry.aim(*self.aimVars) for cavalry in self.troops]

    def hitBayonets(self):
        # take losses from defended enemies
        angleDiff = (self.target.angle - self.angle) % (math.pi * 2)
        angleDiff = math.pi - angleDiff
        carre = hasattr(self.target, 'formation')
        carre = carre and self.target.formation == "Carre"
        if -CV_FIRE_ANGLE < angleDiff < CV_FIRE_ANGLE or carre:
            for cavalry in self.troops:
                if random.randint(0, 99) < CV_ANTI_CAV:
                    self.troops.remove(cavalry)

    def getHit(self, bayonet=False):
        # kill own Infantry when shot
        if self.size == 0:
            return
        self.troops.remove(random.choice(self.troops))
        morale = self.morale * CV_PANIC_BAY ** bayonet
        if random.randint(0, 99) < morale and self.panicTime == 0:
            [infantry.startPanic() for infantry in self.troops]
            self.panicTime = time.get_ticks()

    def getShelled(self, ball):
        # kill own Infantry from Cannon roundshot
        for unit in self.troops:
            if unit.rect.colliderect(ball.rect):
                self.troops.remove(unit)
        if random.randint(0, 99) < self.morale and self.panicTime == 0:
            [infantry.startPanic() for infantry in self.troops]
            self.panicTime = time.get_ticks()

    def orders(self):
        # give orders other than move for Company
        if not self.play:
            return
        cover = [self.flag.rect, self.flag.moveButton.rect,
                 self.flag.attackButton.rect]
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        if (click and self.showOrders == 0 and
            any([infantry.rect.collidepoint(mouse) for infantry in self.troops]) and
            all([not rect.collidepoint(mouse) for rect in cover])):
            self.showOrders = 1
        if self.showOrders == 1 and not click:
            self.showOrders = 2
            # self.bayonetButton.draw(self.coords)
        if self.showOrders == 2 and click:
            self.showOrders = 3
            # if self.bayonetButton.rect.collidepoint(mouse):
                # self.bayonets = not self.bayonets
        if self.showOrders == 3 and not click:
            self.showOrders = 0

    def AIcommand(self, coords, attackMove=False):
        self.flag.coords = coords
        self.flag.attackMove = attackMove

    def AIsupport(self):
        if self.play:
            return
        for ally in self.allies:
            canSee = self.distance(ally.coords) < CV_SIGHT
            if self.idle and ally.target is not None and canSee:
                self.AIcommand(ally.coords, True)

    def blitme(self):
        # print elements of Company
        [infantry.blitme() for infantry in self.troops]
        if self.size > 0:
            self.flag.blitme()
        # if self.showOrders > 1:
            # self.bayonetButton.blitme()

    def __str__(self):
        return self.id
