from random import random
import math

from libraries.entity.asteroid import Asteroid
from libraries.entity.player import Player
from libraries.entity.ufo import UFO

from libraries.entity.reduxEnemy.satellite import Satellite
from libraries.entity.reduxEnemy.turret import Turret

from libraries.constants import *


def spawnAsteroid(game:dict, player:Player=None, spawnRange=80, color=(0, 0, 0)):
    """
    Args:
        game (dict): The game dict
        player (Player): A Player object
    """

    if player is None:
        aX = random() * game['gameWidth']
        aY = random() * game['gameHeight']
    else:
        loop = True
        while loop:
            loop = False
            aX = random() * game['gameWidth']
            aY = random() * game['gameHeight']
            for x in range(-1, 1):
                for y in range(-1, 1):
                    pX = player.x + x * game['gameWidth']
                    pY = player.y + y * game['gameHeight']
                    if math.sqrt(abs(aX - pX) ** 2 + abs(aY - pY) ** 2) < spawnRange:
                        loop = True

    aVelX = random() * 50 - 25
    aVelY = random() * 50 - 25
    aVelAngle = random() * math.pi - math.pi / 2

    game['asteroids'].append(Asteroid(aX, aY, aVelX, aVelY, aVelAngle, 40 + random() * 40, health=3, color=color))


def spawnReduxSatellite(game:dict, player:Player=None, spawnRange=80):
    """
    Args:
        game (dict): The game dict
        player (Player): A Player object
    """

    if player is None:
        aX = random() * game['gameWidth']
        aY = random() * game['gameHeight']
    else:
        loop = True
        while loop:
            loop = False
            aX = random() * game['gameWidth']
            aY = random() * game['gameHeight']
            for x in range(-1, 1):
                for y in range(-1, 1):
                    pX = player.x + x * game['gameWidth']
                    pY = player.y + y * game['gameHeight']
                    if math.sqrt(abs(aX - pX) ** 2 + abs(aY - pY) ** 2) < spawnRange:
                        loop = True

    aVelX = random() * 100 - 50
    aVelY = random() * 100 - 50

    game['enemies'].append(Satellite(aX, aY, SATELLITE_SIZE, aVelX, aVelY))


def spawnReduxTurret(game:dict, player:Player=None, spawnRange=80):
    """
    Args:
        game (dict): The game dict
        player (Player): A Player object
    """

    if player is None:
        aX = random() * game['gameWidth']
        aY = random() * game['gameHeight']
    else:
        loop = True
        while loop:
            loop = False
            aX = random() * game['gameWidth']
            aY = random() * game['gameHeight']
            for x in range(-1, 1):
                for y in range(-1, 1):
                    pX = player.x + x * game['gameWidth']
                    pY = player.y + y * game['gameHeight']
                    if math.sqrt(abs(aX - pX) ** 2 + abs(aY - pY) ** 2) < spawnRange:
                        loop = True

    game['enemies'].append(Turret(aX, aY, TURRET_SIZE))


def spawnUFO(game:dict, speed:float):
    """
    Args:
        game (dict): The game dict
    """

    # Create a UFO
    ufoSize = UFO_SIZE
    
    ufoX = 0
    ufoY = 0
    quad = int(random() * 4)
    match quad:
        case 0:
            ufoX = -ufoSize
            ufoY = random() * game['gameHeight']
        case 1:
            ufoX = game['gameWidth'] + ufoSize
            ufoY = random() * game['gameHeight']
        case 2:
            ufoX = random() * game['gameWidth'] + ufoSize
            ufoY = -ufoSize
        case 3:
            ufoX = random() * game['gameWidth'] + ufoSize
            ufoY = game['gameHeight'] + ufoSize

    ufoTargetX = random() * (game['gameWidth'] - ufoSize * 2) + ufoSize
    ufoTargetY = random() * (game['gameHeight'] - ufoSize * 2) + ufoSize
    game['enemies'].append(UFO(ufoX, ufoY, ufoTargetX, ufoTargetY, ufoSize, speed))
