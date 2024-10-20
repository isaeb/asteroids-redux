"""
Module providing a class for the player character
"""
import pygame
import math

import libraries.services.polygon as polygon
import libraries.services.effects as effects

from libraries.entity.projectile import Bullet
from libraries.entity.particle import Particle
from libraries.entity.shipPart import Line
from libraries.constants import *
from libraries.services.specialFunctions import *
from libraries.services.polygon import cartesianToPolar

from random import random

import json


lastPressed = {'keyFire': 0, 'keySpecial': 0, 'keyUp': 0, 'keyDown': 0, 'keyLeft': 0, 'keyRight': 0}
doubleTapRange = 0.11

scoutShape = [
    [(0, 8), (4, 0), (8, 8), (4, 6)],
    [(3, 3), (4, 1), (5, 3), (4, 4)]
    ]
scoutShape = [[((point[0] - 4) / 6, (point[1] - 4) / 6) for point in part] for part in scoutShape] # Scale
scoutShape = [[cartesianToPolar(point[0], point[1]) for point in part] for part in scoutShape] # C2P
scoutShape = [[(point[0] + math.pi * 0.5, point[1]) for point in part] for part in scoutShape] # Rotate

scoutHitbox = [(0, 8), (4, 0), (8, 8), (4, 6)]
scoutHitbox = [((point[0] - 4) / 6, (point[1] - 4) / 6) for point in scoutHitbox] # Scale
scoutHitbox = [cartesianToPolar(point[0], point[1]) for point in scoutHitbox] # C2P
scoutHitbox = [(point[0] + math.pi * 0.5, point[1]) for point in scoutHitbox] # Rotate

bomberShape = [
    [(0, 8), (4, 3), (4, 2), (6, 0), (8, 2), (8, 3), (12, 8), (6, 7)],
    [(4, 2), (4, 5), (6, 7), (8, 5), (8, 2), (6, 0)],
    [(5, 1), (5, 2), (6, 3), (7, 2), (7, 1), (6, 0)],
    [(2, 3), (3, 3), (3, 6), (2.5, 7), (2, 6)],
    [(9, 3), (10, 3), (10, 6), (9.5, 7), (9, 6)]
    ]
bomberShape = [[((point[0] - 6) / 8, (point[1] - 4) / 6) for point in part] for part in bomberShape] # Scale
bomberShape = [[cartesianToPolar(point[0], point[1]) for point in part] for part in bomberShape] # C2P
bomberShape = [[(point[0] + math.pi * 0.5, point[1]) for point in part] for part in bomberShape] # Rotate

bomberHitbox = [(0, 8), (4, 3), (4, 2), (6, 0), (8, 2), (8, 3), (12, 8), (6, 7)]
bomberHitbox = [((point[0] - 4) / 6, (point[1] - 4) / 6) for point in bomberHitbox] # Scale
bomberHitbox = [cartesianToPolar(point[0], point[1]) for point in bomberHitbox] # C2P
bomberHitbox = [(point[0] + math.pi * 0.5, point[1]) for point in bomberHitbox] # Rotate

heavyShape = [
    [(2, 0), (0, 2), (0, 6), (2, 8)],
    [(6, 0), (8, 2), (8, 6), (6, 8)],
    [(2, 2), (1, 4), (2, 7), (3, 6), (5, 6), (6, 7), (7, 4), (6, 2), (5, 3), (4, 1), (3, 3)],
    [(3, 5), (5, 5), (4, 3)]
    ]
heavyShape = [[((point[0] - 4) / 6, (point[1] - 4) / 6) for point in part] for part in heavyShape] # Scale
heavyShape = [[cartesianToPolar(point[0], point[1]) for point in part] for part in heavyShape] # C2P
heavyShape = [[(point[0] + math.pi * 0.5, point[1]) for point in part] for part in heavyShape] # Rotate

