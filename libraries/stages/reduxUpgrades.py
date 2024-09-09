import pygame
import math
import json

from libraries.services.drawEffects import renderText

# Opening JSON file
with open('libraries/upgrades.json') as json_file:
    upgradeDict = json.load(json_file)


pressedKeys = [pygame.K_SPACE]


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

def draw_star(surface, color, center, size, width=0):
    """
    Draws a 5-pointed star.

    :param surface: The surface to draw on.
    :param color: The color of the star.
    :param center: A tuple (x, y) representing the center of the star.
    :param size: The size (radius) of the star.
    """
    # Calculate the coordinates of the star
    points = []
    angle = math.pi / 2  # Start angle

    for i in range(10):
        r = size if i % 2 == 0 else size / 2
        x = center[0] + r * math.cos(angle)
        y = center[1] - r * math.sin(angle)
        points.append((x, y))
        angle += math.pi / 5

    # Draw the star
    pygame.draw.polygon(surface, color, points, width=width)

def draw_wrapped_text(surface, text, font, color, rect):
    paragraphs = text.split('\n')
    y = rect.top

    for paragraph in paragraphs:
        words = paragraph.split(' ')
        lines = []
        current_line = []

        for word in words:
            # Test the line with the new word
            current_line.append(word)
            test_line = ' '.join(current_line)
            test_width, test_height = font.size(test_line)

            if test_width <= rect.width:
                # The word fits in the line
                continue
            else:
                # The word doesn't fit, start a new line
                current_line.pop()  # Remove the word
                lines.append(' '.join(current_line))  # Add the current line to the lines list
                current_line = [word]  # Start a new line with the word

        # Add the last line to the lines list
        lines.append(' '.join(current_line))

        for line in lines:
            startColor = (255, 255, 255)
            endColor = (200, 200, 200)
            line_surf = renderText(line, font, startColor, endColor, (50, 50, 50), (3, 3), (0, 0, 0), 1)
            surface.blit(line_surf, (rect.left, y))
            if line:
                y += font.get_linesize()

        # Add a newline space
        if current_line:
            y += font.get_linesize()

def draw_player(surface, color, center, size, player):

    # Calculate the coordinates of the player
    points = []

    for vec in player.playerShape:
        x = math.cos(vec[0] + math.pi * 1.5) * vec[1] * size + center[0]
        y = math.sin(vec[0] + math.pi * 1.5) * vec[1] * size + center[1]
        points.append((x, y))

    # Draw the star
    pygame.draw.polygon(surface, color, points, width=1)

def drawStars(game, count=3):
    starSize = game['screenWidth'] * 0.04
    maxStars = 3
    color = pygame.Color(255, 255, 150)

    for c in range(maxStars):
        x = c * (starSize * 2.2) + game['screenWidth'] * 0.2
        y = game['screenHeight'] * 0.2
        if count > c:
            draw_star(game['screen'], (50, 50, 50), (x + 5, y + 5), starSize)
            draw_star(game['screen'], color, (x, y), starSize)
        else:
            draw_star(game['screen'], pygame.Color(255, 255, 255, 255), (x, y), starSize, width=1)

def findDesc(game, category):
    c = game['class']
    level = game[category] + 1
    features = game[category + 'Features']

    if level not in upgradeDict[c]['upgrades'][category]['newFeature']:
        if len(features) <= 0:
            desc = upgradeDict[c]['upgrades'][category]['defaultDescription']
            return [{'name': 'Upgrade ' + category.capitalize(), 'desc': desc}]
        
        tempDict = upgradeDict[c]['upgrades'][category]['features'][features[0]]
        for i in range(len(features) - 1):
            tempDict = tempDict['children'][features[i + 1]]
        desc = tempDict['defaultDescription']
        return [{'name': 'Upgrade ' + category.capitalize(), 'desc': desc}]
    
    newFeatures = []
    if len(features) == 0:
        for key in upgradeDict[c]['upgrades'][category]['features'].keys():
            newFeatures.append({'name': key, 'desc': upgradeDict[c]['upgrades'][category]['features'][key]['desc']})
    else:
        tempDict = upgradeDict[c]['upgrades'][category]['features']
        for feature in features:
            tempDict = tempDict[feature]['children']
        for key in list(tempDict.keys()):
            newFeatures.append({'name': key, 'desc': tempDict[key]['desc']})
    
    return newFeatures

