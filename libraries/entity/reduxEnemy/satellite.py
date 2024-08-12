import pygame


shape = [
        [(0, -1), (1, 0), (0.75, 0.25), (-0.25, -0.75)],
        [(-0.75, -0.25), (0.25, 0.75), (0, 1), (-1, 0)],
        [(0, -0.25), (0.25, -0.25), (0.25, 0), (0, 0.25), (-0.25, 0.25), (-0.25, 0)]
        ]

hitboxShape = [(0, -1), (1, 0), (0.75, 0.25), (0.25, -0.25), (0.25, 0), (0, 0.25), (-0.25, 0.25), (0.25, 0.75), (0, 1), (-1, 0), (-0.75, -0.25), (-0.25, 0.25), (-0.25, 0), (0, -0.25), (0.25, -0.25), (-0.25, -0.75)]

class Satellite:
    """
    Class for satellite
    """
    def __init__(self, x:float, y:float, size:float, x_vel:float=0, y_vel:float=0):
        self.x = x
        self.y = y
        self.size = size
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.points = shape
        self.health = 1
        self.updatePosition()

        # Set the value
        self.value = 10

    def update(self, game:dict):
        self.updatePosition(game)
        self.draw(game)
        return self.health > 0

    def updatePosition(self, game:dict={}):
        if game != {}:
            # Apply velocity
            self.x = (self.x + self.x_vel * (game['frametime'] / 1000)) % game['gameWidth']
            self.y = (self.y + self.y_vel * (game['frametime'] / 1000)) % game['gameHeight']

        # Update the position
        self.points = [[(point[0] * self.size + self.x, point[1] * self.size + self.y) for point in part] for part in shape]
        self.hitbox = [(point[0] * self.size + self.x, point[1] * self.size + self.y) for point in hitboxShape]
        
    def draw(self, game:dict):
        """
        Args:
            game (dict): The game dict
        """

        scrollOffsetX = - game['scrollX']
        scrollOffsetY = - game['scrollY']
        
        drawX = [0]
        drawY = [0]
        
        # draw at y - gameHeight
        if self.y + self.size + scrollOffsetY > game['gameHeight']:
            drawY.append(-game['gameHeight'])

        # draw at y + gameHeight
        if self.y - self.size + scrollOffsetY < 0:
            drawY.append(game['gameHeight'])

        # draw ship at x - gameWidth
        if self.x + self.size + scrollOffsetX > game['gameWidth']:
            drawX.append(-game['gameWidth'])

        # draw ship at x + gameWidth
        if self.x - self.size + scrollOffsetX < 0:
            drawX.append(game['gameWidth'])

        # draw self
        for x in drawX:
            for y in drawY:
                for index in range(len(self.points)):
                    p = [(point[0] + x - 1 + scrollOffsetX, point[1] + y - 1 + scrollOffsetY) for point in self.points[index]]
                    # offset by 1 pixel to account for anti aliasing
                    pygame.draw.polygon(game['layers'][2], pygame.Color(0, 0, 0, 255), p)
                    pygame.draw.aalines(game['layers'][2], pygame.Color(255, 0, 0, 255), True, p)

