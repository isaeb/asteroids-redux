import pygame
import asyncio

from libraries.services.drawEffects import renderText
from math import pi, cos, sin

pressedKeys = [pygame.K_SPACE]
cooldown = 0

items = {'MODE':[0, 'REDUX', 'CLASSIC'], 'TIME':[0, 'DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY', 'ALL-TIME'], 'FILTER':[0, 'GLOBAL', 'PERSONAL', 'FRIENDS'], 'BACK':None}

def drawLeaderboard(width, height, list):
    # Create Surfaces
    surf = pygame.surface.Surface((width, int(height * len(list))))
    surf.set_colorkey((1, 1, 1))
    surf.fill((1, 1, 1))

    s = pygame.surface.Surface((width, height))
    s.set_colorkey((1, 1, 1))

    # Create Fonts
    indexFont = pygame.Font('fonts/SignwoodItalic.ttf', int(height * 0.8))

    scoreFont = pygame.Font('fonts/SignwoodItalic.ttf', int(height * 0.8))
    scoreLength = scoreFont.render('99999', False, (0, 0, 0)).get_width()

    nameFont = pygame.Font('fonts/SignwoodItalic.ttf', int(height * 0.8))
    nameLength = scoreFont.render('0000000000000', False, (0, 0, 0)).get_width()

    dateFont = pygame.Font('fonts/SignwoodItalic.ttf', int(height * 0.4))

    for index, content in enumerate(list):
        # Clear Surface
        s.fill((1, 1, 1))

        # Draw Index
        text = str(content['score'])
        font = indexFont
        startColor = pygame.Color(255, 255, 255)
        endColor = pygame.Color(200, 200, 200)
        shadowColor = pygame.Color(50, 50, 50)
        shadowOffset = (3, 3)
        outlineColor = pygame.Color(0, 0, 0)
        outlineWidth = 1
        s.blit(renderText(text, font, startColor, endColor, shadowColor, shadowOffset, outlineColor, outlineWidth), (0, 0))
        surf.blit(s, (0, int(index * height)))

        # Clear Surface
        s.fill((1, 1, 1))

        # Draw Name
        text = str(content['name'])[:12]
        font = nameFont
        startColor = pygame.Color(255, 255, 255)
        endColor = pygame.Color(200, 200, 200)
        shadowColor = pygame.Color(50, 50, 50)
        shadowOffset = (3, 3)
        outlineColor = pygame.Color(0, 0, 0)
        outlineWidth = 1
        s.blit(renderText(text, font, startColor, endColor, shadowColor, shadowOffset, outlineColor, outlineWidth), (0, 0))
        surf.blit(s, (scoreLength, int(index * height)))

        # Clear Surface
        s.fill((1, 1, 1))

        # Draw Date
        text = str(content['date'])
        font = dateFont
        startColor = pygame.Color(200, 200, 200)
        endColor = pygame.Color(150, 150, 150)
        shadowColor = pygame.Color(50, 50, 50)
        shadowOffset = (3, 3)
        outlineColor = pygame.Color(0, 0, 0)
        outlineWidth = 1
        s.blit(renderText(text, font, startColor, endColor, shadowColor, shadowOffset, outlineColor, outlineWidth), (0, 0))
        surf.blit(s, (scoreLength + nameLength, int(index * height)))
    
    return surf

def draw_rounded_rect(surface, color, rect, corner_radius):
    """
    Draws a rectangle with rounded corners.
    
    :param surface: The surface to draw on.
    :param color: The color of the rectangle.
    :param rect: The rect representing the position and size of the rectangle.
    :param corner_radius: The radius of the corners.
    """
    if corner_radius > 0:
        # Top-left corner
        pygame.draw.circle(surface, color, (rect.x + corner_radius, rect.y + corner_radius), corner_radius)
        # Top-right corner
        pygame.draw.circle(surface, color, (rect.x + rect.width - corner_radius, rect.y + corner_radius), corner_radius)
        # Bottom-left corner
        pygame.draw.circle(surface, color, (rect.x + corner_radius, rect.y + rect.height - corner_radius), corner_radius)
        # Bottom-right corner
        pygame.draw.circle(surface, color, (rect.x + rect.width - corner_radius, rect.y + rect.height - corner_radius), corner_radius)

        # Draw the rectangle without corners
        pygame.draw.rect(surface, color, (rect.x + corner_radius, rect.y, rect.width - 2 * corner_radius, rect.height))
        pygame.draw.rect(surface, color, (rect.x, rect.y + corner_radius, rect.width, rect.height - 2 * corner_radius))

        # Draw the edge rectangles to fill in the gaps
        pygame.draw.rect(surface, color, (rect.x + corner_radius, rect.y, rect.width - 2 * corner_radius, rect.height))
        pygame.draw.rect(surface, color, (rect.x, rect.y + corner_radius, rect.width, rect.height - 2 * corner_radius))
    else:
        pygame.draw.rect(surface, color, rect)

