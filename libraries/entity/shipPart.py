"""
Module providing a class for lines
"""

import pygame

from pygame import gfxdraw

class Line:
    """
    Class for particles
    """
    def __init__(self, xStart:float, yStart:float, xEnd:float, yEnd:float, x_vel:float, y_vel:float, color:pygame.Color, health:float, layer=0):

        self.xStart = xStart
        self.yStart = yStart
        self.xEnd = xEnd
        self.yEnd = yEnd
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.health = health
        self.progress = 0
        self.layer = layer
        self.color = color


    def draw(self, game:dict):
        """
        Args:
            game (dict): The game dict
        """
        scrollOffsetX = - game['scrollX']
        scrollOffsetY = - game['scrollY']
        
        self.color.a = int(255 - self.progress * 255)
        pygame.draw.line(game['layers'][self.layer], self.color, 
                         (int(self.xStart + scrollOffsetX), int(self.yStart + scrollOffsetY)), 
                         (int(self.xEnd + scrollOffsetX), int(self.yEnd + scrollOffsetY)))


    def update(self, game:dict):
        """
        Args:
            game (dict): The game dict
        """

        self.draw(game)

        # Apply velocity
        self.xStart += self.x_vel * (game['frametime'] / 1000)
        self.xEnd += self.x_vel * (game['frametime'] / 1000)
        self.yStart += self.y_vel * (game['frametime'] / 1000)
        self.yEnd += self.y_vel * (game['frametime'] / 1000)

        # Check progress
        self.progress += game['frametime'] / (1000 * self.health)

        return self.progress <= 1
