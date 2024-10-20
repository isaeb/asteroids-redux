import pygame
from libraries.services.drawEffects import renderText, draw_rounded_rect
from libraries.services.fallingStarBackground import FallingStarBackground as BG
from libraries.constants import *


pressedKeys = []

timeTrialOptions = {'30 SECONDS':0, '60 SECONDS':0, '2 MINUTES':0, 'BACK':0}
playOptions = {'REDUX':'CSSRedux', 'CLASSIC':'CSSClassic', 'BACK':0}

optionsOptions = {'CONTROLS':1, 'DISPLAY':2, 'AUDIO':3, 'BACK':0}

mainOptions = {'PLAY':playOptions, 'SETTINGS':optionsOptions, 'ONLINE':'Leaderboards', 'QUIT':-1}

# Add back options
playOptions['BACK'] = mainOptions
optionsOptions['BACK'] = mainOptions

timeTrialOptions['BACK'] = playOptions

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
        self.subMenu = None
        
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
        textSurface = renderText('PRESS SPACE', self.optionFont, SELECTED_TEXT_START, SELECTED_TEXT_END, SELECTED_SHADOW, (8, 10), (0, 0, 0), 2)
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
        if self.subMenu is not None:
            if self.subMenu.update(game):
                self.subMenu = None
                self.selected = 0
                self.drawOptions(game)
            return
        r = await self.updateControl(game)
        return r
              
    async def updateControl(self, game:dict):

        # Get player input
        keys = pygame.key.get_pressed()

        # Read player input
        if True in [keys[key] for key in game['controls']['keyFire']]:
            if 'fire' not in pressedKeys:
                pressedKeys.append('fire')
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
                            
                            case 1:
                                # Controls Menu
                                kwargs = {
                                    'width': game['screenWidth'] * 0.5,
                                    'height': game['screenHeight'] * 0.6,
                                    'game': game
                                }
                                self.subMenu = controlsMenu(**kwargs)
                            
                            case 2:
                                # Video Menu
                                kwargs = {
                                    'width': game['screenWidth'] * 0.4,
                                    'height': game['screenHeight'] * 0.225,
                                    'game': game
                                }
                                self.subMenu = videoMenu(**kwargs)
                            
                            case 3:
                                # Audio Menu
                                kwargs = {
                                    'width': game['screenWidth'] * 0.4,
                                    'height': game['screenHeight'] * 0.281,
                                    'game': game
                                }
                                self.subMenu = audioMenu(**kwargs)

                    else:
                        return option
                
                self.selected = 0
                self.drawOptions(game)
        elif not True in [keys[key] for key in game['controls']['keyFire']]:
            if 'fire' in pressedKeys:
                pressedKeys.remove('fire')

        if self.state == 1:
            if True in [keys[key] for key in game['controls']['keyUp']]:
                if 'up' not in pressedKeys:
                    pressedKeys.append('up')
                    if self.state == 1:
                        self.selected = max(0, self.selected - 1)
                        self.drawOptions(game)
            elif not True in [keys[key] for key in game['controls']['keyUp']]:
                if 'up' in pressedKeys:
                    pressedKeys.remove('up')
            
            if True in [keys[key] for key in game['controls']['keyDown']]:
                if 'down' not in pressedKeys:
                    pressedKeys.append('down')
                    if self.state == 1:
                        self.selected = min(len(self.options) - 1, self.selected + 1)
                        self.drawOptions(game)
            elif not True in [keys[key] for key in game['controls']['keyDown']]:
                if 'down' in pressedKeys:
                    pressedKeys.remove('down')
        return None
    
    def drawOptions(self, game:dict):
        self.optionSurface.fill((1, 1, 1))
        self.optionSurface.set_colorkey((1, 1, 1))

        if self.subMenu is not None:
            return
        
        x = game['screenWidth'] * 0.2
        y = game['screenHeight'] * 0.4
        
        for index, key in enumerate(self.options.keys()):
            if key == 'LOGIN' and game['NGIO'].loggedIn:
                continue

            # Draw the option main text
            startColor = UNSELECTED_TEXT_START
            endColor = UNSELECTED_TEXT_END
            shadowColor = UNSELECTED_SHADOW
            if index == self.selected:
                startColor = SELECTED_TEXT_START
                endColor = SELECTED_TEXT_END
                shadowColor = SELECTED_SHADOW

            font = self.optionFont
            textSurface = renderText(key, font, startColor, endColor, shadowColor, (3, 3), (0, 0, 0), 1)
            
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

        if self.subMenu is not None:
            self.subMenu.draw(game['screen'])

        # Draw the username
        self.updateGui(game)
        game['screen'].blit(self.guiSurface, (self.nameX, self.nameY))

        # Update the display
        pygame.display.flip()

