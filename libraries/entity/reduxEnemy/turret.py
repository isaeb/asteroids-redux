import pygame
from math import cos, sin, atan2, sqrt, pi
from libraries.services.polygon import cartesianToPolar

from libraries.entity.projectile import EnemyBullet
from libraries.constants import *
from random import random


shape = [
        [(-0.75, -0.75), (0.75, -0.75), (0.75, 0.75), (-0.75, 0.75)],
        [(-0.5, 0.75), (-0.5, 1.5), (-0.25, 1.5), (-0.25, 0.75)],
        [(0.5, 0.75), (0.5, 1.5), (0.25, 1.5), (0.25, 0.75)]
        ]
shape = [[cartesianToPolar(point[0], point[1]) for point in part] for part in shape]

hitboxShape = [(-0.75, -0.75), (0.75, -0.75), (0.75, 0.75), (0.5, 0.75), (0.5, 1.5), (0.25, 1.5), (0.25, 0.75), (-0.25, 0.75), (-0.25, 1.5), (-0.5, 1.5), (-0.5, 0.75), (-0.75, 0.75)]
hitboxShape = [cartesianToPolar(point[0], point[1]) for point in hitboxShape]

class Turret:
    """
    Class for turret
    """
    def __init__(self, x:float, y:float, size:float):
        self.x = x
        self.y = y
        self.size = size
        self.points = shape
        self.health = 3
        self.angle = random() * pi * 2
        self.updatePosition()
        self.state = 0
        self.substate = 0
        self.cooldown = 0
        self.ammo = 3
        self.projectileSpeed = 180

        self.angleRange = pi * 0.2
        self.startAngle = self.angle
        self.rotateDirection = True
        self.targetAngle = self.angle

        # Set the value
        self.value = 30

    def update(self, game:dict):

        match self.state:
            case 0: # Targeting
                if len(game['players']) > 0:

                    # Update Angle
                    rotationSpeed = 2
                    player = game['players'][0]
                    activeRange = 150

                    playerX = player.x
                    playerY = player.y

                    # Adjust player coordinates
                    if playerX - self.x > game['gameWidth'] - activeRange:
                        playerX -= game['gameWidth']
                    elif playerX - self.x < activeRange - game['gameWidth']:
                        playerX += game['gameWidth']

                    if playerY - self.y > game['gameHeight'] - activeRange:
                        playerY -= game['gameHeight']
                    elif playerY - self.y < activeRange - game['gameHeight']:
                        playerY += game['gameHeight']

                    # Update substate
                    if sqrt(abs(self.x - playerX) ** 2 + abs(self.y - playerY) ** 2) < activeRange:
                        self.startAngle = self.angle

                        self.targetAngle = atan2(playerY - self.y, playerX - self.x) + pi * 1.5
                        self.angle += sin(self.targetAngle - self.angle) * rotationSpeed * game['frametime'] / 1000
                        self.substate += game['frametime'] / 1000
                        if self.substate >= 1.5 and abs((self.angle + pi * 2) % (pi * 2) - (self.targetAngle + pi * 2) % (pi * 2)) < pi * 0.08:
                            self.state = 1
                            self.ammo = 4
                            self.cooldown = 0.25
                    else:
                        self.angle += sin(self.targetAngle - self.angle) * rotationSpeed * game['frametime'] / 1000
                        if abs((self.angle + pi * 2) % (pi * 2) - (self.targetAngle + pi * 2) % (pi * 2)) < 0.1:
                            if self.rotateDirection:
                                self.targetAngle += pi * 0.5
                            else:
                                self.targetAngle -= pi * 0.5

                            self.rotateDirection = not self.rotateDirection
            
            case 1: # Firing
                if self.cooldown > 0:
                    self.cooldown -= game['frametime'] / 1000
                else:
                    if self.ammo > 0:
                        self.createProjectile(game)
                        self.cooldown = 0.25
                        self.ammo -= 1
                    else:
                        self.state = 0
                        self.substate = 0

        self.updatePosition()
        self.draw(game)
        return self.health > 0

    def updatePosition(self):
        # Update the position
        self.points = [[(self.x + self.size * point[1] * cos(point[0] + self.angle), self.y + self.size * point[1] * sin(point[0] + self.angle)) for point in part] for part in shape]
        self.hitbox = [(self.x + self.size * point[1] * cos(point[0] + self.angle), self.y + self.size * point[1] * sin(point[0] + self.angle)) for point in hitboxShape]
        
    def createProjectile(self, game:dict):

        if len(game['players']) == 0:
            return
        
        px = self.x
        py = self.y

        points = [(0.325, 1.5), (-0.325, 1.5)]
        points = [cartesianToPolar(point[0], point[1]) for point in points]
        points = [(self.size * point[1] * cos(point[0] + self.angle), self.size * point[1] * sin(point[0] + self.angle)) for point in points]

        for point in points:
            game['enemyBullets'].append(EnemyBullet(px + point[0], py + point[1], self.angle + pi * 0.5, self.angle + pi * 0.5, self.projectileSpeed, BULLET_SIZE * 0.8, damage = 0.25))

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
        if self.y + self.size * 1.5 + scrollOffsetY > game['gameHeight']:
            drawY.append(-game['gameHeight'])

        # draw at y + gameHeight
        if self.y - self.size * 1.5 + scrollOffsetY < 0:
            drawY.append(game['gameHeight'])

        # draw ship at x - gameWidth
        if self.x + self.size * 1.5 + scrollOffsetX > game['gameWidth']:
            drawX.append(-game['gameWidth'])

        # draw ship at x + gameWidth
        if self.x - self.size * 1.5 + scrollOffsetX < 0:
            drawX.append(game['gameWidth'])

        # draw self
        for x in drawX:
            for y in drawY:
                for index in range(len(self.points)):
                    p = [(point[0] + x - 1 + scrollOffsetX, point[1] + y - 1 + scrollOffsetY) for point in self.points[index]]
                    # offset by 1 pixel to account for anti aliasing
                    pygame.draw.polygon(game['layers'][0], pygame.Color(0, 0, 0, 255), p)
                    pygame.draw.aalines(game['layers'][0], pygame.Color(255, 0, 0, 255), True, p)
                pygame.draw.circle(game['layers'][0], pygame.Color(255, 0, 0, 255), (self.x + scrollOffsetX + x, self.y + scrollOffsetY + y), self.size * 0.5, 1)
