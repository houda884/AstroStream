import pygame
import numpy as np

from .robot import Robot
from .environment import Environment
from .controls import Controls


class GameEngine:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("AstroStream Robot Simulation")

        self.render_surface = pygame.Surface((width, height))

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

        self.robot = Robot(400, 300)
        self.env = Environment()
        self.controls = Controls()
        self.running = True

    def update(self):
        self.clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    print("⚠️ SAFE MODE ACTIVÉ")
                    self.controls.safe_mode = True
                    self.controls.connection_alive = False
                    self.controls.emergency_stop()
                    self.robot.speed = 0

                if event.key == pygame.K_r:
                    print("✅ SAFE MODE DÉSACTIVÉ")
                    self.controls.safe_mode = False
                    self.controls.connection_alive = True
                    self.controls.steering = 0
                    self.controls.throttle = 0
                    self.controls.brake = 0
                    self.robot.speed = 0

        self.controls.update_keyboard_fallback()

        self.robot.update(
            self.controls.steering,
            self.controls.throttle,
            self.controls.brake,
            self.env.obstacles
        )

    def draw(self):
        self.render_surface.fill((30, 30, 30))
        self.env.draw(self.render_surface)
        self.robot.draw(self.render_surface)

        speed_text = self.font.render(
            f"Speed: {round(self.robot.speed, 2)}",
            True,
            (255, 255, 255)
        )
        self.render_surface.blit(speed_text, (10, 10))

        status = "SAFE MODE" if self.controls.safe_mode else "REMOTE OK"
        status_color = (255, 80, 80) if self.controls.safe_mode else (80, 255, 80)
        status_text = self.font.render(f"Status: {status}", True, status_color)
        self.render_surface.blit(status_text, (10, 35))

        help1 = self.font.render("S = SAFE MODE", True, (200, 200, 200))
        help2 = self.font.render("R = RESTORE", True, (200, 200, 200))
        self.render_surface.blit(help1, (10, 60))
        self.render_surface.blit(help2, (10, 85))

        self.screen.blit(self.render_surface, (0, 0))
        pygame.display.flip()

    def get_frame(self):
        frame = pygame.surfarray.array3d(self.render_surface)
        frame = np.transpose(frame, (1, 0, 2))
        frame = np.ascontiguousarray(frame, dtype=np.uint8)
        return frame

    def stop(self):
        pygame.quit()