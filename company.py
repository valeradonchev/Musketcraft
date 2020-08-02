# import pygame
import math
from infantry import Infantry
from settings import I_SPEED, I_RANGE, I_SIGHT, I_GAPY, FB_SIZE, I_GAPX
from settings import I_FIRE_ANGLE
from settings import blueImages, greenImages
from flag import Flag
from pygame import time
import pygame
import random
import numpy as np
from button import Button

"click on any Infantry - bring up orders: bayonets, carre, etc."


class Company():
    """large unit of several batallions controlled by Flag

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
    troops : list of Infantry
        list of sprites representing troops in Company
    flag : Flag
        sprite that user interacts with to give commands to Company
    target : Company or None
        enemy Company which this Company is aiming at
    maxSize : int, >= 0
        number of Infantry that Company starts with
    sizex : int, >= 0
        number of troops in a row of Infantry
    sizey : int, >= 0
        number of rows of Infantry
    showOrders : int
        stage of selecting orders
    bayonetButton : Button
        button pressed to command Company to charge enemy with bayonets
    carreButton : Button
        button pressed to command Company to form carre
    lineButton : Button
        button pressed to command Company to form line
    play : bool
        whether Company can be given orders by player
    team : str
        team Company is on for friend-foe detection
    formation : String
        formation of Company
    defense : bool
        whether unit will ignore AI move orders
    allies : list of Battery, Company, Squadron
        list of all units with same team value
    enemies : list of Battery, Company, Squadron
        list of all units with different team value

    Properties
    ----------
    size : int, >= 0
        number of Infantry currently contained in Company
    formed : int, >= 0
        count of Infantry in formation
    idle : bool
        whether AI can move this Company
    velocity : float 1-D numpy.ndarray [2]
        velocity of Company in vertical and horizontal axes
    morale : int
        percent chance of Company entering panic on losing next Infantry

    Methods
    -------
    unitInit
        set allies and enemies
    setSpeed
        set speed to min of default, distance to coords
    distanceMany
        measure straight line distance Company to list of coords
    stop
        stop Company, Infantry
    update
        move Company, update Infantry, panic if necessary
    follow
        move Company and Infantry to flag
    lookAt
        set rotation to angle from current center to new point
    findTarget
        select enemy as target
    aim
        turn toward selected target
    getHit
        kill own Infantry when shot
    getShelled
        kill own Infantry hit by cannonball
    orders
        give orders other than move for Company
    formCarre
        Company forms a carre
    formLine
        Company forms a line
    AIcommand
        orders Company to move to coords
    AIsupport
        move to visible allies in combat
    AIcarre
        form carre when idle and charged by cavalry
    blitme
        print elements of Company
    __str__
        return string with name of file for id, used in testing
    """

    def __init__(self, screen, angle, x, y, sizex, sizey, team, flags,
                 strength, play=True, defense=False):
        super().__init__()
        if team == "green":
            fil1, fil2, fil3, fileFlag = greenImages
        elif team == "blue":
            fil1, fil2, fil3, fileFlag = blueImages
        coords = np.array([x, y], dtype=float)
        # self.moving = False
        self.troops = []
        self.maxSize = sizex * sizey
        # add infantry to company
        for i in range(sizex * sizey):
            """ x, y displacement from center of Company based on count
            shiftx increases with count with a period of sizex, creating
            a row of soldiers with a length of sizex
            shifty increases when count increases by sizex, starting
            a new row of soldiers every sizex soldiers
            """
            shifty = I_GAPY * ((i % sizey) - sizey // 2)
            shiftx = I_GAPX * ((i // sizey) - sizex // 2)
            self.troops.append(Infantry(screen, angle, i, self.maxSize, shiftx,
                                        shifty, strength, team, fil1, fil2,
                                        fil3, coords, play, defense))
        self.flag = Flag(screen, (x, y), angle, fileFlag, play)
        flags.append(self.flag)
        # self.target = None
        # 0,1=click,release to show buttons, 2,3=click,release to select
        self.showOrders = 0
        self.bayonetButton = Button(screen, "Bayonets")
        self.carreButton = Button(screen, "Carre")
        self.lineButton = Button(screen, "Line")
        self.play = play
        self.team = team
        self.formation = "Line"
        # self.defense = defense
        # used to id object for testing, not meant to be seen/used
        self.id = fil1

    def unitInit(self, units):
        # set allies and enemies
        # self.enemies = [grp for grp in units if grp.team != self.team]
        # self.allies = [grp for grp in units if grp.team == self.team]
        [inf.unitInit(units) for inf in self.troops]

    @property
    def size(self):
        # number of Infantry currently contained in Company
        return len(self.troops)

    # @property
    # def idle(self):
    #     # whether AI can move this Company
    #     return not self.defense and self.target is None and not self.moving

    @property
    def flagVars(self):
        return (self.flag.coords, self.flag.select, self.flag.attackMove,
                self.flag.angle, self.flag.change)

    def update(self):
        # move Company, update Infantry, panic if necessary
        [inf.panic() for inf in self.troops if inf.panicTime != 0]
        for infantry in self.troops:
            if infantry.size <= 0:
                self.troops.remove(infantry)
            elif infantry.panicTime == 0:
                infantry.update()

    def follow(self, flags):
        # move Company and Infantry to flag
        if self.play:
            self.flag.checkDrag(flags)
        [unit.follow(*self.flagVars) for unit in self.troops]
        self.flag.change = False

    def aim(self):
        # turn toward selected target
        [troop.aim() for troop in self.troops]

    def getHit(self, hits, bayonet=False):
        # kill own Infantry when shot
        target = random.choice(self.troops)
        target.getHit(hits, bayonet)

    # def getShelled(self, ball):
        # kill own Infantry from Cannon roundshot
        # for unit in self.troops:
        #     if unit.rect.colliderect(ball.rect):
        #         self.troops.remove(unit)
        # if random.randint(0, 99) < self.morale:
        #     [infantry.startPanic() for infantry in self.troops]

    def orders(self):
        # give orders other than move for Company
        if not self.play or self.size == 0:
            return
        if self.flag.select != 0 or pygame.mouse.get_pressed()[2]:
            self.showOrders = 0
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        touch = any([inf.rect.collidepoint(mouse) for inf in self.troops])
        coords = self.troops[0].coords
        buttonCoords = (coords[0], coords[1] + FB_SIZE[1])
        if click and self.showOrders == 0 and touch:
            self.showOrders = 1
        if self.showOrders == 1 and not click:
            self.showOrders = 2
            self.bayonetButton.draw(self.troops[0].coords)
            if self.formation == "Line":
                self.carreButton.draw(buttonCoords)
                self.lineButton.draw((-100, -100))
            if self.formation == "Carre":
                self.lineButton.draw(buttonCoords)
                self.carreButton.draw((-100, -100))
        if self.showOrders == 2 and click:
            self.showOrders = 3
            if self.bayonetButton.rect.collidepoint(mouse):
                for troop in self.troops:
                    troop.bayonets = not troop.bayonets
            if self.carreButton.rect.collidepoint(mouse):
                self.formCarre()
            if self.lineButton.rect.collidepoint(mouse):
                self.formLine()
        if self.showOrders == 3 and not click:
            self.showOrders = 0

    def formCarre(self):
        # Company forms a carre
        self.formation = "Carre"
        [inf.formCarre() for inf in self.troops]

    def formLine(self):
        # Company forms a line
        self.formation = "Line"
        [inf.formLine() for inf in self.troops]

    def AIcommand(self, coords, attackMove=False):
        # orders company to move to coords
        self.flag.coords = coords
        self.flag.attackMove = attackMove

    def AIsupport(self):
        "target ally's target?"
        # move to visible allies in combat
        if self.play or self.size == 0:
            return
        trp = self.troops[0]
        allyDist = trp.distanceMany([grp.coords for grp in trp.allies])
        for ally, d in zip(trp.allies, allyDist):
            canSee = d < I_SIGHT
            if self.troops[0].idle and ally.target is not None and canSee:
                self.AIcommand(ally.coords, True)

    def AIcarre(self):
        [troop.AIcarre() for troop in self.troops]

    def blitme(self):
        # print elements of Company
        if self.showOrders > 1:
            self.bayonetButton.blitme()
            self.carreButton.blitme()
            self.lineButton.blitme()
        [infantry.blitme() for infantry in self.troops]
        self.flag.blitme()

    def __str__(self):
        return self.id
