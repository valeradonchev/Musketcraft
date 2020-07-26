import sys
import pygame
from settings import BG_COLOR
from company import Company
from squadron import Squadron
from battery import Battery
from settings import blueCannon, greenCannon, blueCav, greenCav, blueImages
import cProfile


def check_events(color, events, units, screen, flags, cprof):
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
                                         2, 2, color, flags, 500))
                if color == "green":
                    units.append(Company(screen, 0, *pygame.mouse.get_pos(),
                                         2, 2, color, flags, 500,
                                         False))
            if event.unicode == "x":
                if color == "blue":
                    units.append(Battery(screen, 0, *pygame.mouse.get_pos(),
                                         3, color, flags))
                if color == "green":
                    units.append(Battery(screen, 0, *pygame.mouse.get_pos(),
                                         3, color, flags, False))
            if event.unicode == "c":
                if color == "blue":
                    units.append(Squadron(screen, 0, *pygame.mouse.get_pos(),
                                          2, 3, color, flags))
                if color == "green":
                    units.append(Squadron(screen, 0, *pygame.mouse.get_pos(),
                                          2, 3, color, flags,
                                          False))
            if event.unicode == "f":
                units = []
                flags = []
            if event.unicode == "g":
                cprof.print_stats('cumtime')
    for event in events:
        units = event.check(units)
        if event.triggered:
            events.remove(event)
    return color, units


def update(screen, units, flags):
    """ run the methods of Companies

    Parameters
    ----------
    screen : pygame.Surface
        Surface on which sprites are drawn
    units : list of Company, Squadron, Battery
        all unit formations
    flags : Flag list
        all Flag objects

    Modifies
    --------
    screen
        clear screen to default color
    units
        update position, velocity, target, direction, alive units in formations
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