class controlsMenu:
    def __init__(self, width, height, game:dict):
        self.selected = 0
        self.maxSelected = 7
        self.edit = False
        self.keyCount = 0
        self.waiting = False

        self.width = width
        self.height = height

        self.x = game['screenWidth'] / 2 - width / 2
        self.y = game['screenHeight'] * 0.35

        self.bg = subMenuBG(self.x, self.y, width, height)
        self.options = game['controls'].copy()
        self.font = pygame.Font('fonts/Signwood.ttf', int(self.height * 0.07))

        self.tableWidth = width * 0.8
        self.tableHeight = height * 0.8
        self.margin = self.tableWidth * 0.02
        self.spacing = self.tableWidth * 0.02
        self.tableX = self.x + width * 0.1
        self.tableY = self.y + height * 0.1
        self.tableIndexHeight = self.tableHeight / 8
        self.tableSurface = pygame.surface.Surface((self.tableWidth, self.tableHeight))
        self.drawTable(self.tableSurface, game)

    def update(self, game:dict):
        return self.updateControl(game)

    def draw(self, surface):

        # Draw Background
        self.bg.draw(surface)
        
        # Draw Table
        surface.blit(self.tableSurface, (self.tableX, self.tableY))

    def drawTable(self, surface, game:dict):

        surface.fill((0, 0, 0, 0))
        X = self.margin
        Y = 0
        for i, (text, keys) in enumerate(self.options.items()):
            if i == self.selected and not self.edit:
                startColor = SELECTED_TEXT_START
                endColor = SELECTED_TEXT_END
                shadowColor = SELECTED_SHADOW
            else:
                startColor = UNSELECTED_TEXT_START
                endColor = UNSELECTED_TEXT_END
                shadowColor = UNSELECTED_SHADOW
            
            # Render Text
            textSurf = renderText(text[3:], self.font, startColor, endColor, shadowColor, (2, 2), (0, 0, 0), 1)
            surface.blit(textSurf, (self.margin, Y))

            X = max(X, textSurf.get_width() + self.margin)
            Y += self.tableIndexHeight
        
        if 7 == self.selected:
            startColor = SELECTED_TEXT_START
            endColor = SELECTED_TEXT_END
            shadowColor = SELECTED_SHADOW
        else:
            startColor = UNSELECTED_TEXT_START
            endColor = UNSELECTED_TEXT_END
            shadowColor = UNSELECTED_SHADOW

        textSurf = renderText('BACK', self.font, startColor, endColor, shadowColor, (2, 2), (0, 0, 0), 1)
        surface.blit(textSurf, (self.margin, Y))
        
        X += self.spacing
        Y = 0
        for i, (text, keys) in enumerate(self.options.items()):
            if i == self.selected and self.edit:
                startColor = SELECTED_TEXT_START
                endColor = SELECTED_TEXT_END
                shadowColor = SELECTED_SHADOW
            else:
                startColor = UNSELECTED_TEXT_START
                endColor = UNSELECTED_TEXT_END
                shadowColor = UNSELECTED_SHADOW
            
            keyString = ', '.join([pygame.key.name(key) for key in keys])
            keySurf = renderText(keyString, self.font, startColor, endColor, shadowColor, (2, 2), (0, 0, 0), 1)
            surface.blit(keySurf, (X, Y))

            Y += self.tableIndexHeight

    def updateControl(self, game):
        # Get player input
        keys = pygame.key.get_pressed()

        if self.edit:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.options[list(self.options.keys())[self.selected]].append(event.key)
                    self.drawTable(self.tableSurface, game)
                    self.keyCount += 1
                    self.waiting = True
                elif event.type == pygame.KEYUP:
                    self.drawTable(self.tableSurface, game)
                    self.keyCount -= 1
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            
            if self.waiting and self.keyCount <= 0:
                if self.selected >= 6:
                    self.edit = False
                else:
                    self.selected += 1
                    # Clear Controls
                    self.options[list(self.options.keys())[self.selected]] = []
                self.waiting = False
                self.drawTable(self.tableSurface, game)
            return

        # Read player input
        if True in [keys[key] for key in game['controls']['keyFire']]:
            if 'fire' not in pressedKeys:

                if self.selected == 7:
                    game['controls'] = self.options
                    pressedKeys.append('fire')
                    return True

                # Clear Controls
                self.options[list(self.options.keys())[self.selected]] = []

                # Goto Edit Mode
                self.edit = True
                self.waiting = False
                self.keyCount = 1

                self.drawTable(self.tableSurface, game)
                pressedKeys.append('fire')
        elif not True in [keys[key] for key in game['controls']['keyFire']]:
            if 'fire' in pressedKeys:
                pressedKeys.remove('fire')

        if True in [keys[key] for key in game['controls']['keyUp']]:
            if 'up' not in pressedKeys:
                pressedKeys.append('up')
                self.selected = max(0, self.selected - 1)
                self.drawTable(self.tableSurface, game)
        elif not True in [keys[key] for key in game['controls']['keyUp']]:
            if 'up' in pressedKeys:
                pressedKeys.remove('up')

        if True in [keys[key] for key in game['controls']['keyDown']]:
            if 'down' not in pressedKeys:
                pressedKeys.append('down')
                self.selected = min(self.maxSelected, self.selected + 1)
                self.drawTable(self.tableSurface, game)
        elif not True in [keys[key] for key in game['controls']['keyDown']]:
            if 'down' in pressedKeys:
                pressedKeys.remove('down')

        return None     

