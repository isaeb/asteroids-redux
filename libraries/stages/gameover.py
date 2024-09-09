import pygame
import math

from libraries.services.drawEffects import renderText, create_vignette_surface
from libraries.services.fallingStarBackground import FallingStarBackground as BG

pressedKeys = []

thickness = 3

class Gameover:
    def __init__(self, game):

        self.options = {'TRY AGAIN':f'{game['last']}', 'LEADERBOARDS':'Leaderboards', 'MAIN MENU':'Title'}
        width = game['screenWidth']
        height = game['screenHeight']
        self.titleSize = height / 4
        self.scoreSize = height / 16
        self.optionSize = height / 20

        self.selected = 0

        # Darken Background
        self.fadeout = 1
        self.darkSurf = pygame.Surface((game['screenWidth'], game['screenHeight']), pygame.SRCALPHA)
        transparent_color = (0, 0, 0, 255 - 255 * self.fadeout)
        self.darkSurf.fill(transparent_color)

        # Set up vignette
        self.vignetteSurf = create_vignette_surface((game['screenWidth'], game['screenHeight']), (0, 0, 0), game['screenWidth'] * 0.45)

        # Create bg
        self.bg = BG()
        self.bgAlpha = 0
        self.bgSurf = pygame.surface.Surface((width, height), pygame.SRCALPHA)
        
        self.refreshGui(game)

    async def update(self, game:dict):

        game['screen'].blit(game['background'], (0, 0))
        
        for layer in game['layers']:
            layer.fill((1, 1, 1))
            layer.set_colorkey((1, 1, 1))

        # Update Player
        game['players'] = [player for player in game['players'] if player.update(game)]

        # Update Bullets
        game['bullets'] = [bullet for bullet in game['bullets'] if bullet.update(game)]

        # Update Asteroids
        game['asteroids'] = [asteroids for asteroids in game['asteroids'] if asteroids.update(game)]

        # Update Particles
        game['particles'] = [particle for particle in game['particles'] if particle.update(game)]

        # Update Enemies
        game['enemies'] = [enemy for enemy in game['enemies'] if enemy.update(game)]

        # Update Enemy Bullets
        game['enemyBullets'] = [bullet for bullet in game['enemyBullets'] if bullet.update(game)]
        
        # Update Ship Parts
        game['shipParts'] = [shipPart for shipPart in game['shipParts'] if shipPart.update(game)]

        # Update the display
        for layer in game['layers']:
            game['screen'].blit(layer, (0, 0))

        # Darken
        self.fadeout = max(0, self.fadeout - game['frametime'] / 1000)
        transparent_color = (0, 0, 0, 255 - 255 * self.fadeout)
        self.darkSurf.fill(transparent_color)
        game['screen'].blit(self.darkSurf, (0, 0))

        if self.fadeout < 0.5:
            self.bgAlpha = min(1, self.bgAlpha + game['frametime'] / 1000)
            self.bg.update(game)
            self.bgSurf.fill((0, 0, 0))
            self.bg.draw(self.bgSurf, game)
            self.bgSurf.set_alpha(255 * self.bgAlpha)
            game['screen'].blit(self.bgSurf, (0, 0))

        # Draw Vignette
        game['screen'].blit(self.vignetteSurf, (0, 0))

        # Draw the header
        self.headerSurface.set_alpha(255 - 255 * self.fadeout)
        game['screen'].blit(self.headerSurface, (self.hX, self.hY))

        # Draw the score
        self.scoreSurface.set_alpha(255 - 255 * self.fadeout)
        game['screen'].blit(self.scoreSurface, (self.sX, self.sY))

        # Draw the option
        self.optionSurface.set_alpha(255 - 255 * self.fadeout)
        game['screen'].blit(self.optionSurface, (0, 0))
        
        pygame.display.flip()

        return self.updateControl(game)

    def updateControl(self, game):

        # Get player input
        keys = pygame.key.get_pressed()

        # Read player input
        if keys[pygame.K_SPACE]:
            if pygame.K_SPACE not in pressedKeys:
                pressedKeys.append(pygame.K_SPACE)
                return list(self.options.values())[self.selected]
        else:
            if pygame.K_SPACE in pressedKeys:
                pressedKeys.remove(pygame.K_SPACE)

        if keys[pygame.K_UP]:
            if pygame.K_UP not in pressedKeys:
                pressedKeys.append(pygame.K_UP)
                self.selected = max(0, self.selected - 1)
                self.refreshGui(game)
        else:
            if pygame.K_UP in pressedKeys:
                pressedKeys.remove(pygame.K_UP)
        
        if keys[pygame.K_DOWN]:
            if pygame.K_DOWN not in pressedKeys:
                pressedKeys.append(pygame.K_DOWN)
                self.selected = min(len(self.options) - 1, self.selected + 1)
                self.refreshGui(game)
        else:
            if pygame.K_DOWN in pressedKeys:
                pressedKeys.remove(pygame.K_DOWN)

        return None

    def refreshGui(self, game):
        width = game['screenWidth']
        height = game['screenHeight']

        # Initialize the title surface
        headerFont = pygame.font.Font('fonts/Signwood.ttf', int(self.titleSize))
        startColor = (200, 0, 0)
        endColor = (200, 100, 100)
        shadowColor = (50, 0, 0)
        self.headerSurface = renderText('GAMEOVER', headerFont, startColor, endColor, shadowColor, (8, 8), (0, 0, 0), 2)
        self.hX = width / 2 - self.headerSurface.get_width() / 2
        self.hY = height / 8

        # Initialize the score surface
        scoreFont = pygame.font.Font('fonts/Signwood.ttf', int(self.scoreSize))
        startColor = (200, 200, 200)
        endColor = (150, 150, 150)
        shadowColor = (50, 50, 50)
        self.scoreSurface = renderText(f'Score: {game['score']}', scoreFont, startColor, endColor, shadowColor, (3, 3))
        self.sX = width / 2 - self.scoreSurface.get_width() / 2
        self.sY = height / 8 + self.headerSurface.get_height()

        # Options
        self.optionSurface = pygame.surface.Surface((width, height))
        self.optionSurface.fill((1, 1, 1))
        self.optionSurface.set_colorkey((1, 1, 1))
        
        font = pygame.font.Font('fonts/Signwood.ttf', int(self.optionSize))
        shadowColor = (50, 50, 50)
        x = 0
        y = self.sY + self.scoreSurface.get_height() * 2
        for index, key in enumerate(self.options.keys()):
            if index == self.selected:
                startColor = (220, 220, 220)
                endColor = (120, 120, 120)
            else:
                startColor = (100, 100, 100)
                endColor = (50, 50, 50)
            textSurface = renderText(key, font, startColor, endColor, shadowColor, (3, 3))
            x = width / 2 - textSurface.get_width() / 2
            self.optionSurface.blit(textSurface, (x, y))
            y += textSurface.get_height()
