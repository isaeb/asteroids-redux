"""
Module providing a class for the player character
"""
import math
import random
import pygame
import libraries.constants as constants

from libraries.entity.projectile import EnemyBullet


shape = [[(-1 / 3, -2 / 3), (1 / 3, -2 / 3), (1.5 / 3, -1 / 3), (-1.5 / 3, -1 / 3)],
        [(-1.5 / 3, -1 / 3), (1.5 / 3, -1 / 3), (3 / 3, 0 / 3), (-3 / 3, 0 / 3)],
        [(-1.5 / 3, 1 / 3), (1.5 / 3, 1 / 3), (3 / 3, 0 / 3), (-3 / 3, 0 / 3)]]

hitboxShape = [(-1 / 3, -2 / 3), (1 / 3, -2 / 3), (1.5 / 3, -1 / 3), (3 / 3, 0 / 3), (1.5 / 3, 1 / 3), (-1.5 / 3, 1 / 3), (-3 / 3, 0 / 3), (-1.5 / 3, -1 / 3)]

class UFO:
    """
    Class for the ufo
    """

    def __init__(self, x:float, y:float, xTarget:float, yTarget:float, size:float, speed:float, health:int=1, fireTime:float=5.0, leaveChance:float=0.3):
        """
        Args:
            x (float): x position
            y (float): y position
            xTarget (float): x target
            yTarget (float): y target
            size (float): size
            speed (float): speed
            health (int): health
        """

        # Set Variables
        self.x = x
        self.y = y
        self.xTarget = xTarget
        self.yTarget = yTarget
        self.size = size
        self.speed = speed
        self.health = health
        self.fireTime = fireTime
        self.leaveChance = leaveChance
        self.state = 0
        self.substate = 0
        self.projectileSpeed = 160

        # Set up Points
        self.points = shape
        self.hitbox = hitboxShape
        self.updatePosition()

    def draw(self, game:dict):
        """
        Args:
            game (dict): The game dict
        """
        
        for index in range(len(self.points)):
            p = [(point[0], point[1]) for point in self.points[index]]
            pygame.draw.polygon(game['layers'][2], pygame.Color(0, 0, 0, 255), p)
            pygame.draw.aalines(game['layers'][2], pygame.Color(255, 255, 255, 255), True, p)

    def createProjectile(self, game:dict):

        if len(game['players']) == 0:
            return
        
        px = self.x
        py = self.y

        targetPlayer = game['players'][0]

        deltaX = targetPlayer.x - px
        deltaY = targetPlayer.y - py
        deltaAngle = math.atan2(deltaY, deltaX)

        game['enemyBullets'].append(EnemyBullet(px, py, deltaAngle, deltaAngle, self.projectileSpeed, constants.BULLET_SIZE))

    def newTarget(self, game:dict, leaving=False):
        if leaving:
            angle = random.random() * math.pi * 2
            self.xTarget = game['screenWidth'] / 2 + math.cos(angle) * game['screenWidth']
            self.yTarget = game['screenHeight'] / 2 + math.sin(angle) * game['screenWidth']
            return
        
        self.xTarget = random.random() * (game['screenWidth'] - self.size * 2) + self.size
        self.yTarget = random.random() * (game['screenHeight'] - self.size * 2) + self.size

    def updateFire(self, game:dict):
        sProgress = self.progress
        self.progress += (game['frametime'] / 1000)

        # Check if self should fire
        if sProgress < 0.5 * self.fireTime and self.progress > 0.5 * self.fireTime:
            self.createProjectile(game)
        
        # Check if state should change
        if self.progress > self.fireTime:
            if random.random() > self.leaveChance:
                self.state = 0
                self.newTarget(game)
            else:
                self.state = 2
                self.newTarget(game, leaving=True)

    def updatePosition(self, game:dict={}, leaving=False):
        if game != {}:
            # Create movement vector
            deltaX = self.xTarget - self.x
            deltaY = self.yTarget - self.y
            deltaAngle = math.atan2(deltaY, deltaX)
            deltaMagnitude = math.sqrt(deltaX ** 2 + deltaY ** 2)

            # Move to target
            if deltaMagnitude > self.speed * (game['frametime'] / 1000):
                self.x += math.cos(deltaAngle) * self.speed * (game['frametime'] / 1000)
                self.y += math.sin(deltaAngle) * self.speed * (game['frametime'] / 1000)
            
            # Teleport to target and change state
            else:
                self.x = self.xTarget
                self.y = self.yTarget
                self.state = 1
                self.progress = 0
            
            if leaving:
                if self.x < -self.size or self.x > game['screenWidth'] + self.size or self.y < -self.size or self.y > game['screenHeight'] + self.size:
                    return False

        # Update the position and hitbox of the ufo
        self.points = [[(point[0] * self.size + self.x, point[1] * self.size + self.y) for point in part] for part in shape]
        self.hitbox = [(point[0] * self.size + self.x, point[1] * self.size + self.y) for point in hitboxShape]
        return True

    def update(self, game:dict):
        """
        Args:
            game (dict): The game dict
        """

        match self.state:
            # Move to target
            case 0:
                self.updatePosition(game, leaving=False)
            
            # Fire at player
            case 1:
                self.updateFire(game)

            # Leave game area
            case 2:
                if not self.updatePosition(game, leaving=True):
                    return False
            
        self.draw(game)

        return self.health > 0
