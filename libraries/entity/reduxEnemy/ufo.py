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

    def __init__(self, x:float, y:float, size:float, speed:float, health:int=1, waitTime:float=2.0, fireTime:float=4.0):
        """
        Args:
            x (float): x position
            y (float): y position
            size (float): size
            speed (float): speed
            health (int): health
        """

        # Set Variables
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.health = health
        self.waitTime = waitTime
        self.fireTime = fireTime

        self.state = 0
        self.substate = 0
        self.projectileSpeed = 160
        self.aggro = False
        self.fireClock = random.random() * fireTime

        # Set up Points
        self.points = shape
        self.hitbox = hitboxShape
        self.updatePosition()
        
        self.xTarget = self.x
        self.yTarget = self.y

        self.value = 30

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

        # draw ship at x - gameWidth
        if self.x + self.size + scrollOffsetX > game['gameWidth']:
            drawX.append(-game['gameWidth'])

        # draw ship at x + gameWidth
        if self.x - self.size + scrollOffsetX < 0:
            drawX.append(game['gameWidth'])

        # draw self
        for x in drawX:
            for y in drawY:
                for index in range(len(self.points)):
                    p = [(point[0] + x + scrollOffsetX, point[1] + y + scrollOffsetY) for point in self.points[index]]
                    pygame.draw.polygon(game['layers'][2], pygame.Color(0, 0, 0, 255), p)
                    pygame.draw.aalines(game['layers'][2], pygame.Color(255, 0, 0, 255), True, p)

    def updateAggro(self, game):
        # No player
        if len(game['players']) == 0:
            self.aggro = False
            return
        
        # Check distance to player
        player = game['players'][0]
        vision = game['screenWidth'] * 0.35
        for x in (-game['gameWidth'], 0, game['gameWidth']):
            for y in (-game['gameHeight'], 0, game['gameHeight']):
                if math.sqrt(abs(self.x + x - player.x) ** 2 + abs(self.y + y - player.y) ** 2) < vision:
                    self.aggro = True
                    return
        self.aggro = False

    def updateFire(self, game):
        if self.aggro:
            self.fireClock += game['frametime'] / 1000
            if self.fireClock >= self.fireTime:
                self.fireClock = 0
                self.createProjectile(game)

    def createProjectile(self, game:dict):

        if len(game['players']) == 0:
            return
        
        px = self.x
        py = self.y

        targetPlayer = game['players'][0]

        deltaX = targetPlayer.x - px
        deltaY = targetPlayer.y - py
        deltaAngle = math.atan2(deltaY, deltaX)

        game['enemyBullets'].append(EnemyBullet(px, py, deltaAngle, deltaAngle, self.projectileSpeed, constants.BULLET_SIZE, damage=0.7))

    def newTarget(self, game:dict):
        self.xTarget = random.random() * (game['screenWidth'] - self.size * 2) + self.size
        self.yTarget = random.random() * (game['screenHeight'] - self.size * 2) + self.size

    def updatePosition(self, game:dict={}):
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

        # Update the position and hitbox of the ufo
        self.points = [[(point[0] * self.size + self.x, point[1] * self.size + self.y) for point in part] for part in shape]
        self.hitbox = [(point[0] * self.size + self.x, point[1] * self.size + self.y) for point in hitboxShape]
        return True

    def update(self, game:dict):
        """
        Args:
            game (dict): The game dict
        """

        # Update aggro
        self.updateAggro(game)

        # Fire
        self.updateFire(game)

        match self.state:
            # Move to target
            case 0:
                self.updatePosition(game)
            
            # Wait
            case 1:
                self.substate += game['frametime'] / 1000
                if self.substate >= self.waitTime:
                    self.substate = 0
                    self.state = 0
                    self.newTarget(game)
            
        self.draw(game)

        return self.health > 0
