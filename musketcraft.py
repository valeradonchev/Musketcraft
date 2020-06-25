import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, blueImages, greenImages
from settings import blueCannon, greenCannon, blueCav, greenCav
from game_functions import check_events, update
from company import Company
from battery import Battery
from squadron import Squadron
import math


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
    flags = []
    units = [
Battery(screen, math.pi * 5 / 6, 800, 570, 1, *greenCannon, "green", flags, False, True),
Battery(screen, math.pi * 5 / 6, 820, 520, 1, *greenCannon, "green", flags, False, True),
Battery(screen, math.pi * 5 / 6, 840, 470, 1, *greenCannon, "green", flags, False, True),
Battery(screen, math.pi, 550, 415, 1, *greenCannon, "green", flags, False, True),
Battery(screen, math.pi * 5 / 6, 880, 240, 1, *greenCannon, "green", flags, False, True),
Battery(screen, math.pi * 5 / 6, 870, 280, 1, *greenCannon, "green", flags, False, True),
Company(screen, 0, 200, 100, 3, 5, *blueImages, "blue", flags),
Company(screen, 0, 200, 700, 3, 5, *blueImages, "blue", flags),
Company(screen, 0, 200, 400, 3, 5, *blueImages, "blue", flags),
Company(screen, 0, 200, 550, 3, 5, *blueImages, "blue", flags),
Company(screen, 0, 200, 250, 3, 5, *blueImages, "blue", flags),
Company(screen, 0, 100, 100, 3, 5, *blueImages, "blue", flags),
Company(screen, 0, 100, 700, 3, 5, *blueImages, "blue", flags),
Company(screen, 0, 100, 400, 3, 5, *blueImages, "blue", flags),
Company(screen, 0, 100, 550, 3, 5, *blueImages, "blue", flags),
Company(screen, 0, 100, 250, 3, 5, *blueImages, "blue", flags),
Company(screen, math.pi * 5 / 6, 1050, 50, 3, 5, *greenImages, "green", flags, False),
Company(screen, math.pi * 5 / 6, 1010, 120, 3, 5, *greenImages, "green", flags, False),
Company(screen, math.pi * 11 / 12, 950, 180, 3, 5, *greenImages, "green", flags, False),
Company(screen, math.pi * 11 / 12, 920, 270, 3, 5, *greenImages, "green", flags, False),
Company(screen, math.pi * 11 / 12, 970, 220, 3, 5, *greenImages, "green", flags, False),
Company(screen, math.pi * 11 / 12, 900, 390, 3, 5, *greenImages, "green", flags, False),
Company(screen, math.pi * 11 / 12, 870, 470, 3, 5, *greenImages, "green", flags, False),
Company(screen, math.pi * 11 / 12, 880, 550, 3, 5, *greenImages, "green", flags, False),
Company(screen, math.pi * 11 / 12, 840, 570, 3, 5, *greenImages, "green", flags, False),
Company(screen, math.pi, 840, 700, 3, 5, *greenImages, "green", flags, False),
Company(screen, math.pi, 840, 770, 3, 5, *greenImages, "green", flags, False),
Company(screen, math.pi, 800, 140, 2, 3, *greenImages, "green", flags, False),
Company(screen, math.pi, 820, 650, 2, 3, *greenImages, "green", flags, False),
Company(screen, math.pi, 480, 440, 2, 3, *greenImages, "green", flags, False),
Company(screen, math.pi, 550, 470, 2, 3, *greenImages, "green", flags, False),
Company(screen, math.pi, 580, 420, 3, 5, *greenImages, "green", flags, False),
Company(screen, math.pi, 620, 470, 3, 5, *greenImages, "green", flags, False),
]
    events = []

    [company.unitInit(units) for company in units]
    color = "blue"
    # main loop
    while True:
        color, units = check_events(color, events, units, screen, flags)
        test = update(screen, units, flags)
        if(test == "restart"):
            break


while True:
    runGame()

