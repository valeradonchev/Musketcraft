import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCALE, C_SCALE, M_CENTER
from game_functions import check_events, update
from company import Company
from cannon import Cannon
from instruct import Menu
import math


def scaleImage(*paths, scale=1):
    """convert image file location list into scaled image list

    Resizes images by SCALE constant multiplier
    """
    images = []
    for path in paths:
        image = pygame.image.load(path)
        size = [int(i * SCALE * scale) for i in image.get_rect().size]
        images.append(pygame.transform.scale(image, size))
    return images


def runGame():
    """initialize game, loop through gameplay functins until quit

    Modifies
    --------
    screen
        create screen for sprites to be drawn on, add caption
    blueCompanies
        create list of Companies on blue team
    redCompanies
        create list of Companies on red team
    """
    # init game, screen, settings
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Musketcraft")

    blueImages = scaleImage('images/blue_infantry.png',
                            'images/blue_infantry_firing.png',
                            'images/blue_infantry_bayonet.png',
                            'images/blue_flag.png',)
    greenImages = scaleImage('images/green_infantry.png',
                             'images/green_infantry_firing.png',
                             'images/green_infantry_bayonet.png',
                             'images/green_flag.png',)
    cannonImages = scaleImage('images/green_cannon.png',
                              'images/green_cannon_firing.png', scale=C_SCALE)
    flags = []
    cannons = [Cannon(screen, math.pi * 5 / 6, *cannonImages, (800, 570)),
               Cannon(screen, math.pi * 5 / 6, *cannonImages, (820, 520)),
               Cannon(screen, math.pi * 5 / 6, *cannonImages, (840, 470)),
               Cannon(screen, math.pi, *cannonImages, (550, 415)),
               Cannon(screen, math.pi * 5 / 6, *cannonImages, (880, 240)),
               Cannon(screen, math.pi * 5 / 6, *cannonImages, (870, 280)),
               ]
    blueCo = [Company(screen, 0, 200, 100, 5, 3, *blueImages, flags),
              Company(screen, 0, 200, 700, 5, 3, *blueImages, flags),
              Company(screen, 0, 200, 400, 5, 3, *blueImages, flags),
              Company(screen, 0, 200, 550, 5, 3, *blueImages, flags),
              Company(screen, 0, 200, 250, 5, 3, *blueImages, flags),
              Company(screen, 0, 100, 100, 5, 3, *blueImages, flags),
              Company(screen, 0, 100, 700, 5, 3, *blueImages, flags),
              Company(screen, 0, 100, 400, 5, 3, *blueImages, flags),
              Company(screen, 0, 100, 550, 5, 3, *blueImages, flags),
              Company(screen, 0, 100, 250, 5, 3, *blueImages, flags),
              ]
    greenCo = [Company(screen, math.pi * 5 / 6, 1050, 50, 5, 3,
                       *greenImages, flags, False),
               Company(screen, math.pi * 5 / 6, 1010, 120, 5, 3,
                       *greenImages, flags, False),
               Company(screen, math.pi * 11 / 12, 950, 180, 5, 3,
                       *greenImages, flags, False),
               Company(screen, math.pi * 11 / 12, 920, 270, 5, 3,
                       *greenImages, flags, False),
               Company(screen, math.pi * 11 / 12, 970, 220, 5, 3,
                       *greenImages, flags, False),
               Company(screen, math.pi * 11 / 12, 900, 390, 5, 3,
                       *greenImages, flags, False),
               Company(screen, math.pi * 11 / 12, 870, 470, 5, 3,
                       *greenImages, flags, False),
               Company(screen, math.pi * 11 / 12, 880, 550, 5, 3,
                       *greenImages, flags, False),
               Company(screen, math.pi * 11 / 12, 840, 570, 5, 3,
                       *greenImages, flags, False),
               Company(screen, math.pi, 840, 700, 5, 3,
                       *greenImages, flags, False),
               Company(screen, math.pi, 840, 770, 5, 3,
                       *greenImages, flags, False),
               Company(screen, math.pi, 800, 140, 3, 2,
                       *greenImages, flags, False),
               Company(screen, math.pi, 820, 650, 3, 2,
                       *greenImages, flags, False),
               Company(screen, math.pi, 480, 440, 3, 2,
                       *greenImages, flags, False),
               Company(screen, math.pi, 550, 470, 3, 2,
                       *greenImages, flags, False),
               Company(screen, math.pi, 580, 420, 5, 3,
                       *greenImages, flags, False),
               Company(screen, math.pi, 620, 470, 5, 3,
                       *greenImages, flags, False),
               ]
    instruction = Menu("instruction", *M_CENTER, "Continue", screen)
    town = scaleImage('images/town.png')[0]
    # main loop
    while True:
        check_events()
        test = update(screen, instruction, blueCo, greenCo, cannons, flags, town)
        if(test == "restart"):
            break


while True:
    runGame()
