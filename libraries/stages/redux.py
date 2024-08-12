import pygame
import numpy
import libraries.services.spawn as spawn

from libraries.constants import *

from libraries.entity.player import Player
from libraries.stages.reduxUpgrades import ReduxUpgrades
from libraries.services.drawEffects import renderText, create_vignette_surface

from random import random

WIDTH = 1280
HEIGHT = 960

maxCooldown = 2

class Redux:
    def __init__(self, game:dict):
        game['lives'] = 3

        game['gameWidth'] = WIDTH
        game['gameHeight'] = HEIGHT
        game['bulletWrap'] = True

        game['class'] = 'scout'
        game['movement'] = 0
        game['weapons'] = 0
        game['special'] = 0
        game['auxiliary'] = 0
        game['movementFeatures'] = []
        game['weaponsFeatures'] = []
        game['specialFeatures'] = []
        game['auxiliaryFeatures'] = []

        # Declare Variables
        self.score = 0
        self.level = 0
        self.enemyCount = 0
        self.targetScore = 100
        self.cooldown = maxCooldown

        # Fonts
        self.missionFont = pygame.font.Font('fonts/SignwoodItalic.ttf', int(game['screenHeight'] * 0.1))
        self.missionColor = pygame.Color(255, 0, 0)

        self.healthFont = pygame.font.Font('fonts/SignwoodItalic.ttf', int(game['screenHeight'] * 0.1))
        self.healthColor = pygame.Color(200, 255, 255)

        self.specialFont = pygame.font.Font('fonts/SignwoodItalic.ttf', int(game['screenHeight'] * 0.05))
        self.specialColor = pygame.Color(200, 200, 200)

        self.ammoFont = pygame.font.Font('fonts/SignwoodItalic.ttf', int(game['screenHeight'] * 0.05))
        self.ammoColor = pygame.Color(200, 200, 200)

        self.timerFont = pygame.font.Font('fonts/Signwood.ttf', int(game['screenHeight'] * 0.12))

        # New level
        self.newLevel(game)

        # Set up gui
        self.guiSurface = pygame.Surface((game['screenWidth'], game['screenHeight']))
        self.guiModules = []
        self.timerObject = ReduxClock(game['screen'], self.timerFont)

        # Special
        yOffset = self.healthFont.render('HEALTH', True, self.healthColor).get_height() * 1.5
        specialWidth = game['screenWidth'] * 0.1
        specialHeight = game['screenHeight'] * 0.02
        x = game['screenWidth'] * 0.03
        y = game['screenHeight'] * 0.04 + yOffset
        progressFunction = lambda game: game['players'][0].specialCharge / game['players'][0].specialMaxCharge
        self.guiModules.append(ReduxGuiBar(x, y, specialWidth, specialHeight, self.specialFont, self.specialColor, game['players'][0].specialName, pygame.Color(200, 255, 200), pygame.Color(200, 255, 200), progressFunction))

        # Ammo
        yOffset += self.specialFont.render(game['players'][0].specialName, True, self.healthColor).get_height() + specialHeight
        ammoWidth = game['screenWidth'] * 0.1
        ammoHeight = game['screenHeight'] * 0.02
        x = game['screenWidth'] * 0.03
        y = game['screenHeight'] * 0.04 + yOffset
        progressFunction = lambda game:  (game['players'][0].maxBullets - len(game['bullets'])) / game['players'][0].maxBullets
        self.guiModules.append(ReduxGuiBar(x, y, ammoWidth, ammoHeight, self.ammoFont, self.ammoColor, 'AMMO', pygame.Color(200, 255, 200), pygame.Color(200, 255, 200), progressFunction))

        self.state = 'gameplay'
        self.upgradeObject = ReduxUpgrades(game)

        # Set up background
        game['background'].fill((0, 0, 0))

        # Set up vignette
        self.vignetteSurf = create_vignette_surface((game['screenWidth'], game['screenHeight']), (0, 0, 0), game['screenWidth'] * 0.45)

    def newLevel(self, game:dict):
        self.enemyCount = len(game['enemies'])
        self.level += 1
        self.spawnTick = max(1, 10 - self.level)
        self.targetScore = self.level * 100 + 50

        self.timerObject = ReduxClock(game['screen'], self.timerFont)

        game['bullets'] = []
        game['asteroids'] = []
        game['particles'] = []
        game['shipParts'] = []
        game['enemies'] = []
        game['enemyBullet'] = []

        # Create Player
        game['players'] = [Player(320, 240, 0, PLAYER_SIZE)]
        game['players'][0].updateStats(game)

        # Generate points
        starCount = 480
        starX = numpy.random.uniform(0, WIDTH, starCount)
        starY = numpy.random.uniform(0, HEIGHT, starCount)
        self.stars = [(starX[i], starY[i], pygame.Color(random() * 255, random() * 255, random() * 255, 255)) for i in range(len(starX))]

        for _ in range(30):
            r = random()
            color = pygame.Color(16 + r * 16, r * 20, r * 10)
            spawn.spawnAsteroid(game, player=game['players'][0], spawnRange=160, color=color)

        for _ in range(10):
            spawn.spawnReduxTurret(game, player=game['players'][0], spawnRange=160)

        for _ in range(10):
            spawn.spawnReduxSatellite(game, player=game['players'][0], spawnRange=160)

    async def update(self, game:dict):
        if self.state == 'gameplay':
            if len(game['players']) > 0:
                while len(game['enemies']) < 20:
                    if random() * 2 >= 1:
                        spawn.spawnReduxTurret(game, player=game['players'][0], spawnRange=game['screenWidth'] * 0.75)
                    else:
                        spawn.spawnReduxSatellite(game, player=game['players'][0], spawnRange=game['screenWidth'] * 0.75)
                while len(game['asteroids']) < 20:
                    r = random()
                    color = pygame.Color(16 + r * 16, r * 20, r * 10)
                    spawn.spawnAsteroid(game, player=game['players'][0], spawnRange=game['screenWidth'] * 0.75, color=color)

            # Update scroll Values
            if len(game['players']) > 0:
                game['scrollX'] = game['players'][0].x - game['screenWidth'] / 2
                game['scrollY'] = game['players'][0].y - game['screenHeight'] / 2

            # Update Background
            game['screen'].fill((0, 0, 0))
            await drawStars(game['screen'], self.stars, game)
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
                self.score += enemy.value

            # Update Enemy Projectiles
            game['enemyBullets'] = [bullet for bullet in game['enemyBullets'] if bullet.update(game)]

            # Update Particles
            game['particles'] = [particle for particle in game['particles'] if particle.update(game)]
            
            # Update Ship Parts
            game['shipParts'] = [shipPart for shipPart in game['shipParts'] if shipPart.update(game)]

            # Update the Game Display
            for layer in game['layers']:
                game['screen'].blit(layer, (0, 0))

            # Draw Vignette
            game['screen'].blit(self.vignetteSurf, (0, 0))

            # Update Gui
            self.updateGui(game)
            game['screen'].blit(self.guiSurface, (0, 0))
            
            pygame.display.flip()

            if self.score >= self.targetScore:
                if len(game['players']) > 0:
                    game['players'][0].disable()

                self.cooldown -= game['frametime'] / 1000
                if self.cooldown <= 0:
                    self.upgradeObject = ReduxUpgrades(game)
                    self.score = 0
                    self.state = 'upgrades'
                    self.cooldown = maxCooldown

            # Gameover
            if len(game['shipParts']) == 0 and len(game['players']) == 0:
                return 'Gameover'
            
        elif self.state == 'upgrades':

            # Update Background
            game['screen'].fill((0, 0, 0))
            await drawStars(game['screen'], self.stars, game)
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
                    self.newLevel(game)
                    self.state = 'gameplay'


            pygame.display.flip()

        elif self.state == 'paused':
            pass

    def updateGui(self, game:dict):
        # Draw Clock
        self.timerObject.update(game, (self.score < self.targetScore))

        # clear canvas
        self.guiSurface.fill((1, 1, 1))
        self.guiSurface.set_colorkey((1, 1, 1))

        # Draw Modules
        for module in self.guiModules:
            module.update(game)
            module.draw(game['screen'])

        # Draw Mission Text
        gradientColor = (self.missionColor.r * 0.8, self.missionColor.g * 0.8, self.missionColor.b * 0.8)
        missionSurf = renderText(f'MISSION {self.level}', self.missionFont, self.missionColor, gradientColor, (50, 50, 50), (3, 3), (0, 0, 0), 2)
        missionWidth = missionSurf.get_width()
        missionHeight = missionSurf.get_height()
        x = game['screenWidth'] * 0.97 - missionWidth
        y = game['screenHeight'] * 0.03
        self.guiSurface.blit(missionSurf, (x, y))

        # Draw Score Bar
        scoreBarColor = pygame.Color(255, 255, 200)
        y = y + missionHeight

        # Outside
        pygame.draw.rect(self.guiSurface, scoreBarColor, pygame.Rect(x, y, missionWidth, missionHeight * 0.4), width=2)

        # Inside
        progress = min(1, self.score / self.targetScore)
        margin = 4
        pygame.draw.rect(self.guiSurface, scoreBarColor, pygame.Rect(x + margin, y + margin, (missionWidth - margin * 2) * progress, missionHeight * 0.4 - margin * 2))

        # Draw Health Text
        gradientColor = (self.healthColor.r * 0.8, self.healthColor.g * 0.8, self.healthColor.b * 0.8)
        healthSurf = renderText('HEALTH', self.healthFont, self.healthColor, gradientColor, (50, 50, 50), (3, 3), (0, 0, 0), 2)
        healthWidth = healthSurf.get_width()
        healthHeight = healthSurf.get_height()
        x = game['screenWidth'] * 0.03
        y = game['screenHeight'] * 0.03
        self.guiSurface.blit(healthSurf, (x, y))

        # Draw Health Bar
        if len(game['players']) > 0:
            player = game['players'][0]
            self.healthLength = healthWidth * player.maxHealth / 2
        scoreBarColor = pygame.Color(200, 255, 200)
        y = y + healthHeight

        # Outside
        pygame.draw.rect(self.guiSurface, scoreBarColor, pygame.Rect(x, y, self.healthLength, healthHeight * 0.4), width=2)

        # Inside
        progress = 0
        if len(game['players']) > 0:
            player = game['players'][0]
            progress = player.health / player.maxHealth
        margin = 4
        pygame.draw.rect(self.guiSurface, scoreBarColor, pygame.Rect(x + margin, y + margin, (self.healthLength - margin * 2) * progress, healthHeight * 0.4 - margin * 2))