def nextLevel(category:str, level:int):
    if level + 1 in upgradeDict['scout']['upgrades'][category]['newFeature']:
        return True
    return False

def drawDescription(game:dict, category:str, level:int, font):
    x = game['screenWidth'] * 0.53
    y = game['screenHeight'] * 0.6
    width = game['screenWidth'] * 0.35
    height = game['screenHeight'] * 0.35
    rect = pygame.Rect(x, y, width, height)
    text = {
        'movement': "Upgrade your ship's movement systems.",
        'weapons': "Upgrade your ship's weapon systems.",
        'special': "Upgrade your ship's special ability.",
        'auxiliary': "Upgrade your ship's auxiliary systems.",
    }[category]
    if nextLevel(category, level):
        text += " \nNext Level: New Ability"
    else:
        text += " \nNext Level: "
        text += {
            'movement': "Improved Mobility.",
            'weapons': "Improved Weapons.",
            'special': "Improved Special Ability.",
            'auxiliary': "Better.",
        }[category]
    draw_wrapped_text(game['screen'], text, font, (255, 255, 255), rect)

def draw_pointer(surface, color, center, size):
    shape = [0, math.pi * 0.7, math.pi * 1.3]
    points = []

    for i in shape:
        x = center[0] + size * math.cos(i)
        y = center[1] - size * math.sin(i)
        points.append((x, y))

    # Draw the star
    pygame.draw.aalines(surface, color, True, points)

