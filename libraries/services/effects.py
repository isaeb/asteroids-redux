import math
import random
import pygame

from libraries.entity.particle import Particle
from libraries.services.drawEffects import renderText


def createExplosion(x, y, game, scale=2):
    for _ in range(8):
        pMagnitude = random.random() * 5 + 6
        pMagnitude *= scale
        pAngle = random.random() * math.pi * 2
        pVelX = math.cos(pAngle) * pMagnitude
        pVelY = math.sin(pAngle) * pMagnitude

        pX = x
        pY = y
        game['particles'].append(Particle(pX, pY, pVelX, pVelY, 4, 0, pygame.Color(255, 100, 0, 250), pygame.Color(100, 30, 0, 0), 0.4, layer=1))
    for _ in range(12):
        pMagnitude = random.random() * 2 + 3
        pMagnitude *= scale
        pAngle = random.random() * math.pi * 2
        pVelX = math.cos(pAngle) * pMagnitude
        pVelY = math.sin(pAngle) * pMagnitude

        pX = x
        pY = y
        game['particles'].append(Particle(pX, pY, pVelX, pVelY, 3, 0, pygame.Color(255, 100, 100, 255), pygame.Color(200, 200, 100, 0), 0.5, layer=2))
    for _ in range(8):
        pMagnitude = random.random() * 2 + 11
        pMagnitude *= scale
        pAngle = random.random() * math.pi * 2
        pVelX = math.cos(pAngle) * pMagnitude
        pVelY = math.sin(pAngle) * pMagnitude

        pX = x
        pY = y
        game['particles'].append(Particle(pX, pY, pVelX, pVelY, 3, 0, pygame.Color(50, 50, 0, 255), pygame.Color(30, 30, 0, 0), 0.5, layer=2))

class Score:
    def __init__(self, x, y, font, value, time=1, spd=20, color=(255, 255, 200)):
        self.x = x
        self.y = y
        self.font = font
        self.time = time
        self.value = value
        self.color = color
        self.spd = spd
        self.surf = renderText(self.value, self.font, self.color, (self.color[0] * 0.8, self.color[1] * 0.8, self.color[2] * 0.8), (50, 50, 50), (3, 3), (0, 0, 0), 1)
        self.surf.set_colorkey((1, 1, 1))
        self.x -= self.surf.get_width() / 2
        self.y -= self.surf.get_height() / 2
    
    def update(self, game):
        self.time -= game['frametime'] / 1000
        self.y -= self.spd * game['frametime'] / 1000

        self.draw(game)
        if self.time < 0:
            return False
        return True

    def draw(self, game):
        #self.surf.fill((1, 1, 1, 0.001))
        scrollOffsetX = - game['scrollX']
        scrollOffsetY = - game['scrollY']
        
        drawX = [0]
        drawY = [0]
        
        # draw at y - gameHeight
        if self.y + scrollOffsetY > game['gameHeight']:
            drawY.append(-game['gameHeight'])

        # draw at y + gameHeight
        if self.y + scrollOffsetY < 0:
            drawY.append(game['gameHeight'])

        # draw ship at x - gameWidth
        if self.x + scrollOffsetX > game['gameWidth']:
            drawX.append(-game['gameWidth'])

        # draw ship at x + gameWidth
        if self.x + scrollOffsetX < 0:
            drawX.append(game['gameWidth'])

        # draw self
        for x in drawX:
            for y in drawY:
                game['layers'][2].blit(self.surf, (self.x + x + scrollOffsetX, self.y + y + scrollOffsetY))