async def drawStars(surf:pygame.Surface, points:list, game:dict):

    offsetX = -game['scrollX']
    offsetY = -game['scrollY']

    for x, y, color in points:

        x = (x + offsetX) % game['gameWidth']
        y = (y + offsetY) % game['gameHeight']

        if x < 0 or x > game['screenWidth']:
            continue

        if y < 0 or y > game['screenHeight']:
            continue
        
        pygame.draw.circle(surf, color, (x, y), 1)

class ReduxGuiBar:
    def __init__(self, x, y, width, height, font, textColor, text, insideColor, outsideColor, progressFunction=lambda:1):
        # Assign Variables
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.textColor = textColor
        self.gradientColor = pygame.Color(textColor.r * 0.8, textColor.g * 0.8, textColor.b * 0.8)
        self.text = text
        self.insideColor = insideColor
        self.outsideColor = outsideColor
        self.progress = 1
        self.progressFunction = progressFunction

    def update(self, game):
        if len(game['players']) > 0:
            self.progress = self.progressFunction(game)

    def draw(self, surf):
        # Draw Text
        textSurf = renderText(self.text, self.font, self.textColor, self.gradientColor, (50, 50, 50), (3, 3), (0, 0, 0), 2)
        textHeight = textSurf.get_height()
        x = self.x
        y = self.y
        surf.blit(textSurf, (x - 5, y + 5))

        # Draw Score Bar
        y = y + textHeight

        # Outside
        pygame.draw.rect(surf, self.outsideColor, pygame.Rect(x, y, self.width, self.height), width=2)

        # Inside
        margin = 4
        pygame.draw.rect(surf, self.insideColor, pygame.Rect(x + margin, y + margin, (self.width - margin * 2) * self.progress, self.height - margin * 2))

class ReduxClock:
    def __init__(self, surface:pygame.Surface, font:pygame.Font, time:float=60, mode:int=0):
        self.surf = surface
        self.font = font
        self.time = time
        self.mode = mode # 0 = seconds only, 1 = minutes:seconds

        self.startColor = pygame.Color(255, 255, 150)
        self.endColor = pygame.Color(200, 200, 150)

    def update(self, game:dict, updateClock=True):
        if updateClock:
            self.time -= game['frametime'] / 1000
        self.draw(self.surf, game)

    def draw(self, surf:pygame.Surface, game:dict):
        # Set text
        if self.mode == 0:
            text = str(int(self.time))
        elif self.mode == 1:
            minutes = int(self.time / 60)
            seconds = int(self.time % 60)
            text = f'{minutes}:{seconds}'

        # Render text
        textSurf = renderText(text, self.font, self.startColor, self.endColor, (50, 50, 50), (3, 3), (0, 0, 0), 2)
        width = textSurf.get_width()
        x = game['screenWidth'] / 2 - width / 2
        y = game['screenHeight'] * 0.02
        surf.blit(textSurf, (x, y))
