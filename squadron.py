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


class Squadron():
    """Small unit of several Cavalry controlled by Flag

    Attributes
    ----------
    coords : float 1-D numpy.ndarray [2], >=0
        coords of center of Squadron
    speed : float, >=0
        absolute velocity of Squadron
    moving : bool
        whether Squadron is moving, including marching and forming up
    angle : float
        angle in radians of Squadron to x-axis.
    oldAngle : float
        angle in radians of Squadron to x-axis saved from last forming up
    troops : list of Cavalry
        list of sprites representing troops in Squadron
    flag : Flag
        sprite that user interacts with to give commands to Squadron
    target : Squadron or None
        enemy Squadron which this Squadron is aiming at
    maxSize : int, >= 0
        number of Cavalry that Squadron starts with
    sizey : int, >= 0
        number of rows of Cavalry
    panicTime : int, >= 0
        time in milliseconds when Squadron started panicking
    showOrders : int
        stage of selecting orders
    chargeStart : int
        when Squadron started charging at target
    play : bool
        whether Squadron can be given orders by player
    team : str
        team Squadron is on for friend-foe detection
    defense : bool
        whether unit will ignore AI move orders
    allies : list of Battery, Squadron, Squadron
        list of all units with same team value
    enemies : list of Battery, Squadron, Squadron
        list of all units with different team value

    Properties
    ----------
    size : int, >= 0
        number of Cavalry currently contained in Squadron
    formed : int, >= 0
        count of Cavalry in formation
    idle : bool
        whether AI can move this Squadron
    velocity : float 1-D numpy.ndarray [2]
        velocity of Squadron in vertical and horizontal axes
    allowShoot : bool
        whether Squadron will currently aim at targets
    range : int, >= 0
        distance in pixels which Squadrons will set enemies as target
    aimVars : list of vars
        variables passed to Cavalry for aim funciton
    formVars :
        variables passed to Cavalry for form function
    morale : int
        percent chance of Squadron entering panic on losing next Cavalry

    Methods
    -------
    unitInit
        set allies and enemies
    setSpeed
        set speed to min of default, distance to coords
    distance
        measure straight line distance Squadron to coords
    distanceMany
        measure straight line distance Squadron to list of coords
    stop
        stop Squadron, Cavalry
    update
        move Squadron, update Cavalry, panic if necessary
    follow
        move Squadron and Cavalry to flag
    lookAt
        set rotation to angle from current center to new point
    findTarget
        select enemy as target
    aim
        turn toward selected target
    hitBayonets
        take losses from defended enemies
    getHit
        kill own Cavalry when shot
    getShelled
        kill own Cavalry hit by cannonball
    orders
        give orders other than move for Squadron
    AIcommand
        orders company to move to coords
    AIsupport
        move to visible allies in combat
    blitme
        print elements of Squadron
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
        self.chargeStart = 0
        self.play = play
        self.defense = defense
        self.team = team
        # used to id object for testing, not meant to be seen/used
        self.id = file1

    def unitInit(self, units):
        # set allies and enemies
        self.enemies = [grp for grp in units if grp.team != self.team]
        self.allies = [grp for grp in units if grp.team == self.team]

    @property
    def size(self):
        # number of Cavalry currently contained in Squadron
        return len(self.troops)

    @property
    def formed(self):
        # count of Cavalry in formation
        return sum([infantry.formed for infantry in self.troops])

    @property
    def idle(self):
        # whether AI can move this Squadron
        return not self.defense and self.target is None and not self.moving

    @property
    def velocity(self):
        # vertical, horizontal velocity of Squadron
        velocityX = self.speed * math.cos(self.angle)
        velocityY = -self.speed * math.sin(self.angle)
        return np.array([velocityX, velocityY], dtype=float)

    @property
    def allowShoot(self):
        # whether Squadron will currently aim at targets
        return not self.moving or self.flag.attackMove

    @property
    def range(self):
        # distance in pixels which Squadron will set enemies as target
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

    def setSpeed(self, coords):
        # set speed to min of default, distance to coords
        if self.chargeStart == 0:
            speed = CV_SPEED
        else:
            speed = (time.get_ticks() - self.chargeStart) // 100 * CV_ACCEL
        self.speed = min(speed, self.distance(coords))

    def distance(self, coords):
        # measure straight line distance Squadron to coords
        return np.linalg.norm(self.coords - coords)

    def distanceMany(self, coords):
        # measure straight line distance Squadron to list of coords
        return np.linalg.norm(self.coords[None, :] - np.array(coords), axis=1)

    def stop(self):
        # stop Squadron, Cavalry
        self.speed = 0
        [infantry.stop() for infantry in self.troops]
        self.moving = False

    def update(self):
        # move Squadron, update Cavalry, panic if necessary
        if self.panicTime != 0:
            [infantry.panic() for infantry in self.troops]
            if time.get_ticks() - self.panicTime > CV_PANIC_TIME:
                self.troops = []
        else:
            self.coords += self.velocity
            [infantry.update(self.allowShoot) for infantry in self.troops]

    def follow(self, flags):
        # move Squadron and Cavalry to flag
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
        enemyDist = self.distanceMany([grp.coords for grp in self.enemies])
        for target, d in zip(self.enemies, enemyDist):
            if self.target is None:
                seen = d <= CV_SIGHT
                if seen and target.size > 0 and self.allowShoot:
                    self.target = target
                    if self.moving:
                        self.oldAngle = self.angle
                        self.stop()

    def aim(self):
        # turn toward selected target
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
        # kill own Cavalry when shot
        if self.size == 0:
            return
        self.troops.remove(random.choice(self.troops))
        morale = self.morale * CV_PANIC_BAY ** bayonet
        if random.randint(0, 99) < morale and self.panicTime == 0:
            [infantry.startPanic() for infantry in self.troops]
            self.panicTime = time.get_ticks()

    def getShelled(self, ball):
        # kill own Cavalry from Cannon roundshot
        for unit in self.troops:
            if unit.rect.colliderect(ball.rect):
                self.troops.remove(unit)
        if random.randint(0, 99) < self.morale and self.panicTime == 0:
            [infantry.startPanic() for infantry in self.troops]
            self.panicTime = time.get_ticks()

    def orders(self):
        # give orders other than move for Squadron
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
        # orders Squadron to move to coords
        self.flag.coords = coords
        self.flag.attackMove = attackMove

    def AIsupport(self):
        # move to visible allies in combat
        if self.play:
            return
        allyDist = self.distanceMany([grp.coords for grp in self.allies])
        for ally, d in zip(self.allies, allyDist):
            canSee = d < CV_SIGHT
            if self.idle and ally.target is not None and canSee:
                self.AIcommand(ally.coords, True)

    def blitme(self):
        # print elements of Squadron
        [infantry.blitme() for infantry in self.troops]
        if self.size > 0:
            self.flag.blitme()
        # if self.showOrders > 1:
            # self.bayonetButton.blitme()

    def __str__(self):
        return self.id
