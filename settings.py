import math
"""Store constants for use in game, not altered by code/user
"""
# scale of game size
SCALE = .3
# infantry settings
# distance between centers of infantry
I_GAPY = 30 * SCALE
I_GAPX = 50 * SCALE
# speed of infantry
I_SPEED = 1 * SCALE
# aim time of infantry in millisec
I_AIM = 1000
# time to end fire animation of infantry
I_END_FIRE = 400
# reload time of infantry in millisec
I_LOAD = 1000
# range of infantry
I_RANGE = 350 * SCALE
# sight range of infantry
I_SIGHT = 400 * SCALE
# infantry's base percent chance to hit
I_CHANCE = 1
# +/- range of random firing dealy
I_DELAY = 100
# base morale - percent chance to flee
I_MORALE = -10
# max percent chance to flee
I_MORALE_MIN = 25
# Time to panic
I_PANIC_TIME = 1000
# Factor of chance to panic from bayonets
I_PANIC_BAY = 1.5
# Percent chance to hit with bayonet
I_BAY_CHANCE = 90
# Angle (in radians) within which infantry will fire
I_FIRE_ANGLE = math.pi / 12
# flag button settings
# size of button
FB_SIZE = (120, 50)
# color of button
FB_COLOR = (150, 0, 0)
# color of text
FB_TXT_COLOR = (150, 150, 150)
# text size
FB_TXT_SIZE = 48
# screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
BG_COLOR = (50, 110, 0)
FLECHE_COLOR = (165, 42, 42)
ROAD_COLOR = (130, 35, 35)
RIVER_COLOR = (50, 50, 250)
# Cannon settings(TEMPORARY)
C_SCALE = .4
C_AIM = 2000
C_LOAD = 3000
C_DELAY = 300
C_END_FIRE = 800
# Menu settings(TEMPORARY)
M_CENTER = (1060, 60)
