import math
import random
import pygame

from libraries.entity.particle import Particle


def createExplosion(x, y, game, scale=2):
    for _ in range(6):
        pMagnitude = random.random() * 10 + 10
        pMagnitude *= scale
        pAngle = random.random() * math.pi * 2
        pVelX = math.cos(pAngle) * pMagnitude
        pVelY = math.sin(pAngle) * pMagnitude

        pX = x
        pY = y
        game['particles'].append(Particle(pX, pY, pVelX, pVelY, 5, 0, pygame.Color(50, 50, 0, 250), pygame.Color(50, 50, 0, 0), 0.5, layer=1))
    for _ in range(4):
        pMagnitude = random.random() * 15 + 10
        pMagnitude *= scale
        pAngle = random.random() * math.pi * 2
        pVelX = math.cos(pAngle) * pMagnitude
        pVelY = math.sin(pAngle) * pMagnitude

        pX = x
        pY = y
        game['particles'].append(Particle(pX, pY, pVelX, pVelY, 4, 0, pygame.Color(100, 100, 0, 250), pygame.Color(100, 100, 0, 0), 0.6, layer=1))
    for _ in range(12):
        pMagnitude = random.random() * 20
        pMagnitude *= scale
        pAngle = random.random() * math.pi * 2
        pVelX = math.cos(pAngle) * pMagnitude
        pVelY = math.sin(pAngle) * pMagnitude

        pX = x
        pY = y
        game['particles'].append(Particle(pX, pY, pVelX, pVelY, 3, 0, pygame.Color(255, 255, 0, 100), pygame.Color(255, 0, 0, 0), 0.5, layer=2))
