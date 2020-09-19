import pygame.font
from settings import FB_SIZE, FB_COLOR, FB_TXT_SIZE, FB_TXT_COLOR


class Button:
    """Sprite that allows user to give specific commands to Company

    Attributes
    ----------
    screen : pygame.Surface
        Surface on which Button is drawn
    rect : pygame.rect.Rect
        rectangle of Button Surface
    color : int tuple [3], >= 0
        RGB values for color of Button
    txtColor : int tuple [3], >= 0
        RGB values for color of text on Button
    msgImage : pygame.Surface
        image of text to be printed on screen
    msgImageRect : pygame.rect.Rect
        rectangle of text image

    Methods
    -------
    draw
        set button position
    blit
        draw button to screen
    """

    def __init__(self, screen, text):
        self.screen = screen
        self.rect = pygame.Rect(0, 0, *FB_SIZE)
        self.color = FB_COLOR
        self.txtC = FB_TXT_COLOR
        self.font = pygame.font.SysFont('arial', FB_TXT_SIZE)
        self.msgImage = self.font.render(text, True, self.txtC, self.color)
        self.msgImageRect = self.msgImage.get_rect()

    def draw(self, center, text=None):
        # Set button position
        self.rect.center = center
        if text is not None:
            self.msgImage = self.font.render(text, True, self.txtC, self.color)
            self.msgImageRect = self.msgImage.get_rect()
        self.msgImageRect.center = center

    def blitme(self):
        # draw button to screen
        self.screen.fill(self.color, self.rect)
        self.screen.blit(self.msgImage, self.msgImageRect)