class ReduxUpgrades:
    def __init__(self, game):
        menuWidth = game['screenWidth'] * 0.8
        menuHeight = game['screenHeight'] * 0.8

        self.rect = pygame.Rect(game['screenWidth'] * 0.1, game['screenHeight'] * 0.1,
                           menuWidth, menuHeight)
        self.outlineRect = pygame.Rect(game['screenWidth'] * 0.1 - 1, game['screenHeight'] * 0.1 - 1,
                           menuWidth + 2, menuHeight + 2)
        self.cornerRadius = game['screenWidth'] * 0.1

        self.optionSize = int(menuHeight * 0.08)
        self.optionFont = pygame.font.Font('fonts/Signwood.ttf', self.optionSize)

        self.descSize = int(menuHeight * 0.05)
        self.descFont = pygame.font.Font('fonts/Signwood.ttf', self.descSize)

        self.selected = 0
        self.state = 0

        self.darkSurf = pygame.Surface((game['screenWidth'], game['screenHeight']), pygame.SRCALPHA)
        transparent_color = (0, 0, 0, 128)  # Black with 50% transparency
        self.darkSurf.fill(transparent_color)

        self.stars = 3

    def update(self, game):

        if len(game['players']) == 0:
            return
        
        draw_rounded_rect(game['screen'], pygame.Color(255, 255, 255), self.outlineRect, self.cornerRadius)
        draw_rounded_rect(game['screen'], pygame.Color(0, 0, 0), self.rect, self.cornerRadius)
        drawStars(game, count=self.stars)

        player = game['players'][0]
        playerX = game['screenWidth'] * 0.65
        playerY = game['screenHeight'] * 0.4
        playerSize = game['screenWidth'] * 0.1
        draw_player(game['screen'], pygame.Color(255, 255, 255), (playerX, playerY), playerSize, player)

        # Draw Options
        self.drawOptions(game)

        # Draw class name
        thickness = 1
        text = game['class'].capitalize()
        x = game['screenWidth'] * 0.7
        y = game['screenHeight'] * 0.15

        # Draw the option main text
        startColor = (255, 255, 255)
        endColor = (200, 200, 200)
        textSurface = renderText(text, self.optionFont, startColor, endColor, (50, 50, 50), (3, 3), (0, 0, 0), 1)
        game['screen'].blit(textSurface, (x, y))

        if self.state == 0:
            r = self.updateControl(game)
            if r is not None:
                return r
        elif self.state == 1:
            # Darken bg
            game['screen'].blit(self.darkSurf, (0, 0))

            r = self.confirm.update(game)
            if r is not None:
                if r:
                    # Level up
                    category = ['movement', 'weapons', 'special', 'auxiliary'][self.selected]
                    game[category] += 1
                    self.stars -= 1
                self.state = 0

    def drawOptions(self, game):
        pointerSize = game['screenWidth'] * 0.015
        x = game['screenWidth'] * 0.16
        y = game['screenHeight'] * 0.3
        lvlx = game['screenWidth'] * 0.4
        thickness = 1
        levels = [
            game['movement'],
            game['weapons'],
            game['special'],
            game['auxiliary']
        ]

        # Draw upgrade options
        for i, text in enumerate(['Movement', 'Weapons', 'Special', 'Auxiliary']):

            # Draw the option outline
            for angle in range(8):
                textSurface = self.optionFont.render(text, True, pygame.Color(0, 0, 0))
                offsetX = x
                offsetY = y + thickness + i * (self.optionSize + thickness * 2)
                xx = offsetX + math.cos(math.pi * angle / 4) * thickness
                yy = offsetY + math.sin(math.pi * angle / 4) * thickness
                game['screen'].blit(textSurface, (xx, yy))

            # Draw the option main text
            startColor = (255, 255, 255)
            endColor = (200, 200, 200)
            textSurface = renderText(text, self.optionFont, startColor, endColor, (50, 50, 50), (3, 3), (0, 0, 0), 1)
            yy = y + thickness + i * (self.optionSize + thickness * 2)
            game['screen'].blit(textSurface, (x, yy))

            # Draw the level outline
            for angle in range(8):
                textSurface = self.optionFont.render(f'LVL{levels[i]}', True, pygame.Color(0, 0, 0))
                offsetX = lvlx
                offsetY = y + thickness + i * (self.optionSize + thickness * 2)
                xx = offsetX + math.cos(math.pi * angle / 4) * thickness
                yy = offsetY + math.sin(math.pi * angle / 4) * thickness
                game['screen'].blit(textSurface, (xx, yy))

            # Draw the level main text
            startColor = (255, 255, 255)
            endColor = (200, 200, 200)
            textSurface = renderText(f'LVL{levels[i]}', self.optionFont, startColor, endColor, (50, 50, 50), (3, 3), (0, 0, 0), 1)
            yy = y + thickness + i * (self.optionSize + thickness * 2)
            game['screen'].blit(textSurface, (lvlx, yy))

            
            if i == self.selected:
                # Draw Pointer
                draw_pointer(game['screen'], pygame.Color(255, 255, 255), (x - pointerSize - 5, yy + self.optionSize * 0.45), pointerSize)

                # Draw description
                drawDescription(game, text.lower(), levels[i], self.descFont)

        y = game['screenHeight'] * 0.4

        # Draw other options
        for i, text in enumerate(['Next Mission', 'Save & Quit']):
            i += 4

            # Draw the option outline
            for angle in range(8):
                textSurface = self.optionFont.render(text, True, pygame.Color(0, 0, 0))
                offsetX = x
                offsetY = y + thickness + i * (self.optionSize + thickness * 2)
                xx = offsetX + math.cos(math.pi * angle / 4) * thickness
                yy = offsetY + math.sin(math.pi * angle / 4) * thickness
                game['screen'].blit(textSurface, (xx, yy))

            # Draw the option main text
            startColor = (255, 255, 255)
            endColor = (200, 200, 200)
            textSurface = renderText(text, self.optionFont, startColor, endColor, (50, 50, 50), (3, 3), (0, 0, 0), 1)
            yy = y + thickness + i * (self.optionSize + thickness * 2)
            game['screen'].blit(textSurface, (x, yy))

            # Draw Pointer
            if i == self.selected:
                draw_pointer(game['screen'], pygame.Color(255, 255, 255), (x - pointerSize - 5, yy + self.optionSize * 0.45), pointerSize)

    def updateControl(self, game):
        # Get player input
        keys = pygame.key.get_pressed()

        # Read player input
        if keys[pygame.K_SPACE]:
            if pygame.K_SPACE not in pressedKeys:
                pressedKeys.append(pygame.K_SPACE)
                if self.state == 0:
                    if self.selected < 4:
                        if False:#self.stars <= 0:
                            self.state = 1
                            self.confirm = NoStarMenu(game)
                            return
                        self.state = 1
                        self.confirm = ConfirmMenu(game, ['movement', 'weapons', 'special', 'auxiliary'][self.selected])
                    elif self.selected == 4:
                        return True
        else:
            if pygame.K_SPACE in pressedKeys:
                pressedKeys.remove(pygame.K_SPACE)
        if keys[pygame.K_UP]:
            if pygame.K_UP not in pressedKeys:
                pressedKeys.append(pygame.K_UP)
                self.selected = max(self.selected - 1, 0)
        else:
            if pygame.K_UP in pressedKeys:
                pressedKeys.remove(pygame.K_UP)
        
        if keys[pygame.K_DOWN]:
            if pygame.K_DOWN not in pressedKeys:
                pressedKeys.append(pygame.K_DOWN)
                self.selected = min(self.selected + 1, 5)
        else:
            if pygame.K_DOWN in pressedKeys:
                pressedKeys.remove(pygame.K_DOWN)
        return None

