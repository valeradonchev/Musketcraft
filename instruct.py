from button import Button
import pygame
from settings import FB_TXT_SIZE, FB_TXT_COLOR, BG_COLOR

# Note: This method was borrowed from user ShadowHawk on StackOverflow
# https://stackoverflow.com/questions/32590131/pygame-blitting-text-with-an
# -escape-character-or-newline
def multiLine(string, font, rect, fontColour, BGColour, justification=0):
    """Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Parameters
    ----------
    string - the text you wish to render. \n begins a new line.
    font - a Font object
    rect - a rect style giving the size of the surface requested.
    fontColour - a three-byte tuple of the rgb value of the
             text color. ex (0, 0, 0) = BLACK
    BGColour - a three-byte tuple of the rgb value of the surface.
    justification - 0 (default) left-justified
                1 horizontally centered
                2 right-justified

    Returns
    -------
    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
    """

    finalLines = []
    requestedLines = string.splitlines()
    # Create a series of lines that will fit on the provided
    # rectangle.
    for requestedLine in requestedLines:
        if font.size(requestedLine)[0] > rect.width:
            words = requestedLine.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if font.size(word)[0] >= rect.width:
                    raise TextRectException("The word " + word + " is too long to fit in the rect passed.")
            # Start a new line
            accumulatedLine = ""
            for word in words:
                testLine = accumulatedLine + word + " "
                # Build the line while the words fit.
                if font.size(testLine)[0] < rect.width:
                    accumulatedLine = testLine
                else:
                    finalLines.append(accumulatedLine)
                    accumulatedLine = word + " "
            finalLines.append(accumulatedLine)
        else:
            finalLines.append(requestedLine)

    # Let's try to write the text out on the surface.
    surface = pygame.Surface(rect.size)
    surface.fill(BGColour)
    accumulatedHeight = 0
    for line in finalLines:
        if accumulatedHeight + font.size(line)[1] >= rect.height:
            raise TextRectException("Once word-wrapped, the text string was too tall to fit in the rect.")
        if line != "":
            tempSurface = font.render(line, 1, fontColour)
        if justification == 0:
            surface.blit(tempSurface, (0, accumulatedHeight))
        elif justification == 1:
            surface.blit(tempSurface, ((rect.width - tempSurface.get_width()) / 2, accumulatedHeight))
        elif justification == 2:
            surface.blit(tempSurface, (rect.width - tempSurface.get_width(), accumulatedHeight))
        else:
            raise TextRectException("Invalid justification argument: " + str(justification))
        accumulatedHeight += font.size(line)[1]
    return surface


class TextRectException:
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message


class Menu():
    def __init__(self, scene, x, y, text, screen):
        self.next = Button(screen, text)
        self.x = x
        self.y = y
        self.select = 0
        self.scene = scene
        self.screen = screen
        text = ("September 7, 1812\n"
                "Emperor Napoleon!\n"
"The Russian Army has, at long last, turned to face us on the battlefield "
"70 miles west of Moscow. Our army is ready! Drag the flag of an infantry "
"company to order them to a location, and click the 'Attack' button for them to "
"attack the enemy on sight, or the 'Move' button to have them march without "
"firing a shot. You can also click on the company to order them to engage the "
"enemy with bayonets. Remember: make the enemy flee by shattering their morale "
"with overwhelming numbers, and use bayonets to finish off wounded formations.")
        self.text = multiLine(text, pygame.font.SysFont('arial', FB_TXT_SIZE),
                              pygame.Rect(20, 20, 1160, 660), FB_TXT_COLOR,
                              BG_COLOR)

    def check(self):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        if self.next.rect.collidepoint(mouse) and click:
            self.select = 1
        if self.select == 1 and not click:
            if self.next.rect.collidepoint(mouse):
                if self.scene == "instruction":
                    self.scene = "borodino"
                    return
                else:
                    return "restart"
            else:
                self.select = 0
        self.scene = "instruction"

    def update(self):
        if self.scene == "victory":
            text = ("Victory! \n \n"
"The Russian Army has retreated from the battlefield sir! "
"I still believe you should sent the Imperial Guard. As it stands, their army "
"is still a threat, and the heavy losses we suffered will be difficult to "
"replace, especially with the Russian serfs attacking our supplies. However, "
"our scouts are reporting pillars of smoke rising from the direction of "
"Moscow. The Russians wouldn't light their own capital ablaze just to keep us "
"out... would they?\nClick the button if you want to try the battle again!")
        if self.scene == "defeat":
            text = ("Defeat! \n \n"
"Our troops, exhausted by the 3 month march to Moscow, and weakened by the "
"lack of supplies due to the raids made by Russian serfs of all people, "
"proved unable to withstand the ferocious spirit of the Russian soldiers. "
"Their unwavering resolve even in the frenzy of a bayonet melee is unmatched! "
"We are forced to retreat, and with winter coming soon, we may not have "
"the opportunity for another invasion until next year. But, we shall return "
"and shatter the enemies of the French Empire!\n"
"Click the button if you want to try the battle again")
        self.text = multiLine(text, pygame.font.SysFont('arial', FB_TXT_SIZE),
                              pygame.Rect(20, 20, 1160, 660), FB_TXT_COLOR,
                              BG_COLOR)

    def blitme(self):
        self.screen.blit(self.text, (20, 20))
        self.next.draw((self.x, self.y))
        self.next.blitme()
