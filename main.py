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
        'bulletWrap': False
    }

async def main():

    # Variables
    pygame.init()
    pygame.display.set_caption('Asteroids: Redux')
    clock = pygame.time.Clock()
    game = initGame()

    # NGIO
    if game['NGIO'].sessionID is not None:
        await game['NGIO'].checkSessionLogin()
    else:
        await game['NGIO'].newSession()

    # Create Background
    game['background'].fill((0, 0, 0))
    
    stage = Title(game)

    # Main game loop
    while True:
        # Set the max framerate
        game['frametime'] = clock.tick(9999)

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
                     'Leaderboards': Leaderboards}[update](game)

        # Update the Async IO
        await asyncio.sleep(0)
            
asyncio.run(main())
