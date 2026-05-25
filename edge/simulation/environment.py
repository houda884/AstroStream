import pygame

class Environment:
    def __init__(self):
        self.obstacles = [
            pygame.Rect(150, 120, 100, 60),
            pygame.Rect(500, 200, 120, 80),
            pygame.Rect(250, 400, 150, 50),
        ]

    def draw(self, screen):
        for obs in self.obstacles:
            pygame.draw.rect(screen, (255, 80, 80), obs)