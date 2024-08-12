"""
Module providing a class for particles
"""

import pygame


class Particle:
    """
    Class for particles
    """
    def __init__(self, x:float, y:float, x_vel:float, y_vel:float, startingSize:float, endingSize:float, startingColor:pygame.Color, endingColor:pygame.Color, health:float, layer=0):
        """
        Args:
            x (float): x position
            y (float): y position
            x_vel (float): horizontal velocity
            y_vel (float): vertical velocity
            startingSize (float): starting radius
            endingSize (float): ending radius
            startingColor (pygame.Color): starting color
            endingColor (pygame.Color): ending color
            health (float): how long the particle lasts (in seconds)
        """

        self.x = x
        self.y = y
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.startingSize = startingSize
        self.endingSize = endingSize
        self.startingColor = startingColor
        self.endingColor = endingColor
        self.health = health
        self.progress = 0
        self.layer = layer


    def draw(self, game:dict):
        """
        Args:
            game (dict): The game dict
        """

        cSize = self.startingSize * (1 - self.progress) + self.endingSize * (self.progress)
        cR = max(0, self.startingColor.r * (1 - self.progress) + self.endingColor.r * (self.progress))
        cG = max(0, self.startingColor.g * (1 - self.progress) + self.endingColor.g * (self.progress))
        cB = max(0, self.startingColor.b * (1 - self.progress) + self.endingColor.b * (self.progress))
        cA = max(0, self.startingColor.a * (1 - self.progress) + self.endingColor.a * (self.progress))
        cColor = pygame.Color(int(cR), int(cG), int(cB))

        scrollOffsetX = - game['scrollX']
        scrollOffsetY = - game['scrollY']
        
        drawX = [0]
        drawY = [0]
        
        # draw at y - gameHeight
        if self.y + cSize + scrollOffsetY > game['gameHeight']:
            drawY.append(-game['gameHeight'])

        # draw at y + gameHeight
        if self.y - cSize + scrollOffsetY < 0:
            drawY.append(game['gameHeight'])

        # draw ship at x - screenWidth
        if self.x + cSize + scrollOffsetX > game['gameWidth']:
            drawX.append(-game['gameWidth'])

        # draw ship at x + screenWidth
        if self.x - cSize + scrollOffsetX < 0:
            drawX.append(game['gameWidth'])

        for x in drawX:
            for y in drawY:
                surface = pygame.Surface((int(cSize) * 2, int(cSize) * 2))
                surface.set_colorkey((0, 0, 0))
                pygame.draw.circle(surface, cColor, (int(cSize), int(cSize)), int(cSize))
                surface.set_alpha(cA)
                game['layers'][self.layer].blit(surface, (int(x + self.x - int(cSize) - game['scrollX']), int(y + self.y - int(cSize) - game['scrollY'])))


    def update(self, game:dict):
        """
        Args:
            game (dict): The game dict
        """

        self.draw(game)

        # Apply velocity
        self.x += self.x_vel * (game['frametime'] / 1000)
        self.y += self.y_vel * (game['frametime'] / 1000)

        # Check progress
        self.progress += game['frametime'] / (1000 * self.health)

        return self.progress <= 1