def draw_pointer(surface, color, center, size):
    shape = [0, pi * 0.7, pi * 1.3]
    points = []

    for i in shape:
        x = center[0] + size * cos(i)
        y = center[1] - size * sin(i)
        points.append((x, y))

    # Draw the star
    pygame.draw.aalines(surface, color, True, points)

class Leaderboards:
    def __init__(self, game, prevStage='Title', mode='REDUX'):
        # Define Variables
        self.startIndex = 0
        self.range = 10
        self.mode = mode
        self.time = 'DAILY'
        self.filter = 'GLOBAL'
        self.prevStage = prevStage
        self.selected = 0
        self.lbselected = 0
        self.superselected = True
        self.pointerSize = game['screenHeight'] / 48
        self.submenu = None
        self.exit = False

        # Draw Stuff
        self.refreshGUI(game)

    def refreshGUI(self, game):
        # Draw Stuff
        menuWidth = game['screenWidth'] * 0.8
        menuHeight = game['screenHeight'] * 0.8

        # Create Panel
        self.rect = pygame.Rect(game['screenWidth'] * 0.1, game['screenHeight'] * 0.1,
                           menuWidth, menuHeight)
        self.outlineRect = pygame.Rect(game['screenWidth'] * 0.1 - 1, game['screenHeight'] * 0.1 - 1,
                           menuWidth + 2, menuHeight + 2)
        self.cornerRadius = game['screenWidth'] * 0.1

        # Draw Header
        headerSize = int(menuHeight * 0.2)
        headerFont = pygame.font.Font('fonts/SignwoodItalic.ttf', headerSize)
        startColor = pygame.Color(255, 255, 150)
        endColor = pygame.Color(200, 200, 150)
        self.header = renderText(f'{self.mode}', headerFont, startColor, endColor, (50, 50, 50), (5, 5), (0, 0, 0), 1)
        self.headerPos = (game['screenWidth'] * 0.12, game['screenHeight'] * 0.12)

        # Draw Header Subscript
        headerSubSize = int(menuHeight * 0.04)
        headerSubFont = pygame.font.Font('fonts/SignwoodItalic.ttf', headerSubSize)
        startColor = pygame.Color(255, 255, 255)
        endColor = pygame.Color(200, 200, 200)
        self.headerSub = renderText(f'{self.time} Best  [ {self.startIndex} - {self.startIndex + self.range} ]', headerSubFont, startColor, endColor, (50, 50, 50), (3, 3), (0, 0, 0), 1)
        self.headerSubPos = (game['screenWidth'] * 0.12 + self.header.get_width(), game['screenHeight'] * 0.15 + headerSize - headerSubSize * 2)

        # Draw Menu Items
        itemSize = int(menuHeight * 0.1)
        itemFont = pygame.font.Font('fonts/SignwoodItalic.ttf', itemSize)
        startColor = pygame.Color(255, 255, 255)
        endColor = pygame.Color(200, 200, 200)

        self.items = []
        self.itemPos = []
        self.subItems = []
        self.subItemPos = []
        for index, item in enumerate(list(items.keys())):
            self.items.append(renderText(item, itemFont, startColor, endColor, (50, 50, 50), (3, 3), (0, 0, 0), 1))
            self.itemPos.append((game['screenWidth'] * 0.15, game['screenHeight'] * 0.35 + index * itemSize))

            if items[item] is not None:
                self.subItems.append([])
                self.subItemPos.append([])
                for subIndex, subItem in enumerate(list(items[item])[1:]):
                    self.subItems[index].append(renderText(subItem, itemFont, startColor, endColor, (50, 50, 50), (3, 3), (0, 0, 0), 1))
                    self.subItemPos[index].append((game['screenWidth'] * 0.15, game['screenHeight'] * 0.35 + subIndex * itemSize))

        # Draw Leaderboard
        
        self.lb = []
        if self.mode == 'CLASSIC':
            board = game['NGIO'].classicBoard
        elif self.mode == 'REDUX':
            board = game['NGIO'].reduxBoard
        
        for index in range(min(10, len(board))):
            self.lb.append({'name': f'{board[index]['user']['name']}',
                            'date': f'mm/dd/yyyy',
                            'score': board[index]['value']})
        
        width = menuWidth * 0.6
        self.lbheight = menuHeight * 0.07
        self.lbPos = (game['screenWidth'] * 0.42, game['screenHeight'] * 0.3)
        self.lbSurf = drawLeaderboard(width, self.lbheight, self.lb)

    async def update(self, game):
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

        # Draw Body
        draw_rounded_rect(game['screen'], pygame.Color(255, 255, 255), self.outlineRect, self.cornerRadius)
        draw_rounded_rect(game['screen'], pygame.Color(0, 0, 0), self.rect, self.cornerRadius)

        # Draw Header
        game['screen'].blit(self.header, self.headerPos)
        game['screen'].blit(self.headerSub, self.headerSubPos)

        # Draw Leaderboard List
        game['screen'].blit(self.lbSurf, self.lbPos)
        if not self.superselected:
            position = (self.lbPos[0] - game['screenWidth'] * 0.02, self.lbPos[1] + game['screenHeight'] * 0.025 + self.lbselected * self.lbheight)
            draw_pointer(game['screen'], (255, 255, 255), position, self.pointerSize * 0.75)
        
        if self.submenu is None:
            # Draw Items
            for index, item in enumerate(self.items):
                game['screen'].blit(item, self.itemPos[index])
                if self.superselected and index == self.selected:
                    position = (self.itemPos[index][0] - game['screenWidth'] * 0.02, self.itemPos[index][1] + game['screenHeight'] * 0.05)
                    draw_pointer(game['screen'], (255, 255, 255), position, self.pointerSize)
        else:
            selected = self.submenu[0]
            # Draw Items
            for index, item in enumerate(self.subItems[self.selected]):
                game['screen'].blit(item, self.subItemPos[self.selected][index])
                if index == selected:
                    position = (self.subItemPos[self.selected][index][0] - game['screenWidth'] * 0.02, self.subItemPos[self.selected][index][1] + game['screenHeight'] * 0.05)
                    draw_pointer(game['screen'], (255, 255, 255), position, self.pointerSize)

        self.updateControl(game)
        if self.exit:
            return self.prevStage
        pygame.display.flip()

    def updateControl(self, game):
        # Get player input
        keys = pygame.key.get_pressed()

        # Read player input
        if keys[pygame.K_SPACE]:
            if pygame.K_SPACE not in pressedKeys:
                pressedKeys.append(pygame.K_SPACE)
                if self.submenu is not None:
                    s = items[list(items.keys())[self.selected]][0]
                    match self.selected:
                        case 0:
                            self.mode = items[list(items.keys())[self.selected]][1:][s]
                        case 1:
                            self.time = items[list(items.keys())[self.selected]][1:][s]
                        case 2:
                            self.filter = items[list(items.keys())[self.selected]][1:][s]
                    self.refreshGUI(game)
                    self.submenu = None
                    return
                if self.superselected:
                    if self.selected == 3:
                        self.exit = True
                        return
                    self.submenu = items[list(items.keys())[self.selected]]
        else:
            if pygame.K_SPACE in pressedKeys:
                pressedKeys.remove(pygame.K_SPACE)
        if keys[pygame.K_UP]:
            if pygame.K_UP not in pressedKeys:
                pressedKeys.append(pygame.K_UP)

                if self.submenu is not None:
                    key = list(items.keys())[self.selected]
                    items[key][0] = max(0, items[key][0] - 1)
                    return
                if self.superselected:
                    self.selected = max(0, self.selected - 1)
                else:
                    self.lbselected = max(0, self.lbselected - 1)
        else:
            if pygame.K_UP in pressedKeys:
                pressedKeys.remove(pygame.K_UP)
        
        if keys[pygame.K_DOWN]:
            if pygame.K_DOWN not in pressedKeys:
                pressedKeys.append(pygame.K_DOWN)

                if self.submenu is not None:
                    key = list(items.keys())[self.selected]
                    m = len(items[key]) - 2
                    key = list(items.keys())[self.selected]
                    items[key][0] = min(m, items[key][0] + 1)
                    return
                if self.superselected:
                    self.selected = min(3, self.selected + 1)
                else:
                    self.lbselected = min(len(self.lb) - 1, self.lbselected + 1)
        else:
            if pygame.K_DOWN in pressedKeys:
                pressedKeys.remove(pygame.K_DOWN)
        if keys[pygame.K_LEFT]:
            if pygame.K_LEFT not in pressedKeys:
                pressedKeys.append(pygame.K_LEFT)

                self.superselected = True
        else:
            if pygame.K_LEFT in pressedKeys:
                pressedKeys.remove(pygame.K_LEFT)
        if keys[pygame.K_RIGHT]:
            if pygame.K_RIGHT not in pressedKeys:
                pressedKeys.append(pygame.K_RIGHT)

                if self.submenu is None and len(self.lb) > 0:
                    self.superselected = False
        else:
            if pygame.K_RIGHT in pressedKeys:
                pressedKeys.remove(pygame.K_RIGHT)
        return False
