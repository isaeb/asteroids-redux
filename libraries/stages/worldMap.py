import pygame
import math
from libraries.services.drawEffects import renderText, draw_rounded_rect
from libraries.constants import *
from random import randint, random, sample

pressedKeys = ['fire']
mapShape = [1, 3, 5, 5, 5, 3]
mapLength = 5
mapNodeCount = 21
cursorShape = [(-0.25, -1), (0.25, -1), (0, -0.5)]


class WorldMap:
    def __init__(self, game:dict):
        # Declare Variables
        self.sector = 0
        self.playerPosition = (0, 0)
        self.nodes = self.generateMap(game)
        self.selected = 0
        self.path = [0]

        # Create Surfaces
        self.nodeSurf = self.drawNodes(game)
        self.guiSurf = self.drawGUI(game)
        self.bgSurf = self.drawBackground(game)
        self.descSurf = self.drawDesc(game)

        # Create Header Surface
        headerFont = pygame.font.Font('fonts/SignwoodItalic.ttf', int(game['screenHeight'] * 0.15))
        self.headerSurf = renderText(f'SECTOR {self.sector + 1}', headerFont, (255, 100, 100), (150, 100, 100), (50, 50, 50), (5, 5), (0, 0, 0), 1)
        hx = game['screenWidth'] / 2 - self.headerSurf.get_width() / 2
        hy = game['screenHeight'] * 0.1 - self.headerSurf.get_height() / 2
        self.headerPos = (hx, hy)
    
    def drawDesc(self, game:dict):
        width = game['screenWidth']
        height = game['screenHeight'] * 0.2
        surface = pygame.surface.Surface((width, height), pygame.SRCALPHA)
        thickness = 1
        back = pygame.Rect(0, 0, width, height)
        oback = pygame.Rect(thickness, thickness, width - thickness * 2, height - thickness * 2)
        draw_rounded_rect(surface, (255, 255, 255), back, width * 0.02)
        draw_rounded_rect(surface, (0, 0, 0), oback, width * 0.02)
        return surface

    def update(self, game:dict):
        self.updateControl(game)

    def updateControl(self, game):
        y = self.playerPosition[1] + (5 - mapShape[self.playerPosition[0]]) / 2

        # Get player input
        keys = pygame.key.get_pressed()

        # Read player input
        if any([keys[key] for key in game['controls']['keyFire']]):
            if 'fire' not in pressedKeys:
                pressedKeys.append('fire')

                self.path.append(self.selected)
                self.playerPosition = (self.playerPosition[0] + 1, self.selected)
                self.selected = min(self.selected, mapShape[self.playerPosition[0] + 1] - 1)

                self.nodeSurf = self.drawNodes(game)
        else:
            if 'fire' in pressedKeys:
                pressedKeys.remove('fire')

        if any([keys[key] for key in game['controls']['keyUp']]):
            if 'up' not in pressedKeys:
                pressedKeys.append('up')
                self.selected -= 1
                ny = self.selected + (5 - mapShape[self.playerPosition[0] + 1]) / 2
                if abs(ny - y) > 1 or self.selected < 0:
                    self.selected += 1
                
                self.nodeSurf = self.drawNodes(game)
        else:
            if 'up' in pressedKeys:
                pressedKeys.remove('up')
        
        if any([keys[key] for key in game['controls']['keyDown']]):
            if 'down' not in pressedKeys:
                pressedKeys.append('down')
                self.selected += 1
                ny = self.selected + (5 - mapShape[self.playerPosition[0] + 1]) / 2
                if abs(ny - y) > 1 or self.selected >= mapShape[self.playerPosition[0] + 1]:
                    self.selected -= 1
                
                self.nodeSurf = self.drawNodes(game)
        else:
            if 'down' in pressedKeys:
                pressedKeys.remove('down')

        return None

    def draw(self, game:dict):
        game['screen'].blit(self.bgSurf, (0, 0))
        game['screen'].blit(self.guiSurf, (0, 0))
        game['screen'].blit(self.nodeSurf, (0, 0))
        game['screen'].blit(self.descSurf, (0, game['screenHeight'] * 0.8))
        game['screen'].blit(self.headerSurf, self.headerPos)

    def drawNodes(self, game:dict, nodeSize:int=15, width:int=3):
        surface = pygame.surface.Surface((game['screenWidth'], game['screenHeight']), pygame.SRCALPHA)
        
        prevNode = None
        for i, j in enumerate(self.path):
            node = self.nodes[i][j]
            if prevNode is not None:
                prevPosition = prevNode.position
                color = (150, 150, 150)
                pygame.draw.line(surface, color, node.position, prevPosition, width=width)
            
            color = (150, 150, 150)
            pygame.draw.circle(surface, color, node.position, nodeSize, width=width)
            prevNode = node

        y = self.playerPosition[1] + (5 - mapShape[self.playerPosition[0]]) / 2
        for i, node in enumerate(self.nodes[self.playerPosition[0] + 1]):
            ny = i + (5 - mapShape[self.playerPosition[0] + 1]) / 2
            if abs(ny - y) > 1:
                continue

            if i == self.selected:
                color = (255, 0, 0)
                pygame.draw.line(surface, color, node.position, prevNode.position, width=width)

                pygame.draw.circle(surface, (255, 0, 0), node.position, nodeSize)

                color = (255, 255, 255)
                pygame.draw.circle(surface, color, node.position, nodeSize, width=width)

                # Draw Cursor
                cSize = nodeSize * 2
                p = [(node.position[0] + cPoint[0] * cSize, node.position[1] + cPoint[1] * cSize - nodeSize) for cPoint in cursorShape]
                pygame.draw.lines(surface, pygame.Color(255, 255, 255), True, p, width=int(width / 2))
                
            else:
                color = (150, 150, 150)
                draw_dotted_line(surface, color, node.position, prevNode.position, dot_radius=2, spacing=15)
                color = (150, 150, 150)
                pygame.draw.circle(surface, color, node.position, nodeSize, width=width)
                
        return surface

    def drawBackground(self, game:dict):
        surface = pygame.surface.Surface((game['screenWidth'], game['screenHeight']), pygame.SRCALPHA)
        surface.fill((0, 0, 0))
        return surface

    def drawGUI(self, game:dict):
        return pygame.surface.Surface((game['screenWidth'], game['screenHeight']), pygame.SRCALPHA)

    def generateMap(self, game:dict, upperGutter:float=0.2, lowerGutter:float=0.2):
        enemyMap = self.generateEnemyMap(game)
        asteroidMap = self.generateAsteroidMap(game)

        # Place Galactic Stations
        galacticStations = 8 - self.sector
        newMap = [[None for _ in range(i)] for i in mapShape if i > 1]
        for station in range(galacticStations):
            while True:
                i = randint(0, mapNodeCount - 1) # Random index
                x = 0
                y = 0
                while i > 0:
                    i -= 1
                    y += 1
                    if y > mapShape[x + 1] - 1:
                        y = 0
                        x += 1
                if newMap[x][y] is None:
                    if station > galacticStations / 2:
                        newMap[x][y] = ('galactic', 'repair')
                    else:
                        newMap[x][y] = ('galactic', 'upgrade')
                    break

        # Fill Hostile Nodes
        for x, col in enumerate(newMap):
            for y, value in enumerate(col):
                if value is None:
                    newMap[x][y] = (enemyMap[x][y], asteroidMap[x][y])

        # Place Nodes
        screenRatio = 1 - upperGutter - lowerGutter
        nodes = []
        for i, count in enumerate(mapShape):
            nodeLayer = []
            for j in range(count):
                x = ((i + 1) / (len(mapShape) + 1)) * game['screenWidth']
                y = ((j + 1) / (count + 1)) * game['screenHeight'] * screenRatio + upperGutter * game['screenHeight']
                nodeLayer.append(Node(position=(x, y)))
            nodes.append(nodeLayer)
        return nodes

    def generateEnemyMap(self, game:dict):
        enemyMap = [['' for _ in range(5)] for _ in range(mapLength)]
        while any('' in col for col in enemyMap):
            # Pick a random faction
            faction = FACTIONS[randint(0, len(FACTIONS) - 1)]

            # Pick a random size
            rad = random() * 2

            # Pick random coordinates
            x = randint(0, 4)
            y = randint(0, 4)

            # Apply to map
            for mx in range(mapLength):
                for my in range(5):
                    if math.sqrt(abs(x - mx) ** 2 + abs(y - my) ** 2) <= rad:
                        enemyMap[mx][my] = faction
        return enemyMap
    
    def generateAsteroidMap(self, game:dict):
        asteroidMap = [['' for _ in range(5)] for _ in range(mapLength)]
        while any('' in col for col in asteroidMap):
            # Pick a random faction
            density = DENSITIES[randint(0, len(DENSITIES) - 1)]

            # Pick a random size
            rad = random() * 2

            # Pick random coordinates
            x = randint(0, 4)
            y = randint(0, 4)

            # Apply to map
            for mx in range(mapLength):
                for my in range(5):
                    if math.sqrt(abs(x - mx) ** 2 + abs(y - my) ** 2) <= rad:
                        asteroidMap[mx][my] = density
        return asteroidMap


class Node:
    def __init__(self, position:tuple=(0, 0), faction:str='', asteroids:str='', repair:bool=False, upgrade:bool=False):
        self.faction = faction
        self.asteroids = asteroids
        self.position = position
        self.title = {'asteroid':'Asteroid Belt'}


def draw_dotted_line(surface, color, start_pos, end_pos, dot_radius=5, spacing=20):
    # Calculate the total distance between start_pos and end_pos
    distance = math.sqrt((end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2)
    
    # Calculate the number of dots based on the distance and spacing
    num_dots = int(distance / spacing)
    
    # Calculate the direction vector between the start and end positions
    direction = ((end_pos[0] - start_pos[0]) / distance, (end_pos[1] - start_pos[1]) / distance)
    
    for i in range(num_dots + 1):
        # Calculate the position of each dot
        dot_pos = (
            start_pos[0] + direction[0] * i * spacing,
            start_pos[1] + direction[1] * i * spacing
        )
        # Draw the dot as a small circle
        pygame.draw.circle(surface, color, (int(dot_pos[0]), int(dot_pos[1])), dot_radius)