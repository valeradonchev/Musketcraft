import pygame
from button import Button
from settings import FB_SIZE, SCALE
import numpy as np
import math


class Flag:
    """Sprite that user interacts with to give commands to Company

    Attributes
    ----------
    screen : pygame.Surface
        Surface on which Flag is drawn
    image : str
        path to image of Flag
    rect : pygame.rect.Rect
        rectangle of Flag Surface
    draggable : bool
        whether Flag can be dragged by user
    moveButton : Button
        button user presses to move Company without stopping to shoot
    attackButton : Button
        button user presses to move Company while stopping to shoot
    select : bool
        whether the buttons are diplayed
    attackMove : bool
        whether Company should stop to shoot at enemies

    Methods
    -------
    checkDrag
        drag Flag to mouse location, respond to button presses
    blitme
        draw flag, buttons

    """

    def __init__(self, screen, coords, file, draggable):
        self.screen = screen
        # self.image = pygame.image.load(file)
        size = [int(i / math.sqrt(SCALE)) for i in file.get_rect().size]
        self.image = pygame.transform.scale(file, size)
        self.rect = self.image.get_rect()
        self.rect.center = coords
        self.coords = np.array(self.rect.center, dtype=float)
        self.draggable = draggable
        self.moveButton = Button(screen, "Move")
        self.attackButton = Button(screen, "Attack")
        # 0,1=click,release to drag flag, 2,3=click,release to click button
        self.select = 0
        self.attackMove = False

    def checkDrag(self, flags, coords):
        # drag Flag to mouse location, respond to button presses
        idle = all(flag.select == 0 for flag in flags)
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        cancel = pygame.mouse.get_pressed()[2]
        if not idle and self.select == 0:
            return
        if cancel and self.select != 0:
            self.select = 0
            self.coords = coords
        if self.rect.collidepoint(mouse) and click:
            self.select = 1
        if self.select == 1 and not click:
            self.moveButton.draw((self.rect.left - FB_SIZE[0] / 2,
                                  self.rect.centery))
            self.attackButton.draw((self.rect.right + FB_SIZE[0] / 2,
                                    self.rect.centery))
            self.select = 2
        if self.select == 2 and click:
            if self.moveButton.rect.collidepoint(mouse):
                self.select = 3
            elif self.attackButton.rect.collidepoint(mouse):
                self.select = 3
            else:
                self.select = 1
        if self.select == 3 and not click:
            if self.moveButton.rect.collidepoint(mouse):
                self.attackMove = False
                self.select = 0
                self.moveButton.draw((0, 0))
                self.attackButton.draw((0, 0))
            if self.attackButton.rect.collidepoint(mouse):
                self.attackMove = True
                self.select = 0
                self.moveButton.draw((0, 0))
                self.attackButton.draw((0, 0))
        if self.select == 1:
            self.coords = mouse

    def blitme(self):
        # draw flag, buttons
        self.rect.center = self.coords
        if self.draggable:
            self.screen.blit(self.image, self.rect)
        if self.select > 1:
            self.moveButton.blitme()
            self.attackButton.blitme()