class videoMenu:
    def __init__(self, width, height, game:dict):
        self.selected = 0
        self.maxSelected = 2

        self.width = width
        self.height = height

        self.x = game['screenWidth'] / 2 - width / 2
        self.y = game['screenHeight'] * 0.35

        self.bg = subMenuBG(self.x, self.y, width, height)
        self.options = game['videoSettings'].copy()
        self.font = pygame.Font('fonts/Signwood.ttf', int(self.height * 0.187))

        self.tableWidth = width * 0.8
        self.tableHeight = height * 0.8
        self.margin = self.tableWidth * 0.02
        self.spacing = self.tableWidth * 0.02
        self.tableX = self.x + width * 0.1
        self.tableY = self.y + height * 0.1
        self.tableIndexHeight = self.tableHeight / 3
        self.tableSurface = pygame.surface.Surface((self.tableWidth, self.tableHeight))
        self.drawTable(self.tableSurface, game)

    def update(self, game:dict):
        return self.updateControl(game)

    def draw(self, surface):

        # Draw Background
        self.bg.draw(surface)
        
        # Draw Table
        surface.blit(self.tableSurface, (self.tableX, self.tableY))

    def drawTable(self, surface, game:dict):

        surface.fill((0, 0, 0, 0))
        X = self.margin
        Y = 0
        for i, (key, value) in enumerate(self.options.items()):
            if i == self.selected:
                startColor = SELECTED_TEXT_START
                endColor = SELECTED_TEXT_END
                shadowColor = SELECTED_SHADOW
            else:
                startColor = UNSELECTED_TEXT_START
                endColor = UNSELECTED_TEXT_END
                shadowColor = UNSELECTED_SHADOW
            
            # Render Text
            text = {'maxFPS': 'FPS Limit', 'quality': 'Quality'}[key]
            textSurf = renderText(text, self.font, startColor, endColor, shadowColor, (2, 2), (0, 0, 0), 1)
            surface.blit(textSurf, (self.margin, Y))

            X = max(X, textSurf.get_width() + self.margin)
            Y += self.tableIndexHeight
        
        if self.maxSelected == self.selected:
            startColor = SELECTED_TEXT_START
            endColor = SELECTED_TEXT_END
            shadowColor = SELECTED_SHADOW
        else:
            startColor = UNSELECTED_TEXT_START
            endColor = UNSELECTED_TEXT_END
            shadowColor = UNSELECTED_SHADOW

        textSurf = renderText('BACK', self.font, startColor, endColor, shadowColor, (2, 2), (0, 0, 0), 1)
        surface.blit(textSurf, (self.margin, Y))
        
        X += self.spacing
        Y = 0
        for i, (key, value) in enumerate(self.options.items()):
            if i == self.selected:
                startColor = SELECTED_TEXT_START
                endColor = SELECTED_TEXT_END
                shadowColor = SELECTED_SHADOW
            else:
                startColor = UNSELECTED_TEXT_START
                endColor = UNSELECTED_TEXT_END
                shadowColor = UNSELECTED_SHADOW
            
            if i == 0:
                text = str(value)
                if value == -1:
                    text = 'Unlimited'
            elif i == 1:
                text = str(value).capitalize()

            textSurf = renderText(text, self.font, startColor, endColor, shadowColor, (2, 2), (0, 0, 0), 1)
            surface.blit(textSurf, (X, Y))

            Y += self.tableIndexHeight

    def updateControl(self, game):
        # Get player input
        keys = pygame.key.get_pressed()

        # Read player input
        if any([keys[key] for key in game['controls']['keyFire']]):
            if 'fire' not in pressedKeys:

                if self.selected == self.maxSelected:
                    game['videoSettings'] = self.options
                    pressedKeys.append('fire')
                    return True

                # Update Value
                match list(self.options.keys())[self.selected]:
                    case 'maxFPS':
                        values = [-1, 30, 60, 75, 90, 120, 144, 165, 240]
                        for i in range(len(values)):
                            if values[i] == self.options['maxFPS']:
                                if i == len(values) - 1:
                                    self.options['maxFPS'] = values[0]
                                else:
                                    self.options['maxFPS'] = values[i + 1]
                                break
                    case 'quality':
                        values = ['low', 'medium', 'high']
                        for i in range(len(values)):
                            if values[i] == self.options['quality']:
                                if i == len(values) - 1:
                                    self.options['quality'] = values[0]
                                else:
                                    self.options['quality'] = values[i + 1]
                                break

                self.drawTable(self.tableSurface, game)
                pressedKeys.append('fire')
        elif not any([keys[key] for key in game['controls']['keyFire']]):
            if 'fire' in pressedKeys:
                pressedKeys.remove('fire')

        if True in [keys[key] for key in game['controls']['keyUp']]:
            if 'up' not in pressedKeys:
                pressedKeys.append('up')
                self.selected = max(0, self.selected - 1)
                self.drawTable(self.tableSurface, game)
        elif not True in [keys[key] for key in game['controls']['keyUp']]:
            if 'up' in pressedKeys:
                pressedKeys.remove('up')

        if True in [keys[key] for key in game['controls']['keyDown']]:
            if 'down' not in pressedKeys:
                pressedKeys.append('down')
                self.selected = min(self.maxSelected, self.selected + 1)
                self.drawTable(self.tableSurface, game)
        elif not True in [keys[key] for key in game['controls']['keyDown']]:
            if 'down' in pressedKeys:
                pressedKeys.remove('down')

        return None     

