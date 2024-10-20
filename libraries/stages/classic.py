import pygame
import numpy

import libraries.services.spawn as spawn

from libraries.constants import *

from libraries.entity.player import Player
from libraries.services.drawEffects import renderText
from libraries.entity.ufo import UFO
from libraries.stages.classicUpgrades import ClassicUpgrades

maxCooldown = 3

class Classic:
    def __init__(self, game:dict):
        game['last'] = 'Classic'
        game['lives'] = 1

        # Create Player
        game['players'] = [Player(320, 240, 0, PLAYER_SIZE)]
        game['players'][0].updateStats(game)

        game['bullets'] = []
        game['asteroids'] = []
        game['particles'] = []
        game['shipParts'] = []
        game['enemies'] = []
        game['enemyBullet'] = []

        game['movement'] = 0
        game['weapons'] = 0
        game['special'] = 0
        game['auxiliary'] = 0
        game['movementFeatures'] = []
        game['weaponsFeatures'] = []
        game['specialFeatures'] = []
        game['auxiliaryFeatures'] = []
        game['last'] = 'CSSRedux'

        game['gameWidth'] = game['screenWidth']
        game['gameHeight'] = game['screenHeight']
        game['scrollX'] = 0
        game['scrollY'] = 0
        game['bulletWrap'] = False

        # Clear background
        game['background'].fill((0, 0, 0))

        # Generate points
        starCount = 60
        starX = numpy.random.uniform(0, game['screenWidth'], starCount)
        starY = numpy.random.uniform(0, game['screenHeight'], starCount)

        # Draw points
        for index in range(starCount):
            pygame.draw.circle(game['background'], pygame.Color(255, 255, 255), (starX[index], starY[index]), 1)

        self.healthFont = pygame.font.Font('fonts/SignwoodItalic.ttf', int(game['screenHeight'] * 0.1))
        self.healthColor = pygame.Color(200, 255, 255)

        self.specialFont = pygame.font.Font('fonts/SignwoodItalic.ttf', int(game['screenHeight'] * 0.05))
        self.specialColor = pygame.Color(200, 200, 200)

        self.ammoFont = pygame.font.Font('fonts/SignwoodItalic.ttf', int(game['screenHeight'] * 0.05))
        self.ammoColor = pygame.Color(200, 200, 200)

        self.hitFont = pygame.font.Font('fonts/NikkyouSans.ttf', int(game['screenHeight'] * 0.03))
        
        self.scoreFont = pygame.font.Font('fonts/NikkyouSans.ttf', int(game['screenHeight'] * 0.1))
        self.scoreStartColor = pygame.Color(255, 255, 150)
        self.scoreEndColor = pygame.Color(200, 200, 150)

        # Set up gui
        self.guiSurface = pygame.Surface((game['screenWidth'], game['screenHeight']))
        self.guiModules = []
        self.fadeout = 1
        self.fadeoutSurf = pygame.Surface((game['screenWidth'], game['screenHeight']))
        self.fadeoutSurf.fill((0, 0, 0))
        self.guiAlpha = 1

        self.score = 0
        self.level = 0
        self.spawnTick = 20
        self.progress = 0
        self.enemyCount = 0

        self.state = 'gameplay'
        self.cooldown = maxCooldown
        self.newLevel(game)

    def newLevel(self, game:dict):
        self.enemyCount = len(game['enemies'])
        self.level += 1
        self.spawnTick = max(1, 20 - self.level)
        for _ in range(1 + self.level):
            spawn.spawnAsteroid(game, player=game['players'][0])

    def updateEnemySpawns(self, game:dict):
        if len(game['enemies']) > 0 or self.enemyCount > 2:
            return
        
        self.progress += game['frametime'] / 1000
        if self.progress >= self.spawnTick:
            spawn.spawnUFO(game, min(UFO_SPEED + self.level * 4, UFO_MAX_SPEED))
            self.enemyCount += 1
            self.progress -= self.spawnTick

    async def update(self, game:dict):
        if self.state == 'gameplay':
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
            self.updateGui(game)
            game['screen'].blit(self.guiSurface, (0, 0))
            
            pygame.display.flip()

            # Enemy Spawns
            self.updateEnemySpawns(game)

            # New level
            if len(game['asteroids']) == 0 and len(game['players']) > 0:
                if len(game['players']) > 0 and game['players'][0].enabled:
                    game['players'][0].disable()
                    self.missionComplete = ClassicMissionComplete(5, game)
                    self.upgradeObject = ClassicUpgrades(game)

                self.cooldown -= game['frametime'] / 1000
                self.guiSurface.set_alpha(max(0, (self.cooldown - maxCooldown + 1)) * 255)
                self.fadeout = max(0, 1 - self.cooldown)
                if self.cooldown <= 0:
                    self.score = 0
                    self.state = 'upgrades'
                    self.cooldown = 0

                if self.fadeout > 0:
                    self.fadeoutSurf.set_alpha(self.fadeout * 255)
                    game['screen'].blit(self.fadeoutSurf, (0, 0))
                    self.fadeout -= game['frametime'] / 1000

            # Gameover
            if len(game['shipParts']) == 0 and len(game['players']) == 0:
                game['score'] = self.score
                if game['NGIO'].loggedIn:
                    game['NGIO'].postScore(CLASSIC_ID, self.score)
                return 'Gameover'
        elif self.state == 'upgrades':
            # Update Background
            game['screen'].fill((0, 0, 0))
            for layer in game['layers']:
                layer.fill((1, 1, 1))
                layer.set_colorkey((1, 1, 1))

            # Update Asteroids
            for index, asteroid in reversed(list(enumerate(game['asteroids']))):
                if asteroid.update(game):
                    continue
                game['asteroids'].pop(index)

            # Update the Game Display
            for layer in game['layers']:
                game['screen'].blit(layer, (0, 0))
            
            # Update UI
            r = self.upgradeObject.update(game)
            if r is not None:
                if r:
                    self.updateUpgrades(game)
                    self.cooldown = 1

            if self.cooldown > 0:
                self.cooldown -= game['frametime'] / 1000
                self.fadeout = 1 - self.cooldown
                if self.cooldown <= 0:
                    self.newLevel(game)
                    self.state = 'gameplay'
                    self.cooldown = maxCooldown

            if self.fadeout > 0:
                self.fadeoutSurf.set_alpha(self.fadeout * 255)
                game['screen'].blit(self.fadeoutSurf, (0, 0))
                if self.cooldown == 0:
                    self.fadeout -= game['frametime'] / 1000

            pygame.display.flip()

    def updateGui(self, game:dict):
        # clear canvas
        self.guiSurface.fill((1, 1, 1))
        self.guiSurface.set_colorkey((1, 1, 1))

        x = game['screenWidth'] * 0.97
        y = game['screenHeight'] * 0.03

        # Draw Score Text
        scoreSurf = renderText(f'{self.score}', self.scoreFont, self.scoreStartColor, self.scoreEndColor, (50, 50, 50), (3, 3), (0, 0, 0), 1)
        scoreWidth = scoreSurf.get_width()
        x = game['screenWidth'] * 0.97 - scoreWidth
        self.guiSurface.blit(scoreSurf, (x, y))

        # Draw Health Text
        """
        gradientColor = (self.healthColor.r * 0.8, self.healthColor.g * 0.8, self.healthColor.b * 0.8)
        healthSurf = renderText('HEALTH', self.healthFont, self.healthColor, gradientColor, (50, 50, 50), (3, 3), (0, 0, 0), 2)
        healthWidth = healthSurf.get_width()
        healthHeight = healthSurf.get_height()
        x = game['screenWidth'] * 0.03
        y = game['screenHeight'] * 0.03
        self.guiSurface.blit(healthSurf, (x, y))
        """
        x = game['screenWidth'] * 0.03
        # Draw Health Bar
        if len(game['players']) > 0:
            player = game['players'][0]
            self.healthLength = 100 * player.maxHealth / 2
        scoreBarColor = pygame.Color(200, 255, 200)
        #y = y + healthHeight

        # Outside
        pygame.draw.rect(self.guiSurface, scoreBarColor, pygame.Rect(x, y, self.healthLength, 50 * 0.4), width=2)

        # Inside
        progress = 0
        if len(game['players']) > 0:
            player = game['players'][0]
            progress = player.health / player.maxHealth
        margin = 4
        pygame.draw.rect(self.guiSurface, scoreBarColor, pygame.Rect(x + margin, y + margin, (self.healthLength - margin * 2) * progress, 50 * 0.4 - margin * 2))

