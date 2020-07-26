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
    bayonets : bool
        whether Infantry will charge enemies with bayonets
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
    allowShoot : bool
        whether Company will currently aim at targets
    range : int, >= 0
        distance in pixels which Companies will set enemies as target
    aimVars : list of vars
        variables passed to Infantry for aim funciton
    formVars :
        variables passed to Infantry for form function
    morale : int
        percent chance of Company entering panic on losing next Infantry

    Methods
    -------
    unitInit
        set allies and enemies
    setSpeed
        set speed to min of default, distance to coords
    distance
        measure straight line distance Company to coords
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
            fil1, fil2, fileFlag = greenImages
        elif team == "blue":
            fil1, fil2, fileFlag = blueImages
        self.coords = np.array([x, y], dtype=float)
        self.speed = 0
        self.moving = False
        self.angle = angle
        self.oldAngle = self.angle
        self.troops = []
        self.maxSize = sizex * sizey
        self.sizex = sizex
        self.sizey = sizey
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
                                        self.coords))
        self.flag = Flag(screen, (x, y), fileFlag, play)
        flags.append(self.flag)
        self.target = None
        # 0,1=click,release to show buttons, 2,3=click,release to select
        self.showOrders = 0
        self.bayonetButton = Button(screen, "Bayonets")
        self.carreButton = Button(screen, "Carre")
        self.lineButton = Button(screen, "Line")
        self.bayonets = False
        self.play = play
        self.team = team
        self.formation = "Line"
        self.defense = defense
        # used to id object for testing, not meant to be seen/used
        self.id = fil1

    def unitInit(self, units):
        # set allies and enemies
        self.enemies = [grp for grp in units if grp.team != self.team]
        self.allies = [grp for grp in units if grp.team == self.team]
        [inf.unitInit(units) for inf in self.troops]

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
        # whether AI can move this Company
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
        if self.bayonets:
            return I_SPEED
        return (I_RANGE - (self.sizey // 2 + 1) * I_GAPY)

    @property
    def aimVars(self):
        # variables that are passed to Infantry for aim funciton
        if self.target is None:
            return self.target, self.angle, self.allowShoot
        else:
            return (self.target, self.angle, self.allowShoot,
                    self.distance(self.target.coords))

    @property
    def formVars(self):
        # variables that are passed to Infantry for form function
        return self.angle, self.oldAngle, self.coords

    # @property
    # def morale(self):
    #     # update chance to flee
    #     allyDist = self.distanceMany([grp.coords for grp in self.allies])
    #     allySize = sum([grp.size for grp, d in zip(self.allies, allyDist)
    #                     if d < I_SIGHT])
    #     enemyDist = self.distanceMany([grp.coords for grp in self.enemies])
    #     enemySize = sum([grp.size for grp, d in zip(self.enemies, enemyDist)
    #                      if d < I_SIGHT])
    #     deathMorale = I_MORALE_MIN * (1 - (self.size - 1) / self.maxSize)
    #     if allySize > 0:
    #         return I_MORALE + deathMorale * enemySize / allySize
    #     return 0

    def setSpeed(self, coords):
        # set speed to min of default, distance to coords
        self.speed = min(I_SPEED, self.distance(coords))
        if self.formation == "Carre":
            self.speed = 0
        [infantry.setSpeed(self.speed) for infantry in self.troops]

    def distance(self, coords):
        # measure straight line distance Company to coords
        return np.linalg.norm(self.coords - coords)

    def distanceMany(self, coords):
        # measure straight line distance Battery to list of coords
        if len(coords) == 0:
            return []
        return np.linalg.norm(self.coords[None, :] - np.array(coords), axis=1)

    def stop(self):
        # stop Company, Infantry
        self.speed = 0
        [infantry.stop() for infantry in self.troops]
        self.moving = False

    def update(self):
        # move Company, update Infantry, panic if necessary
        [inf.panic() for inf in self.troops if inf.panicTime != 0]
        self.coords += self.velocity
        for infantry in self.troops:
            if infantry.size <= 0:
                self.troops.remove(infantry)
            elif self.target is None and infantry.panicTime == 0:
                infantry.update(self.allowShoot, self.bayonets)
            else:
                infantry.update(self.allowShoot, self.bayonets,
                                self.distance(self.target.coords))

    def follow(self, flags):
        # move Company and Infantry to flag
        if self.play:
            self.flag.checkDrag(flags, self.coords)
        flagCoords = self.flag.coords
        flagPlaced = (self.flag.select == 0 and
                      self.distance(flagCoords) > I_SPEED)
        if flagPlaced and (self.target is None or not self.flag.attackMove):
            if self.formed < self.size:
                self.moving = True
                self.lookAt(flagCoords)
                [infantry.form(*self.formVars) for infantry in self.troops]
            else:
                self.oldAngle = self.angle
                self.setSpeed(flagCoords)
                self.lookAt(flagCoords)
                if abs(self.oldAngle - self.angle) > I_FIRE_ANGLE:
                    self.stop()
                else:
                    self.angle = self.oldAngle
        elif self.moving:
            self.oldAngle = self.angle
            self.stop()
        if self.flag.select > 0 and self.moving:
            self.lookAt(flagCoords)
            self.stop()

    def lookAt(self, coords):
        # set rotation to angle from current center to new point
        if self.formation == "Carre":
            return
        distance = coords - self.coords
        self.angle = (math.atan2(-1 * distance[1], distance[0]))

    def findTarget(self):
        # select target
        enemyDist = self.distanceMany([grp.coords for grp in self.enemies])
        for target, d in zip(self.enemies, enemyDist):
            if self.target is None:
                seen = d <= I_SIGHT
                if seen and target.size > 0 and self.allowShoot:
                    self.target = target
                    if self.moving:
                        self.oldAngle = self.angle
                        self.stop()

    def aim(self):
        # turn toward selected target
        self.findTarget()
        if self.target is None:
            return
        self.lookAt(self.target.coords)
        toTarget = self.distance(self.target.coords)
        dead = self.target.size == 0
        if toTarget > I_SIGHT or dead or not self.allowShoot:
            self.target = None
            self.stop()
            [infantry.aim(*self.aimVars) for infantry in self.troops]
        elif abs(self.oldAngle - self.angle) > I_FIRE_ANGLE:
            if self.formed < self.size:
                [infantry.form(*self.formVars) for infantry in self.troops]
            else:
                self.oldAngle = self.angle
                self.stop()
        elif toTarget > self.range:
            self.flag.attackMove = True
            self.setSpeed(self.target.coords)
            for infantry in self.troops:
                infantry.angle = self.angle
        else:
            self.stop()
            [infantry.aim(*self.aimVars) for infantry in self.troops]

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
        if not self.play:
            return
        if self.flag.select != 0 or pygame.mouse.get_pressed()[2]:
            self.showOrders = 0
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        touch = any([inf.rect.collidepoint(mouse) for inf in self.troops])
        buttonCoords = (self.coords[0], self.coords[1] + FB_SIZE[1])
        if click and self.showOrders == 0 and touch:
            self.showOrders = 1
        if self.showOrders == 1 and not click:
            self.showOrders = 2
            self.bayonetButton.draw(self.coords)
            if self.formation == "Line":
                self.carreButton.draw(buttonCoords)
                self.lineButton.draw((-100, -100))
            if self.formation == "Carre":
                self.lineButton.draw(buttonCoords)
                self.carreButton.draw((-100, -100))
        if self.showOrders == 2 and click:
            self.showOrders = 3
            if self.bayonetButton.rect.collidepoint(mouse):
                self.bayonets = not self.bayonets
            if self.carreButton.rect.collidepoint(mouse):
                self.formCarre()
            if self.lineButton.rect.collidepoint(mouse):
                self.formLine()
        if self.showOrders == 3 and not click:
            self.showOrders = 0

    def formCarre(self):
        # Company forms a carre
        self.formation = "Carre"
        [inf.formCarre(self.sizex, self.sizey) for inf in self.troops]

    def formLine(self):
        # Company forms a line
        self.formation = "Line"
        [inf.formLine() for inf in self.troops]

    def AIcommand(self, coords, attackMove=False):
        # orders company to move to coords
        self.flag.coords = coords
        self.flag.attackMove = attackMove

    def AIsupport(self):
        # move to visible allies in combat
        if self.play:
            return
        allyDist = self.distanceMany([grp.coords for grp in self.allies])
        for ally, d in zip(self.allies, allyDist):
            canSee = d < I_SIGHT
            if self.idle and ally.target is not None and canSee:
                self.AIcommand(ally.coords, True)

    def AIcarre(self):
        # form carre when idle and charged by cavalry
        if self.play or self.target is not None:
            return
        for enmy in self.enemies:
            if hasattr(enmy, "chargeStart") and enmy.target == self:
                self.formCarre()
                return
        self.formLine()

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
