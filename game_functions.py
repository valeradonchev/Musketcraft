import sys
import pygame
from settings import BG_COLOR
from company import Company
from squadron import Squadron
from battery import Battery
from settings import blueCannon, greenCannon, blueCav, greenCav, blueImages
from settings import greenImages


def check_events(color, events, units, screen, flags):
    """ watch keyboard/mouse for events

    When close window button is pressed, exit the game. Other functionality
    may come later.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.unicode == "q":
                color = "blue"
            if event.unicode == "e":
                color = "green"
            if event.unicode == "z":
                if color == "blue":
                    units.append(Company(screen, 0, *pygame.mouse.get_pos(),
                                         3, 5, *blueImages, color, flags))
                if color == "green":
                    units.append(Company(screen, 0, *pygame.mouse.get_pos(),
                                         3, 5, *greenImages, color, flags,
                                         False))
            if event.unicode == "x":
                if color == "blue":
                    units.append(Battery(screen, 0, *pygame.mouse.get_pos(),
                                         3, *blueCannon, color, flags))
                if color == "green":
                    units.append(Battery(screen, 0, *pygame.mouse.get_pos(),
                                         3, *greenCannon, color, flags, False))
            if event.unicode == "c":
                if color == "blue":
                    units.append(Squadron(screen, 0, *pygame.mouse.get_pos(),
                                          2, 3, *blueCav, color, flags))
                if color == "green":
                    units.append(Squadron(screen, 0, *pygame.mouse.get_pos(),
                                          2, 3, *greenCav, color, flags,
                                          False))
            if event.unicode == "f":
                units = []
                flags = []
    for event in events:
        units = event.check(units)
    return color, units


def update(screen, units, flags):
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
    # remove dead units
    [units.remove(company) for company in units if company.size == 0]
    [company.unitInit(units) for company in units]
    # targeting
    [company.aim() for company in units]
    # process logic for moving
    [company.follow(flags) for company in units]
    # give orders
    [company.orders() for company in units]
    # move companies
    [company.update() for company in units]
    # update images
    [company.blitme() for company in units]
    # run AI
    [company.AIsupport() for company in units]
    [company.AIcarre() for company in units if hasattr(company, "AIcarre")]
    # draw screen
    pygame.display.flip()
