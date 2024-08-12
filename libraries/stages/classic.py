import pygame
import libraries.services.spawn as spawn
import libraries.constants as constants

from libraries.entity.player import Player
from libraries.entity.ufo import UFO


class Classic:
    def __init__(self, game:dict):
        game['lives'] = 1

        # Create Player
        game['players'] = [Player(320, 240, 0, constants.PLAYER_SIZE)]

        game['bullets'] = []
        game['asteroids'] = []
        game['particles'] = []
        game['shipParts'] = []
        game['enemies'] = []
        game['enemyBullet'] = []

        game['gameWidth'] = game['screenWidth']
        game['gameHeight'] = game['screenHeight']
        game['scrollX'] = 0
        game['scrollY'] = 0
        game['bulletWrap'] = False

        # Set up gui
        self.scoreSize = game['screenHeight'] * 0.1
        self.guiSurface = pygame.Surface((game['screenWidth'], game['screenHeight']))
        self.scoreFont = pygame.font.Font('fonts/PastiRegular.otf', int(self.scoreSize))
        self.scoreX = game['screenWidth'] * 0.05
        self.scoreY = game['screenHeight'] * 0.05
        self.score = 0
        self.level = 0
        self.spawnTick = 20
        self.progress = 0
        self.enemyCount = 0

    def newLevel(self, game:dict):
        self.enemyCount = len(game['enemies'])
        self.level += 1
        self.spawnTick = max(1, 20 - self.level)
        for _ in range(5 + self.level):
            spawn.spawnAsteroid(game, player=game['players'][0])

    def updateEnemySpawns(self, game:dict):
        if len(game['enemies']) > 0 or self.enemyCount > 2:
            return
        
        self.progress += game['frametime'] / 1000
        if self.progress >= self.spawnTick:
            spawn.spawnUFO(game, min(constants.UFO_SPEED + self.level * 4, constants.UFO_MAX_SPEED))
            self.enemyCount += 1
            self.progress -= self.spawnTick

    async def update(self, game:dict):
        # Update Background
        game['screen'].blit(game['background'], (0, 0))
        for layer in game['layers']:
            layer.fill((1, 1, 1))
            layer.set_colorkey((1, 1, 1))

        # Update Player
        game['players'] = [player for player in game['players'] if player.update(game)]

        # Update Bullets
        game['bullets'] = [bullet for bullet in game['bullets'] if bullet.update(game)]

        # Update Asteroids
        for index, asteroid in reversed(list(enumerate(game['asteroids']))):
            if asteroid.update(game):
                continue
            game['asteroids'].pop(index)
            self.score += 1

        # Update Enemies
        for index, enemy in reversed(list(enumerate(game['enemies']))):
            if enemy.update(game):
                continue
            game['enemies'].pop(index)
            self.score += 1

        # Update Enemy Projectiles
        game['enemyBullets'] = [bullet for bullet in game['enemyBullets'] if bullet.update(game)]

        # Update Particles
        game['particles'] = [particle for particle in game['particles'] if particle.update(game)]
        
        # Update Ship Parts
        game['shipParts'] = [shipPart for shipPart in game['shipParts'] if shipPart.update(game)]

        # Update the Game Display
        for layer in game['layers']:
            game['screen'].blit(layer, (0, 0))

        # Update Gui
        self.updateGui()
        game['screen'].blit(self.guiSurface, (self.scoreX, self.scoreY))
        
        pygame.display.flip()

        # Enemy Spawns
        self.updateEnemySpawns(game)

        # New level
        if len(game['asteroids']) == 0 and len(game['players']) > 0:
            self.newLevel(game)

        # Gameover
        if len(game['shipParts']) == 0 and len(game['players']) == 0:
            return 'Gameover'

    def updateGui(self):
        self.guiSurface = self.scoreFont.render(f'{self.score}', True, (255, 255, 255))
