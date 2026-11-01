import math

import pygame
from pygame import Vector2

from Ball import Ball
from Circle import Circle
from utils import utils


class Ring:
    """Кільце однієї висоти ноти. Радіус і колір задає висота ноти (pitch)."""

    def __init__(self, radius, color, maxTime, rotateDir, startAngle=-90):
        self.radius = radius
        self.color = color
        self.maxTime = maxTime
        self.rotateDir = rotateDir
        self.startAngle = startAngle
        self.center = Vector2(utils.width / 2, utils.height / 2)
        self.dots = []
        self.ball = Ball(self._pos_at(0), 8, color)
        self.visible = False  # з'являється, коли вперше звучить нота цієї висоти

    def _pos_at(self, t):
        angle = self.startAngle + utils.map_value(t, 0, self.maxTime, 0, 360 * self.rotateDir)
        rad = math.radians(angle)
        return self.center + Vector2(math.cos(rad), math.sin(rad)) * self.radius

    def add_event(self, event, color):
        # тривалість ноти -> розмір точки (0..1.5 с -> 4..12 px)
        size = 4 + min(event['duration'], 1.5) / 1.5 * 8
        # color = колір доріжки: у спокої точка має приглушений контур цього кольору,
        # а в момент note_on спалахує кольором кільця
        dim = tuple(int(c * 0.55) for c in color)
        dot = Circle(self._pos_at(event['start']), size, self.color, dim)
        self.dots.append(dot)
        return dot

    def reset(self):
        self.visible = False
        for d in self.dots:
            d.pulse = 0

    def update(self, time, dt):
        self.ball.pos = self._pos_at(time)
        for d in self.dots:
            d.update(dt)

    def draw(self):
        if not self.visible:
            return
        pygame.draw.circle(utils.screen, self.color, self.center, self.radius, 2)
        for d in self.dots:
            d.draw()
        self.ball.draw()