class ClassicMissionComplete:
    def __init__(self, time, game:dict):
        self.time = time
        self.maxTime = time
        self.initialFlash = 1
        self.text = 'MISSION COMPLETE'
        self.fontPath = 'fonts/Signwood.ttf'
        self.fontSize = game['screenHeight'] * 0.15
        self.startColor = pygame.Color(255, 0, 0)
        self.endColor = pygame.Color(200, 0, 0)

    def update(self, game:dict):
        self.time -= game['frametime'] / 1000
        if self.time < 0:
            return False
        
        self.draw(game)
        return True

    def draw(self, game:dict):
        progress = (self.maxTime - self.time)
        alpha = 1
        flash = 0
        size = 1

        if progress < self.initialFlash:
            alpha = min(1, progress / (self.initialFlash / 2))
            flash = max(0, 1 - progress / (self.initialFlash / 2))
            size = 1
        
        font = pygame.font.Font(self.fontPath, int(self.fontSize * size))

        surf = renderText(self.text, font, self.startColor, self.endColor, (50, 50, 50), (5, 5), (0, 0, 0), 2)
        if flash > 0:
            flashSurf = renderText(self.text, font, (255, 255, 255), (255, 255, 255), (255, 255, 255), (5, 5), (0, 0, 0), 2)
            flashSurf.set_alpha(flash * 255)
            surf.blit(flashSurf, (0, 0))
        surf.set_alpha(alpha * 255)

        x = game['screenWidth'] / 2 - surf.get_width() / 2
        y = game['screenHeight'] / 2 - surf.get_height() / 2
        game['screen'].blit(surf, (x, y))

