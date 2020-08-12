# import pygame
import math
from pygame.sprite import Group
from cannon import Cannon
from settings import C_SPEED, C_RANGE, C_MORALE, C_MORALE_MIN, C_SIGHT
from settings import C_PANIC_TIME, C_PANIC_BAY, C_FIRE_ANGLE, C_GAPY
from settings import CC_GAPX, CC_GAPY, C_MEN_PER, C_MIN_RANGE
from settings import blueCannon, greenCannon
from flag import Flag
from pygame import time
import pygame
import random
import numpy as np
from button import Button
from cannoneer import Cannoneer

"click on any Cannon - bring up orders: canister, round shot, etc."


class Battery():
    """Small unit of several Cannon and Cannoneer controlled by Flag

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
    cannons : list of Cannon
        list of sprites representing cannons in Battery
    troops : list of Cannoneer
        list of sprites representing men manning cannons
    flag : Flag
        sprite that user interacts with to give commands to Battery
    target : Battery or None
        enemy Battery which this Battery is aiming at
    maxSize : int, >= 0
        number of Cannon that Battery starts with
    sizex : int, >= 0
        number of rows in Battery
    panicTime : int, >= 0
        time in milliseconds when Battery started panicking
    attackMove : bool
        whether Battery prioritizes aiming at target over moving
    showOrders : int
        stage of selecting orders
    play : bool
        whether Battery can be given orders by player
    team : str
        team Battery is on for friend-foe detection
    defense : bool
        whether unit will ignore AI move orders
    allies : list of Battery, Company, Squadron
        list of all units with same team value
    enemies : list of Battery, Company, Squadron
        list of all units with different team value

    Properties
    ----------
    size : int, >= 0
        number of Cannoneers contained in Battery
    cannonSize : int, >= 0
        number of Cannons and Cannoneers contained in Battery
    formed : int, >= 0
        count of Cannon in formation
    idle : bool
        whether AI can move this Battery
    velocity : float 1-D numpy.ndarray [2]
        velocity of Battery in vertical and horizontal axes
    allowShoot : bool
        whether Battery will currently aim at targets
    range : int, >= 0
        distance in pixels which Batteries will set enemies as target
    aimVars : list of vars
        variables passed to Cannon, Cannoneers for aim funciton
    formVars :
        variables passed to Cannon, Cannoneers for form function
    morale : int
        percent chance of Battery entering panic on losing next Cannon

    Methods
    -------
    unitInit
        set allies and enemies
    setSpeed
        set speed to min of default, distance to coords
    distance
        measure straight line distance Battery to coords
    distanceMany
        measure straight line distance Battery to list of coords
    stop
        stop Battery, Cannon
    update
        move Battery, update Cannon, panic if necessary
    follow
        move Battery and Cannon to flag
    lookAt
        set rotation to angle from current center to new point
    findTarget
        select enemy as target
    aim
        turn toward selected target
    getHit
        kill own Cannoneer when shot
    getShelled
        kill own Cannoneer hit by Cannonball
    orders
        give orders other than move for Battery
    AIcommand
        orders Battery to move to coords
    AIsupport
        move to visible allies in combat
    blitme
        print elements of Battery
    __str__
        return string with name of file for id, used in testing
    """

    def __init__(self, screen, angle, x, y, sizey, team, flags, strength,
                 play=True, defense=False):
        super().__init__()
        if team == "green":
            file1, file2, fileFlag, fileBall = greenCannon
        elif team == "blue":
            file1, file2, fileFlag, fileBall = blueCannon
        coords = np.array([x, y], dtype=float)
        self.troops = []
        for i in range(sizey):
            """ x displacement from center of Battery based on count
            shiftx increases with count with a period of sizey, creating
            a row of soldiers with a length of sizey
            """
            shifty = C_GAPY * ((i % sizey) - sizey // 2)
            shiftx = 0
            self.troops.append(Cannon(screen, angle, shiftx, shifty, strength,
                                       file1, file2, fileBall, team,
                                       coords, defense))
        self.flag = Flag(screen, (x, y), angle, fileFlag, play)
        flags.append(self.flag)
        # 0,1=click,release to show buttons, 2,3=click,release to select
        self.showOrders = 0
        # self.bayonetButton = Button(screen, "Bayonets")
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
        # number of Cannons currently contained in Battery
        return len(self.troops)

    @property
    def flagVars(self):
        return (self.flag.coords, self.flag.select, self.flag.attackMove,
                self.flag.angle, self.flag.change)

    def update(self):
        # move Battery, update Cannons, panic if necessary
        [can.panic() for can in self.troops if can.panicTime != 0]
        for cannon in self.troops:
            if cannon.size <= 0:
                self.troops.remove(cannon)
            elif cannon.panicTime == 0:
                cannon.update()

    def follow(self, flags):
        # move Battery and Cannons to flag
        if self.play:
            self.flag.checkDrag(flags)
        [unit.follow(*self.flagVars) for unit in self.troops]
        self.flag.change = False

    def aim(self):
        # turn toward selected target
        [troop.aim() for troop in self.troops]

    def orders(self):
        # give orders other than move for Battery
        if not self.play:
            return
        cover = [self.flag.rect, self.flag.moveButton.rect,
                 self.flag.attackButton.rect]
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        if (click and self.showOrders == 0 and
            any([cannon.rect.collidepoint(mouse) for cannon in self.troops])
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

    def AIcommand(self, coords, attackMove=False):
        # orders Battery to move to coords
        self.flag.coords = coords
        self.flag.attackMove = attackMove

    def AIsupport(self):
        # move to visible allies in combat
        if self.play or self.size == 0:
            return
        trp = self.troops[0]
        allyDist = trp.distanceMany([grp.coords for grp in trp.allies])
        for ally, d in zip(trp.allies, allyDist):
            cannon = hasattr(ally, 'shot')
            canSee = d < C_SIGHT
            if trp.idle and ally.target is not None and canSee and not cannon:
                self.AIcommand(ally.target.coords, True)
                break

    def blitme(self):
        # print elements of Battery
        [cannon.blitme() for cannon in self.troops]
        if self.size > 0:
            self.flag.blitme()
        # if self.showOrders > 1:
            # self.bayonetButton.blitme()
        # [man.blitme() for man in self.troops]

    def __str__(self):
        return self.id
