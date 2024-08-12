import pygame
import math
import numpy
import asyncio

import libraries.services.spawn as spawn
from libraries.services.drawEffects import renderText

from random import random


# game = dict()

pressedKeys = []

timeTrialOptions = {'30 SECONDS':0, '60 SECONDS':0, '2 MINUTES':0, 'BACK':0}
playOptions = {'REDUX':'Redux', 'CLASSIC':'Classic', 'TIME TRIALS':timeTrialOptions, 'BACK':0}

controlsOptions = {'UP':0, 'DOWN':0, 'LEFT':0, 'RIGHT':0, 'FIRE':0, 'SPECIAL':0, 'BACK':0}
displayOptions = {'RESOLUTION':0, 'VSYNC':0, 'QUALITY':0, 'BACK':0}
audioOptions = {'VOLUME':0, 'BACK':0}
optionsOptions = {'CONTROLS':controlsOptions, 'DISPLAY':displayOptions, 'AUDIO':audioOptions, 'BACK':0}

mainOptions = {'PLAY':playOptions, 'SETTINGS':optionsOptions, 'LEADERBOARDS':0, 'EXTRAS':0, 'LOGIN':0}

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
        nameSize = game['screenHeight'] * 0.08
        self.guiSurface = pygame.Surface((game['screenWidth'], game['screenHeight']))
        self.nameFont = pygame.font.Font('fonts/PastiRegular.otf', int(nameSize))
        self.nameX = game['screenWidth'] * 0.05
        self.nameY = game['screenHeight'] * 0.9

        game['asteroids'] = []
        game['gameWidth'] = game['screenWidth']
        game['gameHeight'] = game['screenHeight']


        
        self.titleSize = self.height * 0.3
        self.optionSize = self.height * 0.07
        
        # Initialize the title surface
        self.headerSurface = pygame.surface.Surface((self.width, self.titleSize + thickness * 2))
        self.headerSurface.fill((1, 1, 1))
        self.headerSurface.set_colorkey((1, 1, 1))

        # Define the font
        self.titleFont = pygame.font.Font('fonts/SignwoodItalic.ttf', int(self.titleSize))

        # Draw Text
        textSurf = renderText('ASTEROIDS', self.titleFont, (180, 180, 180), (225, 225, 225), (50, 50, 50), (8, 10), (20, 20, 20), 3)

        x = (self.width - textSurf.get_size()[0]) / 2
        y = thickness
        self.headerSurface.blit(textSurf, (x, y))

        # Initialize the option surfaces
        self.optionSurface = pygame.surface.Surface((self.width, self.height))

        self.optionSurface.fill((1, 1, 1))
        self.optionSurface.set_colorkey((1, 1, 1))

        # Define the font
        self.optionFont = pygame.font.Font('fonts/SignwoodItalic.ttf', int(self.optionSize))
        self.playFont = pygame.font.Font('fonts/SignwoodItalic.ttf', int(self.optionSize * 2))
        
        # Draw the option main text
        textSurface = renderText('PRESS SPACE', self.optionFont, (150, 150, 150), (200, 200, 200), (50, 50, 50), (8, 10), (0, 0, 0), 2)
        x = (self.width - textSurface.get_size()[0]) / 2
        y = thickness
        self.optionSurface.blit(textSurface, (x, y))

        # Create asteroids
        for _ in range(8):
            spawn.spawnAsteroid(game, color=(0, 0, 0))

        # Clear background
        game['background'].fill((0, 0, 0))

        # Generate points
        starCount = 60
        starX = numpy.random.uniform(0, self.width, starCount)
        starY = numpy.random.uniform(0, self.height, starCount)

        # Draw points
        for index in range(starCount):
            pygame.draw.circle(game['background'], pygame.Color(255, 255, 255), (starX[index], starY[index]), 1)
        
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
                            case 0: 
                                # Login
                                await game['NGIO'].newSession()
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
        for index, key in enumerate(self.options.keys()):
            if key == 'LOGIN' and game['NGIO'].loggedIn:
                continue

            # Draw the option main text
            color = (200, 200, 200)
            if index == self.selected:
                color = pygame.Color(200, 200, 0)

            if index == 0:
                font = self.playFont
            else:
                font = self.optionFont
            textSurface = renderText(key, font, color, (150, 150, 150), (50, 50, 50), (5, 5), (0, 0, 0), 2)
            x = game['screenWidth'] * 0.05
            y = thickness + index * (self.optionSize + thickness * 2)
            if index > 0:
                y += self.optionSize
            self.optionSurface.blit(textSurface, (x, y))

    def updateGui(self, game:dict):
        self.name = game['NGIO'].userName
        self.guiSurface = self.nameFont.render(f'{self.name}', True, (255, 255, 255))

    def draw(self, game):

        # Clear the display
        game['screen'].blit(game['background'], (0, 0))

        # Clear game layers
        for layer in game['layers']:
            layer.fill((1, 1, 1))
            layer.set_colorkey((1, 1, 1))
        
        # Update Asteroids
        game['asteroids'] = [asteroids for asteroids in game['asteroids'] if asteroids.update(game)]

        # Draw game layers
        for layer in game['layers']:
            game['screen'].blit(layer, (0, 0))

        # Draw the header
        game['screen'].blit(self.headerSurface, (0, self.height * 0.03))

        # Draw the option
        game['screen'].blit(self.optionSurface, (0, self.height * 0.38))

        # Draw the username
        self.updateGui(game)
        game['screen'].blit(self.guiSurface, (self.nameX, self.nameY))

        # Update the display
        pygame.display.flip()
