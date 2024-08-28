import pygame
import math
import numpy
import asyncio

import libraries.services.spawn as spawn
from libraries.services.drawEffects import renderText
from libraries.services.fallingStarBackground import FallingStarBackground as BG

from random import random


# game = dict()

pressedKeys = []

timeTrialOptions = {'30 SECONDS':0, '60 SECONDS':0, '2 MINUTES':0, 'BACK':0}
playOptions = {'REDUX':'Redux', 'CLASSIC':'Classic', 'BACK':0}

controlsOptions = {'UP':0, 'DOWN':0, 'LEFT':0, 'RIGHT':0, 'FIRE':0, 'SPECIAL':0, 'BACK':0}
displayOptions = {'RESOLUTION':0, 'VSYNC':0, 'QUALITY':0, 'BACK':0}
audioOptions = {'VOLUME':0, 'BACK':0}
optionsOptions = {'CONTROLS':controlsOptions, 'DISPLAY':displayOptions, 'AUDIO':audioOptions, 'BACK':0}

mainOptions = {'PLAY':playOptions, 'SETTINGS':optionsOptions, 'ONLINE':'Leaderboards', 'QUIT':-1}

# Add back options
playOptions['BACK'] = mainOptions
optionsOptions['BACK'] = mainOptions

timeTrialOptions['BACK'] = playOptions

controlsOptions['BACK'] = optionsOptions
displayOptions['BACK'] = optionsOptions
audioOptions['BACK'] = optionsOptions

thickness = 3

