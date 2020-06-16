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
    units = []

    [company.unitInit(units) for company in units]
    color = "blue"
    # main loop
    while True:
        color, units = check_events(color, units, screen, flags)
        [company.unitInit(units) for company in units]
        test = update(screen, units, flags)
        if(test == "restart"):
            break


while True:
    runGame()
