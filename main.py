"""
Module providing main functions
"""

# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "numpy",
#   "asyncio",
#   "webbrowser",
#   "json",
#   "base64",
#   "pygame-ce"
# ]
# ///

import asyncio
import pygame

from libraries.stages.title import Title
from libraries.stages.classic import Classic
from libraries.stages.gameover import Gameover
from libraries.services.ngio import NGIO
from libraries.stages.redux import Redux
from libraries.stages.leaderboards import Leaderboards
from libraries.stages.charSelect import CSSRedux, CSSClassic
from libraries.stages.worldMap import WorldMap


def initGame():
    return {
        'NGIO': NGIO(),
        'screenWidth': 640,
        'screenHeight': 480,
        'gameWidth': 640,
        'gameHeight': 480,
        'scrollX': 0,
        'scrollY': 0,
        'frametime': 0,
        'screen': pygame.display.set_mode((640, 480)),
        'layers': [pygame.surface.Surface((640, 480)) for _ in range(3)],
        'background': pygame.surface.Surface((640, 480)),
        'lives': 1,
        'players': [],
        'bullets': [],
        'enemies': [],
        'enemyBullets': [],
        'asteroids': [],
        'particles': [],
        'shipParts': [],
        'bulletWrap': False,
        'classes': ['scout', 'bomber', 'heavy'],
        'controls': {
            'keyUp': [pygame.K_UP],
            'keyDown': [pygame.K_DOWN],
            'keyLeft': [pygame.K_LEFT],
            'keyRight': [pygame.K_RIGHT],
            'keyFire': [pygame.K_SPACE, pygame.K_RETURN],
            'keySpecial': [pygame.K_LSHIFT],
            'keyPause': [pygame.K_ESCAPE]
        },
        'videoSettings': {
            'maxFPS': -1,
            'quality': 'high'
        },
        'audioSettings': {
            'master': 100,
            'music': 100,
            'sfx': 100
        }
    }

async def main():

    # Variables
    pygame.init()
    pygame.display.set_caption('Asteroids: Redux')
    clock = pygame.time.Clock()
    game = initGame()
    
    # Create Background
    game['background'].fill((0, 0, 0))
    
    stage = Title(game)

    # Main game loop
    while True:

        # Set the max framerate
        if game['videoSettings']['maxFPS'] == -1:
            game['frametime'] = clock.tick(9999)
        else:
            game['frametime'] = clock.tick(game['videoSettings']['maxFPS'])

        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        await game['NGIO'].update(game)

        update = await stage.update(game)
        
        if type(update) is str:
            stage = {'Title': Title, 
                    'Classic': Classic, 
                    'Gameover': Gameover,
                    'Redux': Redux,
                    'Leaderboards': Leaderboards,
                    'CSSRedux': CSSRedux,
                    'WorldMap': WorldMap,
                    'CSSClassic': CSSClassic}[update](game)

        # Update the Async IO
        await asyncio.sleep(0)
            
asyncio.run(main())
