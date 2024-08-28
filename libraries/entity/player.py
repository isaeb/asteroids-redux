"""
Module providing a class for the player character
"""
import pygame
import math
import random

import libraries.services.polygon as polygon
import libraries.services.effects as effects

from libraries.entity.projectile import Bullet
from libraries.entity.particle import Particle
from libraries.entity.shipPart import Line
from libraries.constants import *

import json


playerShape = [(0, 1), (math.pi * 0.75, 1), (math.pi, 0.25), (math.pi * 1.25, 1)]

class Player:
    """
    Class for the player character
    """
    def __init__(self, x:float, y:float, angle:float, size:float):
        """
        Args:
            x (float): x position
            y (float): y position
            angle (float): angle position
            size (float): size 
        """

        self.x = x
        self.y = y
        self.angle = angle
        self.size = size
        self.points = []

        # Movement
        self.rotation = 2
        self.acceleration = 60
        self.maxSpeed = 640
        self.friction = 0
        self.reverse = 0
        self.noAccelMulti = 1

        self.maxHealth = 1
        self.health = 1
        self.specialName = ''
        self.specialCharge = 0
        self.specialMaxCharge = 1

        self.enabled = True

        self.x_vel = 0
        self.y_vel = 0
        self.shooting = True
        self.progress = 0
        self.playerShape = playerShape

        self.maxBullets = MAX_BULLETS

        self.updatePosition()

        # Upgrade Variables

        # Afterburn
        self.afterburn = False
        self.afterburnBoost = 0
        self.afterburnMax = 0

        # Tactical Dash
        self.tacticalDash = False
        self.tacticalDashDistance = 60
        self.tacticalDashTime = 0.4

        # Evasion Mode
        self.evasionMode = False
        self.evasionModeCost = 0
        self.evasionModeMax = 0
        self.evasionModeRotation = 0
        self.evasionModeAcceleration = 0
        self.evasionModeFriction = 0
        self.manualEvasion = False

        # Initial Dash
        self.initialDash = False
        self.initialDashDistance = 0
        self.initialDashTime = 0
 
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
                p = [(point[0] + x - 1 + scrollOffsetX, point[1] + y - 1 + scrollOffsetY) for point in self.points]
                # offset by 1 pixel to account for anti aliasing
                pygame.draw.polygon(game['layers'][2], pygame.Color(0, 0, 0, 255), p)
                pygame.draw.aalines(game['layers'][2], pygame.Color(255, 255, 255, 255), True, p)

    def updatePosition(self, game:dict={}):
        if game != {}:
            # Apply velocity
            self.x = (self.x + self.x_vel * (game['frametime'] / 1000)) % game['gameWidth']
            self.y = (self.y + self.y_vel * (game['frametime'] / 1000)) % game['gameHeight']

        # Update the position of the player
        self.points = [(self.x + math.cos(point[0] + self.angle) * self.size * point[1],
                        self.y + math.sin(point[0] + self.angle) * self.size * point[1])
                        for point in playerShape]

    def checkAsteroidCollision(self, game:dict):
        for n, asteroid in enumerate(game['asteroids']):
            if polygon.colliding(asteroid.points, self.points):
                self.health -= 1
                return n
            if asteroid.y + asteroid.size > game['gameHeight']:
                if polygon.colliding(asteroid.points, [(point[0], point[1] + game['gameHeight']) for point in self.points]):
                    self.health -= 1
                    return n
            if asteroid.y - asteroid.size < 0:
                if polygon.colliding(asteroid.points, [(point[0], point[1] - game['gameHeight']) for point in self.points]):
                    self.health -= 1
                    return n
            if asteroid.x + asteroid.size > game['gameWidth']:
                if polygon.colliding(asteroid.points, [(point[0] + game['gameWidth'], point[1]) for point in self.points]):
                    self.health -= 1
                    return n
            if asteroid.x - asteroid.size < 0:
                if polygon.colliding(asteroid.points, [(point[0] - game['gameWidth'], point[1]) for point in self.points]):
                    self.health -= 1
                    return n
        return None
    
    def checkProjectileCollision(self, game:dict):
        for n, bullet in enumerate(game['enemyBullets']):
            if polygon.colliding(bullet.points, self.points):
                self.health -= bullet.damage
                return n
            if bullet.y + bullet.size > game['gameHeight']:
                if polygon.colliding(bullet.points, [(point[0], point[1] + game['gameHeight']) for point in self.points]):
                    self.health -= bullet.damage
                    return n
            if bullet.y - bullet.size < 0:
                if polygon.colliding(bullet.points, [(point[0], point[1] - game['gameHeight']) for point in self.points]):
                    self.health -= bullet.damage
                    return n
            if bullet.x + bullet.size > game['gameWidth']:
                if polygon.colliding(bullet.points, [(point[0] + game['gameWidth'], point[1]) for point in self.points]):
                    self.health -= bullet.damage
                    return n
            if bullet.x - bullet.size < 0:
                if polygon.colliding(bullet.points, [(point[0] - game['gameWidth'], point[1]) for point in self.points]):
                    self.health -= bullet.damage
                    return n
        return None
    
    def checkEnemyCollision(self, game:dict):
        for n, enemy in enumerate(game['enemies']):
            if polygon.colliding(enemy.hitbox, self.points):
                self.health -= 1
                return n
            if enemy.y + enemy.size > game['gameHeight']:
                if polygon.colliding(enemy.hitbox, [(point[0], point[1] + game['gameHeight']) for point in self.points]):
                    self.health -= 1
                    return n
            if enemy.y - enemy.size < 0:
                if polygon.colliding(enemy.hitbox, [(point[0], point[1] - game['gameHeight']) for point in self.points]):
                    self.health -= 1
                    return n
            if enemy.x + enemy.size > game['gameWidth']:
                if polygon.colliding(enemy.hitbox, [(point[0] + game['gameWidth'], point[1]) for point in self.points]):
                    self.health -= 1
                    return n
            if enemy.x - enemy.size < 0:
                if polygon.colliding(enemy.hitbox, [(point[0] - game['gameWidth'], point[1]) for point in self.points]):
                    self.health -= 1
                    return n
        return None

    def createDeathEffect(self, game:dict):
        effects.createExplosion(self.x, self.y, game)
        for i in range(len(self.points)):
            point0 = self.points[i]
            point1 = self.points[(i + 1) % len(self.points)]
            angle = math.atan2(point0[1] + point1[1], point0[0] + point1[0]) + random.random() * math.pi - math.pi / 2
            magnitude = (math.sqrt((self.x - point0[0]) ** 2 + (self.y - point0[1]) ** 2) + math.sqrt((self.x - point1[0]) ** 2 + (self.y - point1[1]) ** 2)) / 2
            xVel = math.cos(angle) * magnitude * 5
            yVel = math.sin(angle) * magnitude * 5
            game['shipParts'].append(Line(point0[0], point0[1], point1[0], point1[1], xVel, yVel, pygame.Color(255, 255, 255), health=2, layer=2))
            
    def updateCollisions(self, game:dict):
        n = self.checkAsteroidCollision(game)
        if n is not None:
            game['asteroids'][n].health -= 1
            return True
        
        n = self.checkProjectileCollision(game)
        if n is not None:
            game['enemyBullets'][n].health -= 1
            return True
        
        n = self.checkEnemyCollision(game)
        if n is not None:
            game['enemies'][n].health -= 1
            return True

        return False

    def updateControl(self, game:dict):
        # Get player input
        keys = pygame.key.get_pressed()

        # Read player input
        if keys[pygame.K_SPACE] and not self.shooting:
            self.shooting = True
            if len(game['bullets']) < self.maxBullets:
                bXVel = self.x_vel + math.cos(self.angle) * BULLET_SPEED
                bYVel = self.y_vel + math.sin(self.angle) * BULLET_SPEED
                bAngle = math.atan2(bYVel, bXVel)
                bMagnitude = max(BULLET_SPEED, math.sqrt(bXVel ** 2 + bYVel ** 2))
                game['bullets'].append(Bullet(self.x + math.cos(self.angle) * self.size * BULLET_SIZE / 2,
                                            self.y + math.sin(self.angle) * self.size * BULLET_SIZE / 2,
                                            self.angle,
                                            bAngle,
                                            bMagnitude,
                                            BULLET_SIZE))
        elif not keys[pygame.K_SPACE]:
            self.shooting = False
            
        if keys[pygame.K_LEFT]:
            self.angle -= self.rotation * (game['frametime'] / 1000)

        if keys[pygame.K_RIGHT]:
            self.angle += self.rotation * (game['frametime'] / 1000)

        if keys[pygame.K_UP]:
            
            self.x_vel += math.cos(self.angle) * (game['frametime'] / 1000) * self.acceleration
            self.y_vel += math.sin(self.angle) * (game['frametime'] / 1000) * self.acceleration

            vectorMagnitude = math.sqrt(self.x_vel ** 2 + self.y_vel ** 2)
            
            if vectorMagnitude > self.maxSpeed:
                scaleFactor = self.maxSpeed / vectorMagnitude
                self.x_vel *= scaleFactor
                self.y_vel *= scaleFactor

            # Check progress
            self.progress += game['frametime'] / 1000

            while self.progress > 1 / THRUST_PARTICLES:
                self.progress -= 1 / THRUST_PARTICLES

                # Spawn flame particles
                pMagnitude = 150
                pVelX = self.x_vel + math.cos(self.angle + math.pi) * pMagnitude
                pVelY = self.y_vel + math.sin(self.angle + math.pi) * pMagnitude

                pX = self.x + math.cos(self.angle + math.pi) * 0.25 * self.size * 1.1
                pY = self.y + math.sin(self.angle + math.pi) * 0.25 * self.size * 1.1
                game['particles'].append(Particle(pX, pY, pVelX, pVelY, 4, 0, pygame.Color(255, 255, 0, 255), pygame.Color(255, 0, 0, 100), 0.1, layer=1))

        else:
            vectorMagnitude = math.sqrt(self.x_vel ** 2 + self.y_vel ** 2)
            
            if vectorMagnitude > self.maxSpeed * self.noAccelMulti:
                scaleFactor = self.maxSpeed * self.noAccelMulti / vectorMagnitude
                self.x_vel *= scaleFactor
                self.y_vel *= scaleFactor

            # Apply Friction
            angle = math.atan2(self.y_vel, self.x_vel)
            self.x_vel -= math.cos(angle) * self.friction * game['frametime'] / 1000
            self.y_vel -= math.sin(angle) * self.friction * game['frametime'] / 1000

            self.progress = 0

        if keys[pygame.K_DOWN]:
            self.x_vel -= math.cos(self.angle) * (game['frametime'] / 1000) * (self.reverse + self.friction)
            self.y_vel -= math.sin(self.angle) * (game['frametime'] / 1000) * (self.reverse + self.friction)

            vectorMagnitude = math.sqrt(self.x_vel ** 2 + self.y_vel ** 2)
            
            if vectorMagnitude > self.maxSpeed:
                scaleFactor = self.maxSpeed / vectorMagnitude
                self.x_vel *= scaleFactor
                self.y_vel *= scaleFactor

    def update(self, game:dict):
        """
        Args:
            game (dict): The game dict
        """

        if self.enabled:
            self.draw(game)
            self.updateControl(game)
            self.updatePosition(game)
        
        # Test for collisions
        if self.updateCollisions(game):
            effects.createExplosion(self.x, self.y, game)
        
        if self.enabled and self.health <= 0:
            self.createDeathEffect(game)
            return False
        return True

    def disable(self):
        self.enabled = False
    
    def enable(self):
        self.enabled = True

    def applyUpgrade(self, script):
        script = script.split(';')
        for line in script:
            print(f'Applying change: {line}')
            line = line.split(' ')

            var = line[1]
            value = line[2]
            
            match line[0]:
                case 'set':
                    operator = ' = '
                case 'multiply':
                    operator = ' *= '
                case 'add':
                    operator = ' += '
            
            exec(f'self.{var} {operator} {value}')

    def updateStats(self, game:dict):
        match game['class']:
            case 'scout':
                self.acceleration = 140
                self.maxSpeed = 160
                self.rotation = 3
                self.friction = 100
                self.maxHealth = 2
                self.health = 2
                self.specialName = 'TELEPORT'
                self.noAccelMulti = 0.7

        # Opening JSON file
        with open('libraries/upgrades.json') as json_file:
            upgradeDict = json.load(json_file)

        # Upgrade Self
        for category in ['movement', 'weapons', 'special', 'auxiliary']:
            tempDict = upgradeDict[game['class']]['upgrades'][category]
            newFeature = tempDict['newFeature']
            
            level = game[category]
            for l in range(level):
                # Apply a new feature
                if (l + 1) in newFeature:

                    # Iterate
                    index = newFeature.index(l + 1)
                    if index > 0:
                        tempDict = tempDict['children']
                    else:
                        tempDict = tempDict['features']
                    tempDict = tempDict[game[f'{category}Features'][index]]

                    self.applyUpgrade(tempDict['function'])
                
                # Apply a default upgrade
                else:
                    self.applyUpgrade(tempDict['defaultFunction'])
                
                level -= 1
