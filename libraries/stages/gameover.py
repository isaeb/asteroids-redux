import pygame
import math

pressedKeys = []

thickness = 3

class Gameover:
    def __init__(self, game):

        self.options = {'RETRY':'Classic', 'QUIT':'Title'}
        self.width = game['screenWidth']
        self.height = game['screenHeight']
        self.titleSize = self.height / 4
        self.optionSize = self.height / 12

        self.selected = 0

        # Define the font
        self.optionFont = pygame.font.Font('fonts/PastiRegular.otf', int(self.optionSize))
        
        # Initialize the title surface
        self.headerSurface = pygame.surface.Surface((self.width, self.titleSize + thickness * 2))
        self.headerSurface.fill((1, 1, 1))
        self.headerSurface.set_colorkey((1, 1, 1))

        # Define the font
        self.titleFont = pygame.font.Font('fonts/PastiRegular.otf', int(self.titleSize))

        # Draw the title outline
        for angle in range(8):
            textSurface = self.titleFont.render('GAME OVER', True, (0, 0, 0))
            offsetX = (self.width - textSurface.get_size()[0]) / 2
            offsetY = thickness
            x = offsetX + math.cos(math.pi * angle / 4) * thickness
            y = offsetY + math.sin(math.pi * angle / 4) * thickness
            self.headerSurface.blit(textSurface, (x, y))
        
        # Draw the title main text
        textSurface = self.titleFont.render('GAME OVER', True, (255, 255, 255))
        x = (self.width - textSurface.get_size()[0]) / 2
        y = thickness
        self.headerSurface.blit(textSurface, (x, y))

        self.drawOptions()

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

        # Draw the header
        game['screen'].blit(self.headerSurface, (0, self.height * 0.1))

        # Draw the option
        game['screen'].blit(self.optionSurface, (0, self.height * 0.4))
        
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
                self.drawOptions()
        else:
            if pygame.K_UP in pressedKeys:
                pressedKeys.remove(pygame.K_UP)
        
        if keys[pygame.K_DOWN]:
            if pygame.K_DOWN not in pressedKeys:
                pressedKeys.append(pygame.K_DOWN)
                self.selected = min(len(self.options) - 1, self.selected + 1)
                self.drawOptions()
        else:
            if pygame.K_DOWN in pressedKeys:
                pressedKeys.remove(pygame.K_DOWN)

        return None

        self.optionSurface = pygame.surface.Surface((self.width, len(self.options) * (self.optionSize + thickness * 2)))
        self.optionSurface.fill((1, 1, 1))
        self.optionSurface.set_colorkey((1, 1, 1))
        for index, key in enumerate(self.options.keys()):

            # Draw the option outline
            for angle in range(8):
                textSurface, rect = self.optionFont.render(key, (0, 0, 0))
                offsetX = (self.width - rect[2]) / 2
                offsetY = thickness + index * (self.optionSize + thickness * 2)
                x = offsetX + math.cos(math.pi * angle / 4) * thickness
                y = offsetY + math.sin(math.pi * angle / 4) * thickness
                self.optionSurface.blit(textSurface, (x, y))

            # Draw the option main text
            color = (255, 255, 255)
            if index == self.selected:
                color = (255, 255, 0)
            textSurface, rect = self.optionFont.render(key, color)
            x = (self.width - rect[2]) / 2
            y = thickness + index * (self.optionSize + thickness * 2)
            self.optionSurface.blit(textSurface, (x, y))

    def drawOptions(self):

        self.optionSurface = pygame.surface.Surface((self.width, len(self.options) * (self.optionSize + thickness * 2)))
        self.optionSurface.fill((1, 1, 1))
        self.optionSurface.set_colorkey((1, 1, 1))
        for index, key in enumerate(self.options.keys()):

            # Draw the option outline
            for angle in range(8):
                textSurface = self.optionFont.render(key, True, (0, 0, 0))
                offsetX = (self.width - textSurface.get_size()[0]) / 2
                offsetY = thickness + index * (self.optionSize + thickness * 2)
                x = offsetX + math.cos(math.pi * angle / 4) * thickness
                y = offsetY + math.sin(math.pi * angle / 4) * thickness
                self.optionSurface.blit(textSurface, (x, y))

            # Draw the option main text
            color = pygame.Color(255, 255, 255)
            if index == self.selected:
                color = (255, 255, 0)
            textSurface = self.optionFont.render(key, True, color)
            x = (self.width - textSurface.get_size()[0]) / 2
            y = thickness + index * (self.optionSize + thickness * 2)
            self.optionSurface.blit(textSurface, (x, y))
