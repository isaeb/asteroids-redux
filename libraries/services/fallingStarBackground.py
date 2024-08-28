import pygame

from random import random
from math import pi, sin

class FallingStarBackground:
    def __init__(self, size2D:tuple=(640, 480), stars=300, depth=2000):
        self.width, self.height = size2D
        self.depth = depth

        self.fov = pi
        self.endWidth = self.width + 2 * (depth / sin(self.fov / 2))
        self.endHeight = self.height + 2 * (depth / sin(self.fov / 2))

        self.stars = []
        for _ in range(stars):
            position3D = (random() * self.endWidth, random() * self.endHeight, random() * depth)
            velocity3D = (0, 0, -500)
            self.stars.append(Star(position3D, velocity3D))

    def update(self, game:dict):
        for star in self.stars:
            star.update(game)
            if star.getPosition()[2] < 0:
                position3D = (random() * self.endWidth, random() * self.endHeight, star.getPosition()[2] + self.depth)
                star.setPosition(position3D)

    def draw(self, surf, game:dict):
        for star in self.stars:
            starX, starY, starZ = star.getPosition()
            endWidth = self.width + 2 * (starZ / sin(self.fov / 2))
            endHeight = self.height + 2 * (starZ / sin(self.fov / 2))

            drawX = starX - (self.endWidth - endWidth) / 2  # Account for offset
            drawX *= game['screenWidth'] / endWidth         # Account for screen size

            drawY = starY - (self.endHeight - endHeight) / 2  # Account for offset
            drawY *= game['screenWidth'] / endHeight          # Account for screen size

            alpha = max(0, min(1, (starZ / self.depth) * 5, 5 - (starZ / self.depth) * 5))
            color = (int(200 * alpha), int(200 * alpha), int(200 * alpha))
            pygame.draw.circle(surf, color, (drawX, drawY), 1)

class Star:
    def __init__(self, position3D:tuple, velocity3D:tuple):
        self.x, self.y, self.z = position3D
        self.velX, self.velY, self.velZ = velocity3D
    
    def update(self, game:dict):
        self.z += self.velZ * game['frametime'] / 1000

    def getPosition(self):
        return (self.x, self.y, self.z)
    
    def setPosition(self, position3D:tuple):
        self.x, self.y, self.z = position3D
    