class audioMenu:
    def __init__(self, width, height, game:dict):
        self.maxCooldown = 0.25
        self.cooldownLeft = self.maxCooldown
        self.cooldownRight = self.maxCooldown

        self.selected = 0
        self.maxSelected = 3

        self.width = width
        self.height = height

        self.x = game['screenWidth'] / 2 - width / 2
        self.y = game['screenHeight'] * 0.35

        self.bg = subMenuBG(self.x, self.y, width, height)
        self.options = game['audioSettings'].copy()
        self.font = pygame.Font('fonts/Signwood.ttf', int(self.height * 0.14))

        self.tableWidth = width * 0.8
        self.tableHeight = height * 0.8
        self.margin = self.tableWidth * 0.02
        self.spacing = self.tableWidth * 0.02
        self.tableX = self.x + width * 0.1
        self.tableY = self.y + height * 0.1
        self.tableIndexHeight = self.tableHeight / 4
        self.tableSurface = pygame.surface.Surface((self.tableWidth, self.tableHeight))

        self.sliders = {}
        for option in list(self.options.keys()):
            self.sliders[option] = slider(self.tableWidth * 0.6, self.height * 0.14)

        self.drawTable(self.tableSurface, game)

    def update(self, game:dict):
        return self.updateControl(game)

    def draw(self, surface):

        # Draw Background
        self.bg.draw(surface)
        
        # Draw Table
        surface.blit(self.tableSurface, (self.tableX, self.tableY))

    def drawTable(self, surface, game:dict):
        surface.fill((0, 0, 0, 0))
        X = self.margin
        Y = 0
        for i, (key, value) in enumerate(self.options.items()):
            if i == self.selected:
                startColor = SELECTED_TEXT_START
                endColor = SELECTED_TEXT_END
                shadowColor = SELECTED_SHADOW
            else:
                startColor = UNSELECTED_TEXT_START
                endColor = UNSELECTED_TEXT_END
                shadowColor = UNSELECTED_SHADOW
            
            # Render Text
            text = key.capitalize()
            textSurf = renderText(text, self.font, startColor, endColor, shadowColor, (2, 2), (0, 0, 0), 1)
            surface.blit(textSurf, (self.margin, Y))

            X = max(X, textSurf.get_width() + self.margin)
            Y += self.tableIndexHeight
        
        if self.maxSelected == self.selected:
            startColor = SELECTED_TEXT_START
            endColor = SELECTED_TEXT_END
            shadowColor = SELECTED_SHADOW
        else:
            startColor = UNSELECTED_TEXT_START
            endColor = UNSELECTED_TEXT_END
            shadowColor = UNSELECTED_SHADOW

        textSurf = renderText('BACK', self.font, startColor, endColor, shadowColor, (2, 2), (0, 0, 0), 1)
        surface.blit(textSurf, (self.margin, Y))
        
        X += self.spacing
        Y = 0
        for i, (key, value) in enumerate(self.options.items()):
            if i == self.selected:
                innerColor = SELECTED_TEXT_START
                outerColor = SELECTED_TEXT_END
            else:
                innerColor = UNSELECTED_TEXT_START
                outerColor = UNSELECTED_TEXT_END
            self.sliders[key].draw(surface, X, Y + 3, value, innerColor, outerColor)
            Y += self.tableIndexHeight

    def updateControl(self, game):
        # Get player input
        keys = pygame.key.get_pressed()

        # Read player input
        if any([keys[key] for key in game['controls']['keyFire']]):
            if 'fire' not in pressedKeys:

                if self.selected == self.maxSelected:
                    game['audioSettings'] = self.options
                    pressedKeys.append('fire')
                    return True

                self.drawTable(self.tableSurface, game)
                pressedKeys.append('fire')
        elif not any([keys[key] for key in game['controls']['keyFire']]):
            if 'fire' in pressedKeys:
                pressedKeys.remove('fire')

        if any([keys[key] for key in game['controls']['keyLeft']]):
            if 'left' not in pressedKeys:
                pressedKeys.append('left')
                self.options[list(self.options.keys())[self.selected]] = max(0, self.options[list(self.options.keys())[self.selected]] - 10)
                self.drawTable(self.tableSurface, game)
            else:
                self.cooldownLeft = max(0, self.cooldownLeft - game['frametime'] / 1000)
                if self.cooldownLeft == 0:
                    self.options[list(self.options.keys())[self.selected]] = max(0, self.options[list(self.options.keys())[self.selected]] - (game['frametime'] / 1000) * 50)
                    self.drawTable(self.tableSurface, game)
        elif not any([keys[key] for key in game['controls']['keyLeft']]):
            self.cooldownLeft = self.maxCooldown
            if 'left' in pressedKeys:
                pressedKeys.remove('left')

        if any([keys[key] for key in game['controls']['keyRight']]):
            if 'right' not in pressedKeys:
                pressedKeys.append('right')
                self.options[list(self.options.keys())[self.selected]] = min(100, self.options[list(self.options.keys())[self.selected]] + 10)
                self.drawTable(self.tableSurface, game)
            else:
                self.cooldownRight = max(0, self.cooldownRight - game['frametime'] / 1000)
                if self.cooldownRight == 0:
                    self.options[list(self.options.keys())[self.selected]] = min(100, self.options[list(self.options.keys())[self.selected]] + (game['frametime'] / 1000) * 50)
                    self.drawTable(self.tableSurface, game)
        elif not any([keys[key] for key in game['controls']['keyRight']]):
            self.cooldownRight = self.maxCooldown
            if 'right' in pressedKeys:
                pressedKeys.remove('right')

        if any([keys[key] for key in game['controls']['keyUp']]):
            if 'up' not in pressedKeys:
                pressedKeys.append('up')
                self.selected = max(0, self.selected - 1)
                self.drawTable(self.tableSurface, game)
        elif not any([keys[key] for key in game['controls']['keyUp']]):
            if 'up' in pressedKeys:
                pressedKeys.remove('up')

        if any([keys[key] for key in game['controls']['keyDown']]):
            if 'down' not in pressedKeys:
                pressedKeys.append('down')
                self.selected = min(self.maxSelected, self.selected + 1)
                self.drawTable(self.tableSurface, game)
        elif not any([keys[key] for key in game['controls']['keyDown']]):
            if 'down' in pressedKeys:
                pressedKeys.remove('down')

        return None     

