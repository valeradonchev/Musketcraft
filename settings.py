import math
"""Store constants for use in game, not altered by code/user
"""
# scale of game elements
SCALE = .3
# infantry settings
I_GAPY = 30 * SCALE  # vertical distance between centers of infantry
I_GAPX = 50 * SCALE  # horizontal distance between centers of infantry
I_SPEED = 1 * SCALE  # speed of infantry
I_AIM = 1000  # aim time of infantry in millisec
I_END_FIRE = 400  # time to end fire animation of infantry
I_LOAD = 1000  # reload time of infantry in millisec
I_RANGE = 350 * SCALE  # range of infantry
I_SIGHT = 400 * SCALE  # sight range of infantry
I_CHANCE = 1  # infantry's base percent chance to hit
I_DELAY = 100  # +/- range of random firing dealy
I_MORALE = -10  # base morale - percent chance to flee
I_MORALE_MIN = 25  # max percent chance to flee
I_PANIC_TIME = 1000  # Time to panic
I_PANIC_BAY = 1.5  # Factor of chance to panic from bayonets
I_BAY_CHANCE = 90  # Percent chance to hit with bayonet
I_FIRE_ANGLE = math.pi / 12
# Angle (in radians) within which infantry will fire
# cannon settings
C_GAPX = 250 * SCALE  # horizontal distance between centers of cannon
C_SPEED = .2 * SCALE  # speed of cannon
C_AIM = 2000  # aim time of cannon in millisec
C_END_FIRE = 800  # time to end fire animation of cannon
C_LOAD = 5000  # reload time of cannon in millisec
C_RANGE = 1400 * SCALE  # range of cannon
C_SIGHT = 750 * SCALE  # sight range of cannon
C_ACCURACY = math.pi / 6  # variation in radians of projectile trajectory
C_DELAY = 300  # +/- range of random firing dealy
C_MORALE = -10  # base morale - percent chance to flee
C_MORALE_MIN = 25  # max percent chance to flee
C_PANIC_TIME = 1000  # Time to panic
C_PANIC_BAY = 1.5  # Factor of chance to panic from bayonets
C_FIRE_ANGLE = math.pi / 12
# Angle (in radians) within which cannon will fire
# Cannonball settings
CB_SPEED = 5 * SCALE  # speed of Cannonball
# flag button settings
FB_SIZE = (120, 50)  # size of button
FB_COLOR = (150, 0, 0)  # color of button
FB_TXT_COLOR = (150, 150, 150)  # color of text
FB_TXT_SIZE = 48  # text size
# screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
BG_COLOR = (50, 110, 0)
FLECHE_COLOR = (165, 42, 42)
ROAD_COLOR = (130, 35, 35)
RIVER_COLOR = (50, 50, 250)
# Menu settings(TEMPORARY)
M_CENTER = (1060, 60)
