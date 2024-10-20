import pygame
import math
import json

from libraries.services.drawEffects import renderText

pressedKeys = ['fire']
cooldown = 0


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

class ReduxResults:
    def __init__(self, game, asteroidsDestroyed=0, enemiesDestroyed=0, timeLeft=0, stars=3):

        self.asteroidsDestroyed = asteroidsDestroyed
        self.enemiesDestroyed = enemiesDestroyed
        self.timeLeft = timeLeft
        self.stars = stars

        menuWidth = game['screenWidth'] * 0.8
        menuHeight = game['screenHeight'] * 0.8

        # Create Panel
        self.rect = pygame.Rect(game['screenWidth'] * 0.1, game['screenHeight'] * 0.1,
                           menuWidth, menuHeight)
        self.outlineRect = pygame.Rect(game['screenWidth'] * 0.1 - 1, game['screenHeight'] * 0.1 - 1,
                           menuWidth + 2, menuHeight + 2)
        self.cornerRadius = game['screenWidth'] * 0.1

        # Draw Header
        headerSize = int(menuHeight * 0.25)
        headerFont = pygame.font.Font('fonts/SignwoodItalic.ttf', headerSize)
        startColor = pygame.Color(255, 255, 150)
        endColor = pygame.Color(200, 200, 150)
        self.header = renderText('RESULTS', headerFont, startColor, endColor, (50, 50, 50), (5, 5), (0, 0, 0), 1)
        self.headerPos = (game['screenWidth'] * 0.15, game['screenHeight'] * 0.15)

        # Darken Background
        self.darkSurf = pygame.Surface((game['screenWidth'], game['screenHeight']), pygame.SRCALPHA)
        transparent_color = (0, 0, 0, 128)  # Black with 50% transparency
        self.darkSurf.fill(transparent_color)

        # Draw Bullet Points
        pointSize = int(menuHeight * 0.08)
        pointFont = pygame.font.Font('fonts/SignwoodItalic.ttf', pointSize)
        startColor = pygame.Color(255, 255, 255)
        endColor = pygame.Color(200, 200, 200)

        points = [('Asteroids Destroyed', self.asteroidsDestroyed), ('Enemies Destroyed', self.enemiesDestroyed), ('Time Left', self.timeLeft)]
        self.pointSurf = []
        self.resultSurf = []
        self.resultOffset = []
        for point in points:
            self.pointSurf.append(renderText(point[0], pointFont, startColor, endColor, (50, 50, 50), (3, 3), (0, 0, 0), 1))

            resultText = str(int(point[1]))
            self.resultSurf.append(renderText(resultText, pointFont, startColor, endColor, (50, 50, 50), (3, 3), (0, 0, 0), 1))

            c = resultText[:-1]
            self.resultOffset.append(renderText(c, pointFont, startColor, endColor, (50, 50, 50), (3, 3), (0, 0, 0), 1).get_width())

        
        self.pointPos = (self.headerPos[0], self.headerPos[1] + headerSize * 1.3)

        # Draw grade
        self.pointSurf.append(renderText('Grade', pointFont, startColor, endColor, (50, 50, 50), (3, 3), (0, 0, 0), 1))

    def update(self, game):
        # Draw Body
        draw_rounded_rect(game['screen'], pygame.Color(255, 255, 255), self.outlineRect, self.cornerRadius)
        draw_rounded_rect(game['screen'], pygame.Color(0, 0, 0), self.rect, self.cornerRadius)

        # Draw Header
        game['screen'].blit(self.header, self.headerPos)

        # Draw Points
        positionX = self.pointPos[0]
        positionY = self.pointPos[1]
        resultX = positionX
        gutter = game['screenHeight'] * 0.02

        for index, surf in enumerate(self.pointSurf):
            if index == len(self.pointSurf) - 1:
                positionY += gutter
            game['screen'].blit(surf, (positionX, positionY))
            positionY += surf.get_height()
            resultX = max(resultX, positionX + surf.get_width())
        
        positionY = self.pointPos[1]
        resultX += game['screenWidth'] * 0.07

        for index, surf in enumerate(self.resultSurf):
            game['screen'].blit(surf, (resultX - self.resultOffset[index], positionY))
            positionY += surf.get_height()
        
        starSize = self.pointSurf[0].get_height() * 0.3
        starX = resultX
        starY = positionY + starSize + gutter
        starColor = pygame.Color(255, 255, 150)
        
        for _ in range(self.stars):
            draw_star(game['screen'], (50, 50, 50), (starX + 3, starY + 3), starSize)
            draw_star(game['screen'], starColor, (starX, starY), starSize)
            starX -= starSize * 2.2
        
        return self.updateControl(game)

    def updateControl(self, game):
        # Get player input
        keys = pygame.key.get_pressed()

        # Read player input
        if any([keys[key] for key in game['controls']['keyFire']]):
            if 'fire' not in pressedKeys:
                pressedKeys.append('fire')
                return True
        elif not any([keys[key] for key in game['controls']['keyFire']]):
            if 'fire' in pressedKeys:
                pressedKeys.remove('fire')
        if any([keys[key] for key in game['controls']['keyUp']]):
            if 'up' not in pressedKeys:
                pressedKeys.append('up')
        elif not any([keys[key] for key in game['controls']['keyUp']]):
            if 'up' in pressedKeys:
                pressedKeys.remove('up')
        
        if any([keys[key] for key in game['controls']['keyDown']]):
            if 'down' not in pressedKeys:
                pressedKeys.append('down')
        elif not any([keys[key] for key in game['controls']['keyDown']]):
            if 'down' in pressedKeys:
                pressedKeys.remove('down')
        return False