class ConfirmMenu:
    def __init__(self, game, category):
        self.selected = 0
        self.category = category
        self.desc = findDesc(game, category)
        self.midX = 0
        if len(self.desc) > 1:
            self.options = []
            for option in self.desc:
                self.options.append(option['name'])
            self.options.append('Cancel')
        else:
            self.options = ['Confirm', 'Cancel']

        menuWidth = game['screenWidth'] * 0.9
        menuHeight = game['screenHeight'] * 0.15 * (len(self.desc) + 1)

        self.rect = pygame.Rect(game['screenWidth'] * 0.05, game['screenHeight'] * 0.3,
                           menuWidth, menuHeight)
        self.outlineRect = pygame.Rect(game['screenWidth'] * 0.05 - 1, game['screenHeight'] * 0.3 - 1,
                           menuWidth + 2, menuHeight + 2)
        self.cornerRadius = game['screenWidth'] * 0.1

        self.optionSize = int(game['screenHeight'] * 0.08)
        self.optionFont = pygame.font.Font('fonts/Signwood.ttf', self.optionSize)

        '''
        # Calibrate option size
        while True:
            newOptionSize = self.optionSize
            for option in self.options:
                testSurf = self.optionFont.render(option, True, pygame.Color(0, 0, 0))
                if testSurf.get_width() > game['screenWidth'] * 0.35:
                    newOptionSize -= 1
            
            if newOptionSize < self.optionSize:
                self.optionSize = newOptionSize
                self.optionFont = pygame.font.Font('fonts/Signwood.ttf', self.optionSize)
            else:
                break
        '''

        self.descSize = int(game['screenHeight'] * 0.06)
        self.descFont = pygame.font.Font('fonts/Signwood.ttf', self.descSize)
    
    def drawOptions(self, game):
        pointerSize = game['screenWidth'] * 0.015
        x = game['screenWidth'] * 0.12
        y = game['screenHeight'] * 0.35
        thickness = 1

        # Draw upgrade options
        for i, text in enumerate(self.options):

            # Draw the option outline
            for angle in range(8):
                textSurface = self.optionFont.render(text, True, pygame.Color(0, 0, 0))
                offsetX = x
                offsetY = y + thickness + i * (self.optionSize + thickness * 2) * 1.2
                xx = offsetX + math.cos(math.pi * angle / 4) * thickness
                yy = offsetY + math.sin(math.pi * angle / 4) * thickness
                game['screen'].blit(textSurface, (xx, yy))

            # Draw the option main text
            startColor = (255, 255, 255)
            endColor = (200, 200, 200)
            textSurface = renderText(text, self.optionFont, startColor, endColor, (50, 50, 50), (3, 3), (0, 0, 0), 1)
            self.midX = max(self.midX, textSurface.get_width())
            yy = y + thickness + i * (self.optionSize + thickness * 2) * 1.2
            game['screen'].blit(textSurface, (x, yy))

            
            if i == self.selected:
                # Draw Pointer
                draw_pointer(game['screen'], pygame.Color(255, 255, 255), (x - pointerSize - 5, yy + self.optionSize * 0.65), pointerSize)

                # Draw desc
                if len(self.desc) <= i:
                    i = len(self.desc) - 1
                
                text = self.desc[i]['desc']
                
                rect = pygame.Rect(x * 1.2 + self.midX, game['screenHeight'] * 0.355, game['screenWidth'] * 0.8 - (x * 1.2 + self.midX), game['screenHeight'] * 0.3)
                draw_wrapped_text(game['screen'], text, self.descFont, (255, 255, 255), rect)

    def updateControl(self, game):
        # Get player input
        keys = pygame.key.get_pressed()

        # Read player input
        if keys[pygame.K_SPACE]:
            if pygame.K_SPACE not in pressedKeys:
                pressedKeys.append(pygame.K_SPACE)
                if self.selected == len(self.options) - 1:
                    # Cancel
                    self.selected = 0
                    return False
                else:
                    # Confirm
                    if len(self.desc) > 1:
                        game[self.category + 'Features'].append(self.desc[self.selected]['name'])
                    return True
        else:
            if pygame.K_SPACE in pressedKeys:
                pressedKeys.remove(pygame.K_SPACE)
        if keys[pygame.K_UP]:
            if pygame.K_UP not in pressedKeys:
                pressedKeys.append(pygame.K_UP)
                self.selected = max(self.selected - 1, 0)
        else:
            if pygame.K_UP in pressedKeys:
                pressedKeys.remove(pygame.K_UP)
        
        if keys[pygame.K_DOWN]:
            if pygame.K_DOWN not in pressedKeys:
                pressedKeys.append(pygame.K_DOWN)
                self.selected = min(self.selected + 1, len(self.options) - 1)
        else:
            if pygame.K_DOWN in pressedKeys:
                pressedKeys.remove(pygame.K_DOWN)
        return None

    def update(self, game):
        if len(game['players']) == 0:
            return
        
        draw_rounded_rect(game['screen'], pygame.Color(255, 255, 255), self.outlineRect, self.cornerRadius)
        draw_rounded_rect(game['screen'], pygame.Color(0, 0, 0), self.rect, self.cornerRadius)

        self.drawOptions(game)

        return self.updateControl(game)

