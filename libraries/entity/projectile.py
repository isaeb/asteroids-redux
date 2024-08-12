"""
Module providing a class for bullets
"""
import pygame
import math
import libraries.services.polygon as polygon
import libraries.services.effects as effects
from libraries.constants import *


bulletShape = [(math.pi * 0.25, 0.707), (math.pi * 0.75, 0.707), (math.pi * 1.25, 0.707), (math.pi * 1.75, 0.707)]

class Bullet:
    """
    Class for bullets
    """
    
    def __init__(self, x:float, y:float, angle:float, moveAngle:float, spd:float, size:float, distance:float=BULLET_DISTANCE):
        """
        Args:
            x (float): x position
            y (float): y position
            angle (float): angle position
            moveAngle (float): angle of movement
            spd (float): speed of movement
            size (float): size
        """

        # Define Variables
        self.x = x
        self.y = y
        self.angle = angle
        self.moveAngle = moveAngle
        self.size = size
        self.x_vel = math.cos(angle) * spd
        self.y_vel = math.sin(angle) * spd
        self.distance = distance
        
        # Make a Polygon
        self.points = [(self.x + math.cos(point[0] + self.angle) * self.size * point[1],
                        self.y + math.sin(point[0] + self.angle) * self.size * point[1])
                        for point in bulletShape]

    def draw(self, game:dict):
        """
        Args:
            game (dict): The game dict
        """

        if not game['bulletWrap']:
            pygame.draw.polygon(game['layers'][1], pygame.Color(0, 0, 0, 255), self.points)
            pygame.draw.aalines(game['layers'][1], pygame.Color(255, 255, 255, 255), True, self.points)
            return

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
                p = [(point[0] + x - 1 + scrollOffsetX, point[1] + y - 1 + scrollOffsetY) for point in self.points]
                # offset by 1 pixel to account for anti aliasing
                pygame.draw.polygon(game['layers'][1], pygame.Color(0, 0, 0, 255), p)
                pygame.draw.aalines(game['layers'][1], pygame.Color(255, 255, 255, 255), True, p)

    def checkEnemyCollision(self, game:dict):
        for n, enemy in enumerate(game['enemies']):
            if polygon.colliding(enemy.hitbox, self.points):
                return n
            if enemy.y + enemy.size > game['gameHeight']:
                if polygon.colliding(enemy.hitbox, [(point[0], point[1] + game['gameHeight']) for point in self.points]):
                    return n
            if enemy.y - enemy.size < 0:
                if polygon.colliding(enemy.hitbox, [(point[0], point[1] - game['gameHeight']) for point in self.points]):
                    return n
            if enemy.x + enemy.size > game['gameWidth']:
                if polygon.colliding(enemy.hitbox, [(point[0] + game['gameWidth'], point[1]) for point in self.points]):
                    return n
            if enemy.x - enemy.size < 0:
                if polygon.colliding(enemy.hitbox, [(point[0] - game['gameWidth'], point[1]) for point in self.points]):
                    return n
        return None

    def checkAsteroidCollision(self, game:dict):
        for n, asteroid in enumerate(game['asteroids']):
            if polygon.colliding(asteroid.points, self.points):
                return n
            if asteroid.y + asteroid.size > game['gameHeight']:
                if polygon.colliding(asteroid.points, [(point[0], point[1] + game['gameHeight']) for point in self.points]):
                    return n
            if asteroid.y - asteroid.size < 0:
                if polygon.colliding(asteroid.points, [(point[0], point[1] - game['gameHeight']) for point in self.points]):
                    return n
            if asteroid.x + asteroid.size > game['gameWidth']:
                if polygon.colliding(asteroid.points, [(point[0] + game['gameWidth'], point[1]) for point in self.points]):
                    return n
            if asteroid.x - asteroid.size < 0:
                if polygon.colliding(asteroid.points, [(point[0] - game['gameWidth'], point[1]) for point in self.points]):
                    return n
        return None

    def updatePosition(self, game:dict):
        # Apply velocity
        self.x += self.x_vel * (game['frametime'] / 1000)
        self.y += self.y_vel * (game['frametime'] / 1000)

        # Update the position of the bullet
        self.points = [(self.x + math.cos(point[0] + self.angle) * self.size * point[1],
                        self.y + math.sin(point[0] + self.angle) * self.size * point[1])
                        for point in bulletShape]

        if not game['bulletWrap']:
            if self.x - self.size > game['screenWidth']:
                return False
            
            if self.x + self.size < 0:
                return False
            
            if self.y - self.size > game['screenHeight']:
                return False
            
            if self.y + self.size < 0:
                return False
        else:
            self.x %= game['gameWidth']
            self.y %= game['gameHeight']

            self.distance -= (game['frametime'] / 1000)
            if self.distance <= 0:
                return False
        
        return True

    def updateCollisions(self, game:dict):
        n = self.checkAsteroidCollision(game)
        if n is not None:
            effects.createExplosion(self.x, self.y, game)
            game['asteroids'][n].health -= 1
            return True
    
        n = self.checkEnemyCollision(game)
        if n is not None:
            effects.createExplosion(self.x, self.y, game)
            game['enemies'][n].health -= 1
            return True
        
        return False

    def update(self, game:dict):
        """
        Args:
            game (dict): The game dict
        """

        if self.updateCollisions(game):
            return False
        
        self.draw(game)
        
        return self.updatePosition(game)