class Title:
    def __init__(self, game:dict):
        # Set variables
        self.state = 0
        self.selected = -1
        self.width = game['screenWidth']
        self.height = game['screenHeight']
        self.progress = 0
        self.blinkSpd = 0.75
        self.displayOption = True
        self.back = dict()
        self.options = {'PRESS SPACE':0}
        self.guiSurface = None
        
        self.name = None

        # Set up gui
        nameSize = game['screenHeight'] * 0.02
        self.guiSurface = pygame.Surface((game['screenWidth'], game['screenHeight']))
        self.nameFont = pygame.font.Font('fonts/PastiRegular.otf', int(nameSize))
        self.nameX = game['screenWidth'] * 0.05
        self.nameY = game['screenHeight'] * 0.9

        game['asteroids'] = []
        game['gameWidth'] = game['screenWidth']
        game['gameHeight'] = game['screenHeight']
        game['scrollX'] = 0
        game['scrollY'] = 0
        
        self.titleSize = self.height * 0.3
        self.optionSize = self.height * 0.05
        
        # Initialize the title surface
        self.headerSurface = pygame.surface.Surface((self.width, self.titleSize + thickness * 2))
        self.headerSurface.fill((1, 1, 1))
        self.headerSurface.set_colorkey((1, 1, 1))

        # Define the font
        self.titleFont = pygame.font.Font('fonts/Signwood.ttf', int(self.titleSize * 0.6))

        # Draw Text
        textSurf = renderText('ASTEROIDS', self.titleFont, (255, 225, 255), (200, 200, 200), (50, 50, 50), (5, 5), (20, 20, 20), 3)

        x = (self.width - textSurf.get_size()[0]) / 2
        y = thickness
        self.headerSurface.blit(textSurf, (x, y))

        self.titleSubFont = pygame.font.Font('fonts/SignwoodItalic.ttf', int(self.titleSize * 0.25))
        self.titleSubSurface = renderText('REDUX', self.titleSubFont, (255, 100, 100), (150, 100, 100), (50, 50, 50), (3, 3), (20, 20, 20), 3)
        
        # Initialize the option surfaces
        self.optionSurface = pygame.surface.Surface((self.width, self.height))

        self.optionSurface.fill((1, 1, 1))
        self.optionSurface.set_colorkey((1, 1, 1))

        # Define the font
        self.optionFont = pygame.font.Font('fonts/Signwood.ttf', int(self.optionSize))
        
        # Draw the option main text
        textSurface = renderText('PRESS SPACE', self.optionFont, (150, 150, 150), (200, 200, 200), (50, 50, 50), (8, 10), (0, 0, 0), 2)
        x = self.width / 2 - textSurface.get_size()[0] / 2
        y = thickness
        self.optionSurface.blit(textSurface, (x, y))

        # Create bg
        self.bg = BG()
        self.bgSurf = pygame.surface.Surface((self.width, self.height), pygame.SRCALPHA)
        
        self.drawOptions(game)
        self.draw(game)

    async def update(self, game:dict):
        self.draw(game)
        r = await self.updateControl(game)
        return r
              
    async def updateControl(self, game:dict):

        # Get player input
        keys = pygame.key.get_pressed()

        # Read player input
        if keys[pygame.K_SPACE]:
            if pygame.K_SPACE not in pressedKeys:
                pressedKeys.append(pygame.K_SPACE)
                if self.state == 0:
                    self.options = mainOptions
                    self.state = 1
                else:
                    option = list(self.options.values())[self.selected]
                    if type(option) is dict:
                        self.options = list(self.options.values())[self.selected]
                    elif type(option) is int:
                        match option:
                            case -1:
                                # Quit
                                pygame.quit()
                                exit()

                            case 0: 
                                # Login
                                await game['NGIO'].login()
                                self.drawOptions(game)

                    else:
                        return option
                
                self.selected = 0
                self.drawOptions(game)

        else:
            if pygame.K_SPACE in pressedKeys:
                pressedKeys.remove(pygame.K_SPACE)

        if self.state == 1:
            if keys[pygame.K_UP]:
                if pygame.K_UP not in pressedKeys:
                    pressedKeys.append(pygame.K_UP)
                    if self.state == 1:
                        self.selected = max(0, self.selected - 1)
                        self.drawOptions(game)
            else:
                if pygame.K_UP in pressedKeys:
                    pressedKeys.remove(pygame.K_UP)
            
            if keys[pygame.K_DOWN]:
                if pygame.K_DOWN not in pressedKeys:
                    pressedKeys.append(pygame.K_DOWN)
                    if self.state == 1:
                        self.selected = min(len(self.options) - 1, self.selected + 1)

                        self.drawOptions(game)
            else:
                if pygame.K_DOWN in pressedKeys:
                    pressedKeys.remove(pygame.K_DOWN)
        return None
    
    def drawOptions(self, game:dict):

        #self.optionSurface = pygame.surface.Surface((self.width, len(self.options) * (self.optionSize + thickness * 2)))
        self.optionSurface.fill((1, 1, 1))
        self.optionSurface.set_colorkey((1, 1, 1))
        x = game['screenWidth'] * 0.2
        y = game['screenHeight'] * 0.4
        
        for index, key in enumerate(self.options.keys()):
            if key == 'LOGIN' and game['NGIO'].loggedIn:
                continue

            # Draw the option main text
            startColor = (150, 150, 150)
            endColor = (100, 100, 100)
            if index == self.selected:
                startColor = (255, 255, 255)
                endColor = (200, 200, 200)

            font = self.optionFont
            textSurface = renderText(key, font, startColor, endColor, (50, 50, 50), (3, 3), (0, 0, 0), 2)
            
            self.optionSurface.blit(textSurface, (self.width / 2 - textSurface.get_width() / 2, y))
            y += textSurface.get_height() * 0.7

    def updateGui(self, game:dict):
        self.name = game['NGIO'].userName
        self.guiSurface = self.nameFont.render(f'{self.name}', True, (255, 255, 255))

    def draw(self, game):

        # Clear the display
        game['screen'].blit(game['background'], (0, 0))
        self.bg.update(game)
        self.bgSurf.fill((0, 0, 0))
        self.bg.draw(self.bgSurf, game)
        game['screen'].blit(self.bgSurf, (0, 0))

        # Draw the header
        game['screen'].blit(self.headerSurface, (0, self.height * 0.03))

        # Draw the subtitile
        game['screen'].blit(self.titleSubSurface, (game['screenWidth'] / 2 - self.titleSubSurface.get_width() / 2, self.height * 0.22))

        # Draw the option
        game['screen'].blit(self.optionSurface, (0, 0))

        # Draw the username
        self.updateGui(game)
        game['screen'].blit(self.guiSurface, (self.nameX, self.nameY))

        # Update the display
        pygame.display.flip()
