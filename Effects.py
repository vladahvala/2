import pygame.draw

from utils import utils


class Ripple:
    """Хвиля, що розходиться від кільця в момент note_on."""

    LIFE = 1.0  # секунд

    def __init__(self, center, radius, color, speed):
        self.center = center
        self.radius = radius
        self.color = color
        self.speed = speed
        self.age = 0.0

    def update(self, dt):
        self.age += dt

    def alive(self):
        return self.age < self.LIFE

    def draw(self):
        k = max(0.0, 1.0 - self.age / self.LIFE)  # затухання до чорного фону
        color = tuple(int(c * k) for c in self.color)
        r = int(self.radius + self.age * self.speed)
        pygame.draw.circle(utils.screen, color, self.center, r, 2)