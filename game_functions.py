import sys
import pygame
from settings import BG_COLOR


def check_events():
    """ watch keyboard/mouse for events

    When close window button is pressed, exit the game. Other functionality
    may come later.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()


def update(screen, blueInfantry, greenInfantry, flags):
    """ run the methods of Companies

    Parameters
    ----------
    screen : pygame.Surface
        Surface on which sprites are drawn
    scene : str
        part of game to be displayed
    blueInfantry : Company list
        all Companies on blue team
    redInfantry : Company list
        all Companies on red team
    flags : Flag list
        all Flag objects

    Modifies
    --------
    screen
        clear screen to default color
    blueInfantry
        update position, velocity, target, direction, alive Infantry of Company
    redInfantry
        update position, velocity, target, direction, alive Infantry of Company
    """
    # redraw screen
    screen.fill(BG_COLOR)
    # updating morale
    [unit.updateMorale(blueInfantry, greenInfantry) for unit in blueInfantry]
    [unit.updateMorale(greenInfantry, blueInfantry) for unit in greenInfantry]
    # targeting
    [company.aim(greenInfantry) for company in blueInfantry]
    [company.aim(blueInfantry) for company in greenInfantry]
    # process logic for moving
    [company.follow(flags) for company in blueInfantry]
    [company.follow(flags) for company in greenInfantry]
    # give orders
    [company.orders() for company in blueInfantry]
    [company.orders() for company in greenInfantry]
    # move companies
    [company.update() for company in blueInfantry]
    [company.update() for company in greenInfantry]
    # update images
    [company.blitme() for company in blueInfantry]
    [company.blitme() for company in greenInfantry]
    # draw screen
    pygame.display.flip()