class EnemyBullet:
    """
    Class for enemy bullets
    """
    
    def __init__(self, x:float, y:float, angle:float, moveAngle:float, spd:float, size:float, health:int=1, distance:float=BULLET_DISTANCE, damage:float=1):
        """
        Args:
            x (float): x position
            y (float): y position
            angle (float): angle position
            moveAngle (float): angle of movement
            spd (float): speed of movement
            size (float): size
        """

        # Define Variables
        self.x = x
        self.y = y
        self.angle = angle
        self.moveAngle = moveAngle
        self.size = size
        self.x_vel = math.cos(angle) * spd
        self.y_vel = math.sin(angle) * spd
        self.health = health
        self.distance = distance
        self.damage = damage
        
        # Make a Polygon
        self.points = [(self.x + math.cos(point[0] + self.angle) * self.size * point[1],
                        self.y + math.sin(point[0] + self.angle) * self.size * point[1])
                        for point in bulletShape]

    def draw(self, game:dict):
        """
        Args:
            game (dict): The game dict
        """

        if not game['bulletWrap']:
            pygame.draw.polygon(game['layers'][1], pygame.Color(0, 0, 0, 255), self.points)
            pygame.draw.aalines(game['layers'][1], pygame.Color(255, 255, 255, 255), True, self.points)
            return

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
                p = [(point[0] + x - 1 + scrollOffsetX, point[1] + y - 1 + scrollOffsetY) for point in self.points]
                # offset by 1 pixel to account for anti aliasing
                pygame.draw.polygon(game['layers'][1], pygame.Color(0, 0, 0, 255), p)
                pygame.draw.aalines(game['layers'][2], pygame.Color(255, 255, 255, 255), True, p)

    def updatePosition(self, game:dict):
        # Apply velocity
        self.x += self.x_vel * (game['frametime'] / 1000)
        self.y += self.y_vel * (game['frametime'] / 1000)

        # Update the position of the bullet
        self.points = [(self.x + math.cos(point[0] + self.angle) * self.size * point[1],
                        self.y + math.sin(point[0] + self.angle) * self.size * point[1])
                        for point in bulletShape]

    def checkAsteroidCollision(self, game:dict):
        for n, asteroid in enumerate(game['asteroids']):
            if polygon.colliding(asteroid.points, self.points):
                return n
            if asteroid.y + asteroid.size > game['gameHeight']:
                if polygon.colliding(asteroid.points, [(point[0], point[1] + game['gameHeight']) for point in self.points]):
                    return n
            if asteroid.y - asteroid.size < 0:
                if polygon.colliding(asteroid.points, [(point[0], point[1] - game['gameHeight']) for point in self.points]):
                    return n
            if asteroid.x + asteroid.size > game['gameWidth']:
                if polygon.colliding(asteroid.points, [(point[0] + game['gameWidth'], point[1]) for point in self.points]):
                    return n
            if asteroid.x - asteroid.size < 0:
                if polygon.colliding(asteroid.points, [(point[0] - game['gameWidth'], point[1]) for point in self.points]):
                    return n
        return None

    def update(self, game:dict):
        """
        Args:
            game (dict): The game dict
        """

        self.updatePosition(game)

        r = self.checkAsteroidCollision(game)
        if r is not None:
            game['asteroids'][r].health -= 1
            self.health -= 1
        
        if not game['bulletWrap']:
            if self.x - self.size > game['screenWidth']:
                return False
            
            if self.x + self.size < 0:
                return False
            
            if self.y - self.size > game['screenHeight']:
                return False
            
            if self.y + self.size < 0:
                return False
        else:
            self.distance -= game['frametime'] / 1000
            if self.distance <= 0:
                return False
        
        self.draw(game)
        
        if self.health <= 0:
            effects.createExplosion(self.x, self.y, game)
            return False
        return True
