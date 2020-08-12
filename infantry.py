from settings import I_SPEED, I_RANGE, I_AIM, I_LOAD, I_CHANCE
from settings import I_END_FIRE, I_DELAY, I_BAY_CHANCE, I_SIGHT, I_MORALE
from settings import I_MORALE_MIN, I_PANIC_BAY, I_PANIC_TIME, I_FIRE_ANGLE
from settings import I_MED_SHELLED, I_AMP_SHELLED
import pygame
import math
from pygame.sprite import Sprite
from pygame import time
import random
import numpy as np
"set SPEED"
"add cavalry, blue cannons"
"events"

"AI retreat"
"troops can't move through each other"
"review numbers - smaller ranges, fire rate"
"show health?"
"terrain?"
"line vs. column formation"
"AI support target ally's target?"
"computer control"
"make ratios of units better"

"cavalry should be injured without charge"
"carre should take time to form"

"rework formation/idNum"
"sort out values in Settings"
"update documentation"
"slow rotation speed"
"Add multi control"
"util module for simple functions"
"add volley fire"
"smoke reduces accuracy? vision?"

"Carre - no move, effective vs. cavalry, weak vs. infantry"
"morale - true lifebar"
"bayonet - high chance of enemy routing, attacker high chance to die if not"


class Infantry(Sprite):
    """batallion of infantry

    Parents
    -------
    pygame.sprite.Sprite

    Attributes
    ----------
    screen : pygame.Surface
        Surface on which Infantry is drawn
    line : pygame.image
        image of Infantry when in line formation
    carre : pygame.image
        image of Infantry when in carre formation
    costume : pygame.image
        current image used by Infantry
    angle : float
        angle in radians of Infantry to x-axis
    oldAngle : float
        angle in radians of Infantry to x-axis saved from last move
    rect : pygame.rect.Rect
        rectangle of Infantry Surface
    shiftr : float, > 0
        distance Infantry keeps from center of Company when in formation
    shiftt : float
        angle in radians to x-axis of line from Company center to Infantry
    coords : float 1-D numpy.ndarray [2], >= 0
        coords of Infantry as float to avoid rounding errors
    velocity : float 1-D numpy.ndarray [2]
        velocity of Infantry in x, y directions
    moving : bool
        whether Infantry is moving
    attackMove : bool
        whether Infantry will stop to attack enemies
    bayonets : bool
        whether Infantry will charge enemies with bayonets
    targetxy : float 1-D numpy.ndarray [2], >= 0
        coords where Infantry is moving to, target[0] = -1 when no target
    target : pygame.Group or None
        enemy which Infantry is aiming at
    aimedOn : int, > 0
        time in milliseconds when Infantry aimed, 0 = no time saved
    firedOn : int, > 0
        time in milliseconds when Infantry fired, 0 = no time saved
    panicAngle : float
        angle in radians in which Infantry moves when panicking
    panicTime : int, >= 0
        time in milliseconds when Infantry started panicking
    formation : str
        current formation of Infantry/Company
    idNum : int, >= 0
        ordinal number of Infantry, used to find position in Company
    ComSize : int, > 0
        max number of Infantry in Company
    maxSize : int, >= 0
        starting number of troops in Infantry
    size : int, >= 0
        number of troops in Infantry - attack, health
    team : str
        team Infantry is on for friend-foe detection
    allies : list of Cannon, Infantry, Cavalry
        list of all units with same team value, including self
    enemies : list of Cannon, Infantry, Cavalry
        list of all units with different team value
    play : bool
        whether Infantry can be given orders by player
    defense : bool
        whether unit will ignore AI move orders

    Properties
    ----------
    relatCoords : float 1-D numpy.ndarray [2]
        coords of Infantry relative to Company center
    image : pygame.Surface
        image rotated to face current Infantry direction
    allowShoot : bool
        whether Infantry will currently aim at targets
    morale : int
        percent chance of Infantry entering panic on losing next unit

    Methods
    -------
    unitInit
        set allies and enemies
    distanceMany
        measure straight line distance from Infantry to list of coords
    formCarre
        move Infantry into carre formation
    formLine
        move Infantry into line formation
    form
        move Infantry into formation for moving to flag/firing
    setTarget
        set targetxy based on targeted coords, shift from center of Company
    move
        point at targetxy, move to targetxy
    distance
        measure straight line distance Infantry to coords, 0 if negative coords
    lookAt
        point at coordinates
    setSpeed
        set vertical, horizontal speed
    stop
        stop movement
    aim
        set target, point at target
    update
        move Infantry based on speed, fire at target if possible
    panic
        move Infantry in randomly determined direction while panicking
    startPanic
        set direction Infantry moves away in when panicking
    fire
        fire when target isn't None, reload after firing
    getHit
        reduce size by number of hits, check for panic
    blitme
        draw Infantry on screen

    """

    def __init__(self, screen, angle, shiftx, shifty, size,
                 team, file1, file2, file3, coords, play, defense):
        super().__init__()
        self.screen = screen
        self.line = file1
        self.firing = file2
        self.carre = file3
        self.costume = self.line
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
        self.bayonets = False
        self.targetxy = np.array([-1, -1], dtype=float)
        self.target = None
        self.aimedOn = 0
        self.firedOn = 0
        self.panicAngle = 0
        self.panicTime = 0
        self.formation = "Line"
        self.maxSize = size
        self.size = size
        self.team = team
        self.play = play
        self.defense = defense

    def unitInit(self, units):
        # set allies and enemies
        self.enemies = [unt for grp in units
                        for unt in grp.troops if grp.team != self.team]
        self.allies = [unt for grp in units
                       for unt in grp.troops if grp.team == self.team]

    @property
    def relatCoords(self):
        # coords of Infantry relative to Company center
        angle = self.shiftt - self.angle
        return np.array([self.shiftr * math.cos(angle),
                         self.shiftr * math.sin(angle)], dtype=float)

    @property
    def image(self):
        # image rotated to face current Infantry direction
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
                        if d < I_SIGHT])
        enemyDist = self.distanceMany([grp.coords for grp in self.enemies])
        enemySize = sum([grp.size for grp, d in zip(self.enemies, enemyDist)
                         if d < I_SIGHT])
        deathMorale = I_MORALE_MIN * (1 - (self.size - 1) / self.maxSize)
        if allySize > 0:
            return I_MORALE + deathMorale * enemySize / allySize
        return 0

    @property
    def range(self):
        # distance in pixels which Companies will set enemies as target
        if self.bayonets:
            return I_SPEED
        return I_RANGE

    @property
    def idle(self):
        # whether AI can move this Company
        return not self.defense and self.target is None and not self.moving

    def distanceMany(self, coords):
        # measure straight line distance Battery to list of coords
        if len(coords) == 0:
            return []
        return np.linalg.norm(self.coords[None, :] - np.array(coords), axis=1)

    def formCarre(self):
        # move Infantry into carre formation
        self.formation = "Carre"
        self.costume = self.carre

    def formLine(self):
        # move Infantry into line formation
        self.formation = "Line"
        self.costume = self.line

    def follow(self, fCoords, fSelect, attackMove, angle, change):
        # move Infantry to flag
        altFCoords = fCoords + self.relatCoords
        if not self.moving:
            flagPlaced = (fSelect == 0 and self.distance(altFCoords) > I_SPEED)
        else:
            flagPlaced = (fSelect == 0 and self.distance(self.targetxy) > I_SPEED)
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
            self.angle = angle
            self.oldAngle = self.angle
            self.stop()
        if fSelect > 0 and self.moving:
            self.lookAt(fCoords)
            self.stop()

    def setTarget(self, coords):
        # set targetxy based on targetxy coords, shift from center of Company
        self.targetxy = coords + self.relatCoords

    def move(self):
        # point at targetxy, move to targetxy
        self.lookAt(self.targetxy)
        self.setSpeed(min(I_SPEED, self.distance(self.targetxy)))

    def distance(self, coords):
        # measure straight line distance Infantry to coords, 0 if no target
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
            seen = d <= I_SIGHT
            panic = target.panicTime != 0
            allow = seen and target.size > 0 and self.allowShoot and not panic
            closer = self.target is None
            closer = closer or d < self.distance(self.target.coords)
            if allow and closer:
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
        if toTarget > I_SIGHT or dead or not self.allowShoot:
            self.target = None
            self.stop()
        elif abs(self.oldAngle - self.angle) > I_FIRE_ANGLE:
            self.oldAngle = self.angle
            self.stop()
        elif toTarget > self.range:
            self.attackMove = True
            self.targetxy = self.target.coords
            self.move()
        else:
            self.stop()

    def update(self):
        # move Infantry based on speed, fire at target if possible
        self.coords += self.velocity
        self.fire()

    def panic(self):
        # move Infantry in randomly determined direction while panicking
        self.target = None
        self.angle = self.panicAngle
        self.setSpeed(I_SPEED)
        self.update()
        if time.get_ticks() - self.panicTime > I_PANIC_TIME:
            self.size = 0

    def startPanic(self):
        # set direction Infantry moves away in when panicking
        self.target = None
        self.panicAngle = self.angle + math.pi * random.uniform(.75, 1.25)
        self.panicTime = time.get_ticks()

    def fire(self):
        # fire when target isn't None, reload after firing
        outrange = self.target is None
        outrange = outrange or self.distance(self.target.coords) > self.range
        if not self.allowShoot or outrange:
            self.aimedOn = 0
        if self.aimedOn == 0 and self.target is not None and self.firedOn == 0:
            self.aimedOn = time.get_ticks() + random.randint(-I_DELAY, I_DELAY)
        if self.aimedOn != 0 and time.get_ticks() - self.aimedOn > I_AIM:
            dist = self.distance(self.target.coords)
            if self.costume != self.carre:
                self.costume = self.firing
            self.firedOn = time.get_ticks()
            self.aimedOn = 0
            chance = I_CHANCE * I_RANGE / dist
            # * max(1, self.target.size // 3)
            if dist < I_SPEED:
                # self.costume = self.bayonet
                chance = I_BAY_CHANCE
            hits = np.random.binomial(self.size, min(chance / 100, 1))
            # if random.randint(0, 99) < chance:
            self.target.getHit(hits, self.bayonets)
        if self.firedOn != 0 and time.get_ticks() - self.firedOn > I_END_FIRE:
            if self.costume != self.carre:
                self.costume = self.line
        if self.firedOn != 0 and time.get_ticks() - self.firedOn > I_LOAD:
            self.firedOn = 0

    def getHit(self, hits, bayonet=False):
        # reduce size by number of hits
        self.size -= hits
        morale = self.morale * I_PANIC_BAY ** bayonet
        if random.randint(0, 99) < morale and self.panicTime == 0:
            self.startPanic()
        # print(self.size)

    def getShelled(self, hits, angle):
        # reduce size based on hits, angle
        angleDiff = abs(self.angle - angle)
        mult = (I_MED_SHELLED - math.cos(angleDiff * 2) * I_AMP_SHELLED) // 1
        self.getHit(hits * mult)

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
        # draw Infantry on screen
        self.rect = self.image.get_rect()
        self.rect.center = self.coords
        self.screen.blit(self.image, self.rect)
        pygame.draw.circle(self.screen, pygame.Color("red"), self.targetxy.astype(int), 1)
