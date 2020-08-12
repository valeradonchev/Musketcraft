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
                 strength, play=True, defense=False):
        super().__init__()
        if team == "green":
            file1, fileFlag = greenCav
        elif team == "blue":
            file1, fileFlag = blueCav
        coords = np.array([x, y], dtype=float)
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
            self.troops.append(Cavalry(screen, angle, shiftx, shifty, strength,
                                       team, file1, coords, play,
                                       defense))
        self.flag = Flag(screen, (x, y), angle, fileFlag, play)
        flags.append(self.flag)
        # 0,1=click,release to show buttons, 2,3=click,release to select
        self.showOrders = 0
        # self.bayonetButton = Button(screen, "Bayonets")
        # self.bayonets = False
        self.play = play
        self.team = team
        self.oldUnits = []
        # used to id object for testing, not meant to be seen/used
        self.id = file1

    def unitInit(self, units):
        # set allies and enemies
        if units != self.oldUnits:
            self.oldUnits = units
            [unit.unitInit(units) for unit in self.troops]

    @property
    def size(self):
        # number of Cavalry currently contained in Squadron
        return len(self.troops)

    @property
    def flagVars(self):
        return (self.flag.coords, self.flag.select, self.flag.attackMove,
                self.flag.angle, self.flag.change)

    def update(self):
        # move Squadron, update Cavalry, panic if necessary
        [unit.panic() for unit in self.troops if unit.panicTime != 0]
        for unit in self.troops:
            if unit.size <= 0:
                self.troops.remove(unit)
            elif unit.panicTime == 0:
                unit.update()

    def follow(self, flags):
        # move Squadron and Cavalry to flag
        if self.play:
            self.flag.checkDrag(flags)
        [unit.follow(*self.flagVars) for unit in self.troops]
        self.flag.change = False

    def aim(self):
        # turn toward selected target
        [troop.aim() for troop in self.troops]

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
        if self.play or self.size == 0:
            return
        unit = self.troops[0]
        allyDist = unit.distanceMany([grp.coords for grp in unit.allies])
        for ally, d in zip(unit.allies, allyDist):
            cannon = hasattr(ally, 'shot')
            canSee = d < CV_SIGHT
            if unit.idle and ally.target is not None and canSee and not cannon:
                self.AIcommand(ally.target.coords, True)
                break

    def blitme(self):
        # print elements of Squadron
        [unit.blitme() for unit in self.troops]
        if self.size > 0:
            self.flag.blitme()
        # if self.showOrders > 1:
            # self.bayonetButton.blitme()

    def __str__(self):
        return self.id