class NoStarMenu:
    def __init__(self, game):
        self.desc = "You need a star to upgrade your ship."

        menuWidth = game['screenWidth'] * 0.9
        menuHeight = game['screenHeight'] * 0.3

        self.rect = pygame.Rect(game['screenWidth'] * 0.05, game['screenHeight'] * 0.3,
                           menuWidth, menuHeight)
        self.outlineRect = pygame.Rect(game['screenWidth'] * 0.05 - 1, game['screenHeight'] * 0.3 - 1,
                           menuWidth + 2, menuHeight + 2)
        self.cornerRadius = game['screenWidth'] * 0.1

        self.descSize = int(game['screenHeight'] * 0.10)
        self.descFont = pygame.font.Font('fonts/Signwood.ttf', self.descSize)
    
    def drawOptions(self, game):
        x = game['screenWidth'] * 0.12
        y = game['screenHeight'] * 0.35
        width = game['screenWidth'] * 0.86
        height = game['screenHeight'] * 2
        rect = pygame.Rect(x, y, width, height)
        draw_wrapped_text(game['screen'], self.desc, self.descFont, (255, 255, 255), rect)

    def updateControl(self, game):
        # Get player input
        keys = pygame.key.get_pressed()

        # Read player input
        if keys[pygame.K_SPACE]:
            if pygame.K_SPACE not in pressedKeys:
                pressedKeys.append(pygame.K_SPACE)
                return False
        else:
            if pygame.K_SPACE in pressedKeys:
                pressedKeys.remove(pygame.K_SPACE)
        return None

    def update(self, game):
        if len(game['players']) == 0:
            return
        
        draw_rounded_rect(game['screen'], pygame.Color(255, 255, 255), self.outlineRect, self.cornerRadius)
        draw_rounded_rect(game['screen'], pygame.Color(0, 0, 0), self.rect, self.cornerRadius)

        self.drawOptions(game)

        return self.updateControl(game)
