import math
import pygame
"""Store constants for use in game, not altered by code/user
"""
# scale of game elements
SCALE = .3
SPEED = 1
# infantry settings
I_GAPX = 70 * SCALE  # horizontal distance between centers of infantry
I_GAPY = 70 * SCALE  # vertical distance between centers of infantry
I_SPEED = 1 * SCALE * SPEED  # speed of infantry
I_AIM = 1000 // SPEED  # aim time of infantry in millisec
I_END_FIRE = 400 // SPEED  # time to end fire animation of infantry
I_LOAD = 1000 // SPEED  # reload time of infantry in millisec
I_RANGE = 450 * SCALE  # range of infantry
I_SIGHT = 600 * SCALE  # sight range of infantry
I_CHANCE = 1  # infantry's base percent chance to hit
I_DELAY = 100 // SPEED  # +/- range of random firing dealy
I_MORALE = -10  # base morale - percent chance to flee
I_MORALE_MIN = 25  # max percent chance to flee
I_PANIC_TIME = 1000 // SPEED  # Time to panic
I_PANIC_BAY = 1.5  # Factor of chance to panic from bayonets
I_BAY_CHANCE = 60  # Percent chance to hit with bayonet
I_FIRE_ANGLE = math.pi / 12
# Angle (in radians) within which infantry will fire
# cannon settings
C_GAPY = 250 * SCALE  # vertical distance between centers of cannon
C_SPEED = .2 * SCALE * SPEED  # speed of cannon
C_AIM = 2000 // SPEED  # aim time of cannon in millisec
C_END_FIRE = 800 // SPEED  # time to end fire animation of cannon
C_LOAD = 5000 // SPEED  # reload time of cannon in millisec
C_RANGE = 1500 * SCALE  # range of cannon (SHOULD BE 15000)
C_SIGHT = 1600 * SCALE  # sight range of cannon
C_MIN_RANGE = 100 * SCALE  # Cannoneers flee from enemies at this distance
C_ACCURACY = math.pi / 6  # variation in radians of projectile trajectory
C_DELAY = 300 // SPEED  # +/- range of random firing dealy
C_MORALE = -10  # base morale - percent chance to flee
C_MORALE_MIN = 25  # max percent chance to flee
C_PANIC_TIME = 1000 // SPEED  # Time to panic
C_PANIC_BAY = 1.5  # Factor of chance to panic from bayonets
C_FIRE_ANGLE = math.pi / 12
# Angle (in radians) within which cannon will fire
C_MEN_PER = 4  # number of Cannoneers needed to man each cannon
# Cannoneer settings
CC_GAPX = 100 * SCALE  # horizontal distance between Cannoneer and Cannon
CC_GAPY = 80 * SCALE  # vertical distance between Cannoneer and Cannon
# Cannonball settings
CB_SPEED = 5 * SCALE * SPEED  # speed of Cannonball
# cavalry settings
CV_GAPX = 150 * SCALE  # horizontal distance between centers of cavalry
CV_GAPY = 70 * SCALE  # vertical distance between centers of cavalry
CV_SPEED = 3 * SCALE * SPEED  # speed of cavalry
CV_ACCEL = .3 * SCALE * SPEED  # rate at which cavalry in a charge accelerates
CV_ANTI_CAV = 50  # percent chance of cavalry to die when they hit bayonets
CV_AIM = 100 // SPEED  # aim time of cavalry in millisec
CV_END_FIRE = 200 // SPEED  # time to end fire animation of cavalry
CV_LOAD = 1500 // SPEED  # reload time of cavalry in millisec
CV_RANGE = 650 * SCALE  # range within which cavalry won't charge
CV_SIGHT = 700 * SCALE  # sight range of cavalry
# CV_CHANCE = 1  # cavalry's base percent chance to hit
CV_DELAY = 50 // SPEED  # +/- range of random firing dealy
CV_MORALE = -40  # base morale - percent chance to flee
CV_MORALE_MIN = 25  # max percent chance to flee
CV_PANIC_TIME = 1000 // SPEED  # Time to panic
CV_PANIC_BAY = 1.5  # Factor of chance to panic from bayonets
CV_BAY_CHANCE = 90  # Percent chance to hit with bayonet
CV_FIRE_ANGLE = math.pi / 12
# Angle (in radians) within which cavalry will charge
# flag button settings
FB_SIZE = (120, 50)  # size of button
FB_COLOR = (150, 0, 0)  # color of button
FB_TXT_COLOR = (150, 150, 150)  # color of text
FB_TXT_SIZE = 48  # text size
# screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
BG_COLOR = (50, 110, 0)
FLECHE_COLOR = (165, 42, 42)
ROAD_COLOR = (130, 35, 35)
RIVER_COLOR = (50, 50, 250)
# Menu settings(TEMPORARY)
M_CENTER = (1060, 60)
# Images


def scaleImage(*paths, scale=1):
    """convert image file location list into scaled image list
rdddq
    Resizes images by SCALE constant multiplier
    """
    images = []
    for path in paths:
        image = pygame.image.load(path).convert_alpha()
        size = [int(i * SCALE * scale) for i in image.get_rect().size]
        images.append(pygame.transform.scale(image, size))
    return images


blueImages = scaleImage('images/blue_battalion.png',
                        'images/blue_battalion_fire.png',
                        'images/blue_square.png',
                        'images/blue_flag.png',)
greenImages = scaleImage('images/green_battalion.png',
                         'images/green_battalion_fire.png',
                         'images/green_square.png',
                         'images/green_flag.png',)
blueCannon = scaleImage('images/blue_cannon.png',
                        'images/blue_cannon_firing.png',
                        'images/blue_flag.png',
                        'images/cannonball.png',
                        'images/blue_human.png')
greenCannon = scaleImage('images/green_cannon.png',
                         'images/green_cannon_firing.png',
                         'images/green_flag.png',
                         'images/cannonball.png',
                         'images/green_human.png')
blueCav = scaleImage('images/blue_cavalry.png',
                     'images/blue_cavalry_slash.png',
                     'images/blue_flag.png',)
greenCav = scaleImage('images/green_cavalry.png',
                      'images/green_cavalry_slash.png',
                      'images/green_flag.png',)
