import math
import pygame

class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.width = 40
        self.height = 20
        self.max_speed = 5
        self.max_reverse_speed = -3
        self.acceleration = 0.2
        self.turn_speed = 3

    def update(self, steering, throttle, brake, obstacles):
        # Marche avant / marche arrière
        if throttle > 0:
            self.speed += self.acceleration * throttle
        elif throttle < 0:
            self.speed += self.acceleration * throttle  # diminue la vitesse => recule
        elif brake > 0:
            self.speed = 0
        else:
            self.speed *= 0.95

        self.speed = max(self.max_reverse_speed, min(self.speed, self.max_speed))

        self.angle += steering * self.turn_speed

        rad = math.radians(self.angle)
        new_x = self.x + math.cos(rad) * self.speed
        new_y = self.y + math.sin(rad) * self.speed

        old_x, old_y = self.x, self.y
        self.x, self.y = new_x, new_y

        if self.check_collision(obstacles):
            self.x, self.y = old_x, old_y
            self.speed = 0

    def get_rect(self):
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )

    def check_collision(self, obstacles):
        robot_rect = self.get_rect()
        return any(robot_rect.colliderect(obs) for obs in obstacles)

    def draw(self, screen):
        rect = self.get_rect()
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surface.fill((0, 200, 255))
        rotated = pygame.transform.rotate(surface, -self.angle)
        screen.blit(rotated, rotated.get_rect(center=rect.center))

    def get_sensor_data(self, obstacles):
        return [100, 100, 100]