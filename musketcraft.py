import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCALE
from game_functions import check_events, update
from company import Company
from battery import Battery
import math


def scaleImage(*paths, scale=1):
    """convert image file location list into scaled image list
rdddq
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
    flags = []
    units = [Company(screen, 0, 700, 100, 3, 5, *blueImages, "blue", flags),
             Company(screen, 0, 200, 700, 3, 5, *blueImages, "blue", flags),
             Battery(screen, 0, 900, 400, 3, *blueCannon, "blue", flags),
             Company(screen, math.pi, 1050, 100, 3, 5,
                     *greenImages, "green", flags, False),
             Company(screen, math.pi, 1010, 600, 3, 5,
                     *greenImages, "green", flags, False),
             ]

    [company.unitInit(units) for company in units]
    # main loop
    while True:
        check_events()
        test = update(screen, units, flags)
        if(test == "restart"):
            break


while True:
    runGame()
