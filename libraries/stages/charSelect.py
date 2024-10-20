import pygame

from libraries.services.drawEffects import renderText, draw_player, draw_wrapped_text
from libraries.services.fallingStarBackground import FallingStarBackground as bg
from libraries.entity.player import Player
from math import pi, cos, sin
from libraries.constants import *
from json import load

pressedKeys = ['fire']


class CharSelect:
    def __init__(self, game, nextStage):
        self.nextStage = nextStage
        self.bg = bg()

        self.players = [Player(0, 0, 0, 0) for _ in game['classes']]
        for index, player in enumerate(self.players):
            game['class'] = game['classes'][index]
            player.updateStats(game)

        self.classAngles = [(index / len(self.players)) * pi * 2 for index in range(len(self.players))]

        self.selected = 0
        self.angle = 0
        self.targetAngle = 0
        self.rotationSpeed = pi * 8 / len(self.players)

        self.classNameFont = pygame.font.Font('fonts/Signwood.ttf', int(game['screenHeight'] * 0.15))
        self.descFont = pygame.font.Font('fonts/Signwood.ttf', int(game['screenHeight'] * 0.04))
        self.scoreFont = pygame.font.Font('fonts/Signwood.ttf', int(game['screenHeight'] * 0.08))

        self.fadeout = 1
        self.fadeoutSurf = pygame.Surface((game['screenWidth'], game['screenHeight']))
        self.fadeoutSurf.fill((0, 0, 0))

        self.exiting = 0

        # Opening JSON file
        with open('libraries/classInfo.json') as json_file:
            self.classInfo = load(json_file)

        self.info = self.classInfo[game['classes'][self.selected]]
        
    async def update(self, game):
        if self.exiting == 0:
            self.updateControl(game)
            self.fadeout = max(0, self.fadeout - game['frametime'] / 1000)
        else:
            self.exiting -= game['frametime'] / 1000
            self.fadeout = 1 - self.exiting
            if self.exiting <= 0:
                game['class'] = game['classes'][self.selected]
                return self.nextStage

        delta = self.targetAngle * self.rotationSpeed * game['frametime'] / 1000
        if abs(delta) > abs(self.targetAngle):
            delta = self.targetAngle

        self.angle += delta
        self.targetAngle -= delta

        game['screen'].fill((0, 0, 0))

        self.bg.update(game)
        self.bg.draw(game['screen'], game)

        classNameSurf = renderText(game['classes'][self.selected], self.classNameFont, SELECTED_TEXT_START, SELECTED_TEXT_END, SELECTED_SHADOW, (3, 3), outline_width=1)
        position = (game['screenWidth'] / 2 - classNameSurf.get_width() / 2, game['screenHeight'] * 0.65)
        game['screen'].blit(classNameSurf, position)

        self.drawInfo(game)

        self.drawClasses(game['screen'], game)

        if self.fadeout > 0:
            self.fadeoutSurf.set_alpha(self.fadeout * 255)
            game['screen'].blit(self.fadeoutSurf, (0, 0))

        pygame.display.flip()
    
    def drawClasses(self, surf, game:dict):
        drawQueue = []
        for index in range(len(self.players)):
            depth = cos(self.classAngles[index] + self.angle)
            x = sin(self.classAngles[index] + self.angle)
            drawQueue.append((depth, x, index))

        drawQueue.sort(key=lambda d: d[0])

        for d in drawQueue:
            index = d[2]
            x = game['screenWidth'] / 2 + d[1] * game['screenWidth'] * 0.2
            y = game['screenHeight'] * 0.35 + d[0] * game['screenHeight'] * 0.1
            depth = (d[0] + 1) / 2
            draw_player(surf, (255, 255, 255), (0, 0, 0), (x, y), game['screenWidth'] / 16 + depth * game['screenWidth'] / 8, self.players[index], width=2)

    def drawInfo(self, game:dict):
        # Draw description
        kwargs = {
            'surface': game['screen'],
            'text': self.info['desc'],
            'font': self.descFont,
            'rect': pygame.Rect(game['screenWidth'] * 0.2,
                                game['screenHeight'] * 0.85,
                                game['screenWidth'] * 0.6,
                                9999),
            'startColor': SELECTED_TEXT_START,
            'endColor': SELECTED_TEXT_END,
            'shadowColor': SELECTED_SHADOW
        }
        draw_wrapped_text(**kwargs)

        kwargs = {
            'text': 'Best Score: 9999',
            'font': self.scoreFont,
            'start_color': SELECTED_TEXT_START,
            'end_color': SELECTED_TEXT_END,
            'shadow_color': SELECTED_SHADOW,
            'shadow_offset': (2, 2),
            'outline_color': (0, 0, 0),
            'outline_width': 1
        }
        position = (game['screenWidth'] * 0.05, game['screenHeight'] * 0.05)
        game['screen'].blit(renderText(**kwargs), position)

    def updateControl(self, game:dict):

        # Get player input
        keys = pygame.key.get_pressed()

        # Read player input
        if any([keys[key] for key in game['controls']['keyFire']]):
            if 'fire' not in pressedKeys:
                pressedKeys.append('fire')
                self.exiting = 1
        elif not any([keys[key] for key in game['controls']['keyFire']]):
            if 'fire' in pressedKeys:
                pressedKeys.remove('fire')

        if any([keys[key] for key in game['controls']['keyLeft']]):
            if 'left' not in pressedKeys:
                pressedKeys.append('left')
                self.selected = (self.selected - 1) % len(self.players)
                self.info = self.classInfo[game['classes'][self.selected]]
                self.targetAngle = (self.targetAngle + pi * 2 / len(self.players))
        elif not any([keys[key] for key in game['controls']['keyLeft']]):
            if 'left' in pressedKeys:
                pressedKeys.remove('left')
        
        if any([keys[key] for key in game['controls']['keyRight']]):
            if 'right' not in pressedKeys:
                pressedKeys.append('right')
                self.selected = (self.selected + 1) % len(self.players)
                self.info = self.classInfo[game['classes'][self.selected]]
                self.targetAngle = (self.targetAngle - pi * 2 / len(self.players))
        elif not any([keys[key] for key in game['controls']['keyRight']]):
            if 'right' in pressedKeys:
                pressedKeys.remove('right')
        return None
    
class CSSRedux(CharSelect):
    def __init__(self, game):
        super().__init__(game, 'Redux')

class CSSClassic(CharSelect):
    def __init__(self, game):
        super().__init__(game, 'Classic')
