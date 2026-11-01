import pygame.draw

from utils import utils


class Circle:
    """Точка на кільці = одна нота. Розмір залежить від тривалості, колір від доріжки."""

    def __init__(self, pos, radius, color=(233, 233, 233), outline=(110, 110, 110)):
        self.pos = pos
        self.radius = radius
        self.color = color      # колір спалаху (колір кільця)
        self.outline = outline  # колір контуру в спокої (колір доріжки, приглушений)
        self.pulse = 0.0  # 1.0 у момент note_on, згасає до 0

    def trigger(self):
        self.pulse = 1.0

    def update(self, dt):
        self.pulse = max(0.0, self.pulse - dt * 2)

    def draw(self):
        if self.pulse > 0:
            r = int(self.radius * (1 + self.pulse))
            pygame.draw.circle(utils.screen, self.color, self.pos, r)
        else:
            pygame.draw.circle(utils.screen, self.outline, self.pos, int(self.radius), 2)