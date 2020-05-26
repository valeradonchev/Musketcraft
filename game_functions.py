import sys
import pygame
import math
from settings import BG_COLOR, FLECHE_COLOR, RIVER_COLOR, ROAD_COLOR


def check_events():
    """ watch keyboard/mouse for events

    When close window button is pressed, exit the game. Other functionality
    may come later.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()


def update(screen, menu, blueInfantry, greenInfantry, cannons, flags, town):
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
    if menu.scene == "instruction":
        menu.blitme()
        menu.check()
    if menu.scene == "borodino":
        pygame.draw.arc(screen, FLECHE_COLOR, pygame.Rect(770, 550, 40, 30),
                        math.pi / 4, math.pi * 3 / 2, 5)
        pygame.draw.arc(screen, FLECHE_COLOR, pygame.Rect(790, 500, 40, 30),
                        math.pi / 4, math.pi * 3 / 2, 5)
        pygame.draw.arc(screen, FLECHE_COLOR, pygame.Rect(810, 450, 40, 30),
                        math.pi / 4, math.pi * 3 / 2, 5)
        pygame.draw.arc(screen, FLECHE_COLOR, pygame.Rect(520, 400, 40, 30),
                        math.pi / 2, math.pi * 3 / 2, 5)
        pygame.draw.arc(screen, FLECHE_COLOR, pygame.Rect(840, 220, 80, 80),
                        math.pi / 4, math.pi * 3 / 2, 5)
        pygame.draw.line(screen, RIVER_COLOR, (0, 500), (900, 150), 5)
        pygame.draw.line(screen, RIVER_COLOR, (900, 150), (1000, 0), 5)
        pygame.draw.line(screen, ROAD_COLOR, (450, 250), (800, 110), 5)
        pygame.draw.line(screen, ROAD_COLOR, (450, 250), (450, 800), 5)
        pygame.draw.line(screen, ROAD_COLOR, (620, 390), (840, 740), 5)
        pygame.draw.line(screen, ROAD_COLOR, (860, 740), (940, 520), 5)
        pygame.draw.line(screen, ROAD_COLOR, (940, 520), (700, 150), 5)
        pygame.draw.line(screen, ROAD_COLOR, (800, 120), (1040, 220), 5)
        townRect = town.get_rect()
        screen.blit(town, pygame.Rect(760, 80, *townRect.size))
        screen.blit(town, pygame.Rect(1000, 180, *townRect.size))
        screen.blit(town, pygame.Rect(900, 480, *townRect.size))
        screen.blit(town, pygame.Rect(800, 700, *townRect.size))
        screen.blit(town, pygame.Rect(580, 350, *townRect.size))
        screen.blit(town, pygame.Rect(420, 400, *townRect.size))
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
        # fire cannnons
        [cannon.fire() for cannon in cannons]
        # draw cannons
        [cannon.blitme() for cannon in cannons]
        # update images
        [company.blitme() for company in blueInfantry]
        [company.blitme() for company in greenInfantry]
        if sum([company.size for company in greenInfantry]) == 0:
            menu.scene = "victory"
        if sum([company.size for company in blueInfantry]) == 0:
            menu.scene = "defeat"
    if menu.scene == "victory" or menu.scene == "defeat":
        menu.update()
        menu.blitme()
        pygame.display.flip()
        return menu.check()
    # draw screen
    pygame.display.flip()