heavyHitbox = [(2, 0), (0, 2), (0, 6), (2, 8), (2, 7), (3, 6), (5, 6), (6, 7), (6, 8), (8, 6), (8, 2), (6, 0), (6, 2), (5, 3), (4, 1), (3, 3), (2, 2)]
heavyHitbox = [((point[0] - 4) / 6, (point[1] - 4) / 6) for point in bomberHitbox] # Scale
heavyHitbox = [cartesianToPolar(point[0], point[1]) for point in bomberHitbox] # C2P
heavyHitbox = [(point[0] + math.pi * 0.5, point[1]) for point in bomberHitbox] # Rotate

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
        self.specialCharge = 1
        self.specialMaxCharge = 1
        self.specialCost = 1
        self.specialFunction = lambda: print('no special function assigned')
        self.specialState = False

        self.enabled = True

        self.x_vel = 0
        self.y_vel = 0
        self.shooting = True
        self.bulletDamage = 1
        self.bulletSpeed = BULLET_SPEED
        self.bulletSize = BULLET_SIZE
        self.bulletPierce = 0
        self.progress = 0

        self.playerShape = scoutShape
        self.hitbox = scoutHitbox

        self.maxBullets = MAX_BULLETS

        self.updatePosition()

        # Upgrade Variables

        # Scout Movement
        # Afterburn
        self.afterburn = False
        self.afterburnCharge = 999
        self.afterburnBoost = 0
        self.afterburnCost = 0
        self.afterburnMax = 0
        self.afterburnCooldown = 0
        self.afterburnMaxCooldown = 0

        # Evasion Mode
        self.evasionMode = False
        self.evasionModeActive = 0
        self.evasionModeDuration = 3
        self.evasionModeCharge = 10
        self.evasionModeCost = 10
        self.evasionModeMax = 10
        self.evasionModeRotation = 1.2
        self.evasionModeAcceleration = 3
        self.evasionModeFriction = 5
        self.manualEvasion = False

        # Initial Dash
        self.initialDash = False
        self.initialDashDistance = 100
        self.initialDashSpeed = 400

        # Tactical Dash
        self.tacticalDash = False
        self.tacticalDashDistance = 60
        self.tacticalDashSpeed = 240

        # Dashing (general)
        self.dashX = 0
        self.dashY = 0

        # Weapons
        # Auto-Fire
        self.autoFire = False
        self.autoFireRate = 5
        self.autoFireCooldown = 0

        # Spread-Fire
        self.spreadFireCount = 1
        self.spreadAngle = 0

        # Charge-Beams
        self.chargeBlast = False
        self.chargeTime = 0
        self.chargeBlastDamage = 1
        self.chargeBlastCount = 1
        self.chargeBlastSpread = 0
        self.chargeBlastSize = 1
        self.chargeBlastSpeed = BULLET_SPEED
        self.charge = 0

        # Lasers!
        self.laser = False

        # Drones
        self.droneCount = 0
        self.droneFireRate = 1
        self.droneDamage = 1
        self.droneBulletSpeed = BULLET_SPEED
        self.droneBulletSize = self.bulletSize * 0.5
        self.droneLaser = False
 
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
                    p = [(point[0] + x - 1 + scrollOffsetX, point[1] + y - 1 + scrollOffsetY) for point in self.points[index]]
                    # offset by 1 pixel to account for anti aliasing
                    pygame.draw.polygon(game['layers'][2], pygame.Color(0, 0, 0, 255), p)
                    pygame.draw.aalines(game['layers'][2], pygame.Color(255, 255, 255, 255), True, p)

    def updatePosition(self, game:dict={}):
        if game != {}:
            if abs(self.dashX) + abs(self.dashY) > 1:
                # Calculate Dash Velocity
                angle = math.atan2(self.dashY, self.dashX)
                if self.tacticalDash:
                    magnitude = self.tacticalDashSpeed
                elif self.initialDash:
                    magnitude = self.initialDashSpeed
                velX = math.cos(angle) * magnitude
                velY = math.sin(angle) * magnitude

                # Apply Dash Velocity
                self.x = (self.x + velX * (game['frametime'] / 1000)) % game['gameWidth']
                self.y = (self.y + velY * (game['frametime'] / 1000)) % game['gameHeight']

                # Adjust Dash Variables
                if abs(self.dashX) < abs(velX * (game['frametime'] / 1000)):
                    self.dashX = 0
                else:
                    self.dashX -= velX * (game['frametime'] / 1000)

                if abs(self.dashY) < abs(velY * (game['frametime'] / 1000)):
                    self.dashY = 0
                else:
                    self.dashY -= velY * (game['frametime'] / 1000)
            else:
                # Apply velocity
                self.x = (self.x + self.x_vel * (game['frametime'] / 1000)) % game['gameWidth']
                self.y = (self.y + self.y_vel * (game['frametime'] / 1000)) % game['gameHeight']
                
        # Update the position of the player
        self.points = [[(self.x + math.cos(point[0] + self.angle) * self.size * point[1],
                        self.y + math.sin(point[0] + self.angle) * self.size * point[1])
                        for point in part] for part in self.playerShape]
        
        self.hitboxPoints = [(self.x + math.cos(point[0] + self.angle) * self.size * point[1],
                        self.y + math.sin(point[0] + self.angle) * self.size * point[1])
                        for point in self.hitbox]

    def checkAsteroidCollision(self, game:dict):
        for n, asteroid in enumerate(game['asteroids']):
            if polygon.colliding(asteroid.points, self.hitboxPoints):
                self.health -= 1
                return n
            if asteroid.y + asteroid.size > game['gameHeight']:
                if polygon.colliding(asteroid.points, [(point[0], point[1] + game['gameHeight']) for point in self.hitboxPoints]):
                    self.health -= 1
                    return n
            if asteroid.y - asteroid.size < 0:
                if polygon.colliding(asteroid.points, [(point[0], point[1] - game['gameHeight']) for point in self.hitboxPoints]):
                    self.health -= 1
                    return n
            if asteroid.x + asteroid.size > game['gameWidth']:
                if polygon.colliding(asteroid.points, [(point[0] + game['gameWidth'], point[1]) for point in self.hitboxPoints]):
                    self.health -= 1
                    return n
            if asteroid.x - asteroid.size < 0:
                if polygon.colliding(asteroid.points, [(point[0] - game['gameWidth'], point[1]) for point in self.hitboxPoints]):
                    self.health -= 1
                    return n
        return None
    
    def checkProjectileCollision(self, game:dict):
        for n, bullet in enumerate(game['enemyBullets']):
            if polygon.colliding(bullet.points, self.hitboxPoints):
                self.health -= bullet.damage
                return n
            if bullet.y + bullet.size > game['gameHeight']:
                if polygon.colliding(bullet.points, [(point[0], point[1] + game['gameHeight']) for point in self.hitboxPoints]):
                    self.health -= bullet.damage
                    return n
            if bullet.y - bullet.size < 0:
                if polygon.colliding(bullet.points, [(point[0], point[1] - game['gameHeight']) for point in self.hitboxPoints]):
                    self.health -= bullet.damage
                    return n
            if bullet.x + bullet.size > game['gameWidth']:
                if polygon.colliding(bullet.points, [(point[0] + game['gameWidth'], point[1]) for point in self.hitboxPoints]):
                    self.health -= bullet.damage
                    return n
            if bullet.x - bullet.size < 0:
                if polygon.colliding(bullet.points, [(point[0] - game['gameWidth'], point[1]) for point in self.hitboxPoints]):
                    self.health -= bullet.damage
                    return n
        return None
    
    def checkEnemyCollision(self, game:dict):
        for n, enemy in enumerate(game['enemies']):
            if polygon.colliding(enemy.hitbox, self.hitboxPoints):
                self.health -= 1
                return n
            if enemy.y + enemy.size > game['gameHeight']:
                if polygon.colliding(enemy.hitbox, [(point[0], point[1] + game['gameHeight']) for point in self.hitboxPoints]):
                    self.health -= 1
                    return n
            if enemy.y - enemy.size < 0:
                if polygon.colliding(enemy.hitbox, [(point[0], point[1] - game['gameHeight']) for point in self.hitboxPoints]):
                    self.health -= 1
                    return n
            if enemy.x + enemy.size > game['gameWidth']:
                if polygon.colliding(enemy.hitbox, [(point[0] + game['gameWidth'], point[1]) for point in self.hitboxPoints]):
                    self.health -= 1
                    return n
            if enemy.x - enemy.size < 0:
                if polygon.colliding(enemy.hitbox, [(point[0] - game['gameWidth'], point[1]) for point in self.hitboxPoints]):
                    self.health -= 1
                    return n
        return None

    def createDeathEffect(self, game:dict):
        effects.createExplosion(self.x, self.y, game)
        for part in self.points:
            for i in range(len(part)):
                point0 = part[i]
                point1 = part[(i + 1) % len(part)]
                angle = math.atan2(point0[1] + point1[1], point0[0] + point1[0]) + random() * math.pi - math.pi / 2
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

        if self.manualEvasion and self.evasionModeActive == 0 and self.evasionModeCharge >= self.evasionModeCost:
            if any([keys[key] for key in (game['controls']['keyLeft'])]) and any([keys[key] for key in (game['controls']['keyRight'])]) and any([keys[key] for key in (game['controls']['keyUp'])]) and any([keys[key] for key in (game['controls']['keyDown'])]):
                print('manual evasion mode: active')
                self.evasionModeActive = self.evasionModeDuration
                self.evasionModeCharge -= self.evasionModeCost

        # Update last pressed
        if self.tacticalDash:
            for key in lastPressed.keys():
                if any([keys[v] for v in (game['controls'][key])]):
                    if lastPressed[key] > 0 and lastPressed[key] < doubleTapRange:
                        # Dash
                        match key:
                            case 'keyUp':
                                self.dashY = -self.tacticalDashDistance
                                self.y_vel = -self.tacticalDashSpeed * 0.5
                            case 'keyDown':
                                self.dashY = self.tacticalDashDistance
                                self.y_vel = self.tacticalDashSpeed * 0.5
                            case 'keyLeft':
                                self.dashX = -self.tacticalDashDistance
                                self.x_vel = -self.tacticalDashSpeed * 0.5
                            case 'keyRight':
                                self.dashX = self.tacticalDashDistance
                                self.x_vel = self.tacticalDashSpeed * 0.5

                        print(self.dashX, self.dashY)
                    lastPressed[key] = 0
                else:
                    lastPressed[key] += game['frametime'] / 1000
        elif self.initialDash:
            if any([keys[key] for key in (game['controls']['keyUp'])]):
                if lastPressed['keyUp'] > 0 and lastPressed['keyUp'] < doubleTapRange:
                    # Dash
                    self.dashX = math.cos(self.angle) * self.initialDashDistance
                    self.dashY = math.sin(self.angle) * self.initialDashDistance
                    self.x_vel = math.cos(self.angle) * self.initialDashSpeed
                    self.y_vel = math.sin(self.angle) * self.initialDashSpeed
                lastPressed['keyUp'] = 0
            else:
                lastPressed['keyUp'] += game['frametime'] / 1000

        # Read player input
        if self.autoFire:
            self.autoFireCooldown = max(0, self.autoFireCooldown - game['frametime'] / 1000)
            if any([keys[key] for key in game['controls']['keyFire']]) and self.autoFireCooldown == 0:
                self.autoFireCooldown = 1 / self.autoFireRate
                self.shoot(game)
        else:
            if any([keys[key] for key in game['controls']['keyFire']]) and not self.shooting:
                self.shooting = True
                self.shoot(game)
        
        if not any([keys[key] for key in game['controls']['keyFire']]):
            self.shooting = False
            if self.chargeBlast:
                self.charge = min(self.chargeTime, self.charge + game['frametime'] / 1000)

        if any([keys[key] for key in game['controls']['keySpecial']]) and not self.specialState:
            if self.specialCharge >= self.specialCost:
                self.specialCharge -= self.specialCost
                self.specialState = True
                self.specialFunction(game)
        elif not any([keys[key] for key in game['controls']['keySpecial']]):
            self.specialState = False
            
        if any([keys[key] for key in game['controls']['keyLeft']]):
            if self.evasionModeActive > 0:
                self.angle -= self.rotation * self.evasionModeRotation * (game['frametime'] / 1000)
            else:
                self.angle -= self.rotation * (game['frametime'] / 1000)

        if any([keys[key] for key in game['controls']['keyRight']]):
            if self.evasionModeActive > 0:
                self.angle += self.rotation * self.evasionModeRotation * (game['frametime'] / 1000)
            else:
                self.angle += self.rotation * (game['frametime'] / 1000)

        if any([keys[key] for key in game['controls']['keyUp']]):
            if self.afterburn and self.afterburnCharge > 0:
                self.x_vel += math.cos(self.angle) * (game['frametime'] / 1000) * self.acceleration * self.afterburnBoost
                self.y_vel += math.sin(self.angle) * (game['frametime'] / 1000) * self.acceleration * self.afterburnBoost
                self.afterburnCharge = max(0, self.afterburnCharge - self.afterburnCost * game['frametime'] / 1000)
                vectorMagnitude = math.sqrt(self.x_vel ** 2 + self.y_vel ** 2) / self.afterburnBoost
            elif self.evasionModeActive > 0:
                self.x_vel += math.cos(self.angle) * (game['frametime'] / 1000) * self.acceleration * self.evasionModeAcceleration
                self.y_vel += math.sin(self.angle) * (game['frametime'] / 1000) * self.acceleration * self.evasionModeAcceleration
                vectorMagnitude = math.sqrt(self.x_vel ** 2 + self.y_vel ** 2)
            else:
                self.x_vel += math.cos(self.angle) * (game['frametime'] / 1000) * self.acceleration
                self.y_vel += math.sin(self.angle) * (game['frametime'] / 1000) * self.acceleration
                vectorMagnitude = math.sqrt(self.x_vel ** 2 + self.y_vel ** 2)
            
            if vectorMagnitude > self.maxSpeed:
                scaleFactor = self.maxSpeed / vectorMagnitude
                self.x_vel *= scaleFactor
                self.y_vel *= scaleFactor

            # Check progress
            self.progress += game['frametime'] / 1000

            self.afterburnCooldown = self.afterburnMaxCooldown

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
            if self.afterburn:
                self.afterburnCooldown = max(0, self.afterburnCooldown - game['frametime'] / 1000)
                if self.afterburnCooldown <= 0:
                    self.afterburnCharge = min(self.afterburnMax, self.afterburnCharge + game['frametime'] / 1000)

            vectorMagnitude = math.sqrt(self.x_vel ** 2 + self.y_vel ** 2)
            
            if vectorMagnitude > self.maxSpeed * self.noAccelMulti:
                scaleFactor = self.maxSpeed * self.noAccelMulti / vectorMagnitude
                self.x_vel *= scaleFactor
                self.y_vel *= scaleFactor

            # Apply Friction
            angle = math.atan2(self.y_vel, self.x_vel)
            if self.evasionModeActive > 0:
                self.x_vel -= math.cos(angle) * self.friction * self.evasionModeFriction * game['frametime'] / 1000
                self.y_vel -= math.sin(angle) * self.friction * self.evasionModeFriction * game['frametime'] / 1000
            else:
                self.x_vel -= math.cos(angle) * self.friction * game['frametime'] / 1000
                self.y_vel -= math.sin(angle) * self.friction * game['frametime'] / 1000

            self.progress = 0

        if any([keys[key] for key in game['controls']['keyDown']]):
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

        if not self.enabled:
            return True

        self.specialCharge = min(self.specialMaxCharge, self.specialCharge + game['frametime'] / 1000)

        if self.evasionModeActive == 0:
            self.evasionModeCharge = min(self.evasionModeMax, self.evasionModeCharge + game['frametime'] / 1000)
        self.evasionModeActive = max(0, self.evasionModeActive - game['frametime'] / 1000)

        self.draw(game)
        self.updateControl(game)
        self.updatePosition(game)
        
        # Test for collisions
        if self.evasionModeActive <= 0 and self.updateCollisions(game):
            effects.createExplosion(self.x, self.y, game)
            # Evasion Mode
            if self.evasionMode and self.evasionModeCharge >= self.evasionModeCost:
                print('evasion mode: active')
                self.evasionModeActive = self.evasionModeDuration
                self.evasionModeCharge -= self.evasionModeCost
        
        if self.health <= 0:
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
                self.maxSpeed = 200
                self.rotation = 3
                self.friction = 100
                self.maxHealth = 1.5
                self.health = 1.5
                self.specialName = 'TELEPORT'
                self.specialCharge = 30
                self.specialMaxCharge = 30
                self.specialCost = 30
                self.specialFunction = teleport

                self.noAccelMulti = 0.8
            
            case 'bomber':
                self.size *= 1.5
                self.playerShape = bomberShape
                self.hitbox = bomberHitbox
            
            case 'heavy':
                self.size *= 2
                self.playerShape = heavyShape
                self.hitbox = heavyHitbox

        try:
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
        except Exception as e:
            print(e)

    def shoot(self, game:dict):
        t = 'bullet'
        if self.laser:
            t = 'laser'

        if not self.chargeBlast or self.charge < self.chargeTime:
            for i in range(self.spreadFireCount):
                a = self.angle - self.spreadAngle / 2 + self.spreadAngle * i / max(1, self.spreadFireCount - 1)
                bXVel = self.x_vel + math.cos(a) * self.bulletSpeed
                bYVel = self.y_vel + math.sin(a) * self.bulletSpeed
                bAngle = math.atan2(bYVel, bXVel)
                bMagnitude = max(self.bulletSpeed, math.sqrt(bXVel ** 2 + bYVel ** 2))
                game['bullets'].append(Bullet(self.x + math.cos(a) * self.size * self.bulletSize / 2,
                                            self.y + math.sin(a) * self.size * self.bulletSize / 2,
                                            a,
                                            bAngle,
                                            bMagnitude,
                                            self.bulletSize,
                                            damage=self.bulletDamage,
                                            type=t))
            return
        
        # Charge Blast
        for i in range(self.chargeBlastCount):
            a = self.angle - self.chargeBlastSpread / 2 + self.chargeBlastSpread * i / max(1, self.chargeBlastCount - 1)
            bXVel = self.x_vel + math.cos(a) * self.chargeBlastSpeed
            bYVel = self.y_vel + math.sin(a) * self.chargeBlastSpeed
            bAngle = math.atan2(bYVel, bXVel)
            bMagnitude = max(self.chargeBlastSpeed, math.sqrt(bXVel ** 2 + bYVel ** 2))
            game['bullets'].append(Bullet(self.x + math.cos(a) * self.size * self.chargeBlastSize / 2,
                                        self.y + math.sin(a) * self.size * self.chargeBlastSize / 2,
                                        a,
                                        bAngle,
                                        bMagnitude,
                                        self.chargeBlastSize,
                                        damage=self.chargeBlastDamage,
                                        type=t))
        self.charge = 0