class subMenuBG:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        thickness = 1
        self.back = pygame.Rect(x, y, width, height)
        self.oback = pygame.Rect(x + thickness, y + thickness, width - thickness * 2, height - thickness * 2)
    
    def draw(self, surface:pygame.Surface):

        # White
        draw_rounded_rect(surface, (255, 255, 255), self.back, self.width * 0.02)

        # Black
        draw_rounded_rect(surface, (0, 0, 0), self.oback, self.width * 0.02)

class slider:
    def __init__(self, width, height, minValue=0, maxValue=100):
        self.width = width
        self.height = height

        self.minValue = minValue
        self.maxValue = maxValue

        self.bracketWidth = self.width * 0.03

        self.cursorWidth = self.width * 0.04
        self.cursorHeight = self.height - self.bracketWidth * 2.6
        self.cursorY = self.bracketWidth * 1.3
        self.Xmin = self.bracketWidth * 1.3
        self.Xmax = self.width - self.cursorWidth
    
    def draw(self, surface, x, y, value, innerColor=(255, 255, 255), outlineColor=(50, 50, 50)):
        newSurf = pygame.Surface((self.width, self.height))

        # Left Bracket
        lines = [(0, 0), (self.width * 0.05, 0), (self.width * 0.05, self.bracketWidth), (self.bracketWidth, self.bracketWidth), (self.bracketWidth, self.height - self.bracketWidth), (self.width * 0.05, self.height - self.bracketWidth), (self.width * 0.05, self.height - 1), (0, self.height - 1)]
        pygame.draw.polygon(newSurf, innerColor, lines)
        pygame.draw.lines(newSurf, outlineColor, True, lines)

        # Right Bracket
        lines = [(self.width - 1, 0), (self.width * 0.95 - 1, 0), (self.width * 0.95 - 1, self.bracketWidth), (self.width - self.bracketWidth - 1, self.bracketWidth), (self.width - self.bracketWidth - 1, self.height - self.bracketWidth), (self.width * 0.95 - 1, self.height - self.bracketWidth), (self.width * 0.95 - 1, self.height - 1), (self.width - 1, self.height - 1)]
        pygame.draw.polygon(newSurf, innerColor, lines)
        pygame.draw.lines(newSurf, outlineColor, True, lines)

        # Cursor
        cx = (self.Xmax - self.Xmin) * value / self.maxValue
        lines = [(self.Xmin, self.cursorY), (cx + self.cursorWidth, self.cursorY), (cx + self.cursorWidth, self.cursorY + self.cursorHeight), (self.Xmin, self.cursorY + self.cursorHeight)]
        pygame.draw.polygon(newSurf, innerColor, lines)
        pygame.draw.lines(newSurf, outlineColor, True, lines)
        surface.blit(newSurf, (x, y))
