import pygame

from random import random
from math import sqrt

def teleport(game:dict):
    print('teleport')
    r = game['screenWidth'] / 6
    # Error Checking
    if game['players'] == 0:
        return

    # Get Player Obj
    player = game['players'][0]

    # Get random coords
    pX, pY = (player.x, player.y)
    
    width = game['gameWidth'] - game['screenWidth']
    height = game['gameHeight'] - game['screenHeight']

    rX, rY = (pX + random() * width + game['screenWidth'] / 2, pY + random() * height + game['screenHeight'] / 2)

    # Update Asteroids
    game['asteroids'] = [asteroid for asteroid in game['asteroids'] if sqrt((asteroid.x - rX) ** 2 + (asteroid.y - rY) ** 2) > r]

    # Update Enemies
    game['enemies'] = [enemy for enemy in game['enemies'] if sqrt((enemy.x - rX) ** 2 + (enemy.y - rY) ** 2) > r]

    # Update Enemy Projectiles
    game['enemyBullets'] = [bullet for bullet in game['enemyBullets'] if sqrt((bullet.x - rX) ** 2 + (bullet.y - rY) ** 2) > r]

    player.x = rX
    player.y = rY
    player.x_vel = 0
    player.y_vel = 0
