"""
Module providing a class for the player character
"""
import pygame
import math
import numpy
import random
import libraries.services.polygon as polygon


class Asteroid:
    """
    Class for the player character
    """

    def __init__(self, x:float, y:float, x_vel:float, y_vel:float, angle_vel:float, size:float, health:int=2, shape:list=[], color=(0, 0, 0)):
        """
        Args:
            x (float): x position
            y (float): y position
            x_vel (float): horizontal velocity
            y_vel (float): vertical velocity
            angle_vel (float): angle velocity
            size (float): size
        """

        self.x = x
        self.y = y
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.size = size
        self.angle = 0
        self.angle_vel = angle_vel
        self.health = health
        self.stage = health
        self.color = color
        if len(shape) == 0:
            self.shape = randomShape()
        else:
            self.shape = shape
        self.updatePosition()

    def draw(self, game:dict):
        """
        Args:
            game (dict): The game dict
        """

        scrollOffsetX = - game['scrollX']
        scrollOffsetY = - game['scrollY']
        
        drawX = [0]
        drawY = [0]
        
        # draw at y - gameHeight
        if self.y + self.size + scrollOffsetY > game['gameHeight']:
            drawY.append(-game['gameHeight'])

        # draw at y + gameHeight
        if self.y - self.size + scrollOffsetY < 0:
            drawY.append(game['gameHeight'])

        # draw ship at x - screenWidth
        if self.x + self.size + scrollOffsetX > game['gameWidth']:
            drawX.append(-game['gameWidth'])

        # draw ship at x + screenWidth
        if self.x - self.size + scrollOffsetX < 0:
            drawX.append(game['gameWidth'])

        # draw self
        for x in drawX:
            for y in drawY:
                p = [(point[0] + x + scrollOffsetX, point[1] + y + scrollOffsetY) for point in self.points]
                pygame.draw.polygon(game['layers'][2], self.color, p)
                pygame.draw.aalines(game['layers'][2], pygame.Color(255, 255, 255, 255), True, p)

    def updatePosition(self, game:dict={}):
        if game != {}:
            # Apply velocity
            self.x = (self.x + self.x_vel * (game['frametime'] / 1000)) % game['gameWidth']
            self.y = (self.y + self.y_vel * (game['frametime'] / 1000)) % game['gameHeight']
            self.angle = (self.angle + self.angle_vel * (game['frametime'] / 1000)) % (math.pi * 2)

        # Update the position of the asteroid
        self.points = [(self.x + math.cos(point[0] + self.angle) * self.size * point[1],
                        self.y + math.sin(point[0] + self.angle) * self.size * point[1])
                        for point in self.shape]

    def spawnChildren(self, game):
        for _ in range(2):
            aVelX = random.random() * 100 - 50
            aVelY = random.random() * 100 - 50
            newSize = self.size * 0.5
            game['asteroids'].append(Asteroid(self.x + aVelX / 2, self.y + aVelY / 2, aVelX, aVelY, random.random() * math.pi - math.pi / 2, newSize, health=self.health, color=self.color))

    def update(self, game:dict):
        """
        Args:
            game (dict): The game dict
        """

        self.updatePosition(game)

        self.draw(game)

        # Destroy Self
        if self.health <= 0:
            return False
        elif self.health <= self.stage - 1:
            self.spawnChildren(game)
            self.stage -= 1
            return False

        return True


def centerShape(shape:list):
 
    # Convert vectors to cartesian
    points = [polygon.polarToCartesian(vec[0], vec[1]) for vec in shape]

    # Find the center of mass
    center = polygon.polygonCentroid(points)

    # Augment the cartesian vectors
    points = [(point[0] - center[0], point[1] - center[1]) for point in points]

    # Convert back to polar
    shape = [polygon.cartesianToPolar(point[0], point[1]) for point in points]

    # Normalize points so that size remains consistent
    mSize = 0
    for vec in shape:
        mSize = max(mSize, vec[1])
    shape = [(vec[0], vec[1] / mSize) for vec in shape]

    return shape

def randomShape(pointCount:int=30, magnitude:int=1):
    """
    Args:
        the number of points in the random shape
    """

    # Define variables
    shape = []
    m = magnitude
    a = 0

    # Generate a sorted list of angles
    angles = sorted(numpy.random.uniform(0, math.pi * 2, pointCount))

    # Assign varying magnitudes to each point
    for angle in angles:
        maxDiff = (angle - a) / 5
        newM = max(0.5, m - maxDiff, min(1, m + maxDiff, random.random()))
        m = newM
        shape.append((angle, newM))
        a = angle
    
    # Make magnitude of last point average of adjacent points
    shape[pointCount - 1] = shape[pointCount - 1][0], (shape[pointCount - 2][1] + shape[0][1]) / 2

    return centerShape(shape)