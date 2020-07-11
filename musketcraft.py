import pygame
from settings import SCREEN
from game_functions import check_events, update
from company import Company
from battery import Battery
from squadron import Squadron
import pandas as pd
import math
import cProfile


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
    cprof = cProfile.Profile()
    cprof.enable()
    screen = SCREEN
    pygame.display.set_caption("Musketcraft")
    flags = []
    infantry = pd.read_csv('levels/BorodinoInfantry.csv')
    cannon = pd.read_csv('levels/BorodinoCannon.csv')
    units = []
    for row in cannon.itertuples(False):
        units.append(Battery(screen, row.angle, row.x, row.y, row.size,
                             row.team, flags, row.play, row.defend))
    for row in infantry.itertuples(False):
        units.append(Company(screen, row.angle, row.x, row.y, row.sizex,
                             row.sizey, row.team, flags, row.play, row.defend))
    events = []

    [company.unitInit(units) for company in units]
    color = "blue"
    # main loop
    while True:
        color, units = check_events(color, events, units, screen, flags, cprof)
        test = update(screen, units, flags)
        if(test == "restart"):
            break


while True:
    runGame()
