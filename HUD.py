import pygame

from Game import TRACK_COLORS
from utils import utils

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

BG = (18, 18, 24)
EDGE = (50, 50, 60)
TEXT = (220, 220, 225)
DIM = (130, 130, 140)
ACCENT = (255, 220, 120)


def note_name(n):
    return f"{NOTE_NAMES[n % 12]}{n // 12 - 1}"


class HUD:
    """Ліва панель: статус, легенда доріжок, відповідність MIDI -> анімація,
    керування і журнал останніх MIDI-подій."""

    def __init__(self):
        self.title = pygame.font.Font(None, 30)
        self.font = pygame.font.Font(None, 22)
        self.small = pygame.font.Font(None, 19)
        self.x = 16

    def _text(self, font, s, color, y, x=None):
        utils.screen.blit(font.render(s, True, color), (self.x if x is None else x, y))
        return y + font.get_height() + 3

    def draw(self, game):
        w, h = utils.hud_width, utils.height
        pygame.draw.rect(utils.screen, BG, (0, 0, w, h))
        pygame.draw.rect(utils.screen, EDGE, (w - 2, 0, 2, h))

        y = 14
        y = self._text(self.title, "MIDI RINGS", ACCENT, y)

        # --- статус ---
        status = f"t = {game.time:5.1f} / {game.maxTime:.1f} s    speed x{game.speed:g}"
        y = self._text(self.font, status, TEXT, y)
        if game.paused:
            y = self._text(self.font, "PAUSED", ACCENT, y)
        y += 6

        # --- доріжки ---
        y = self._text(self.small, "TRACKS  (press key to toggle)", DIM, y)
        for i, t in enumerate(game.tracks):
            color = TRACK_COLORS.get(t, (255, 255, 255))
            on = game.enabled[t]
            pygame.draw.rect(utils.screen, color, (self.x, y + 2, 12, 12), 0 if on else 2)
            label = f"[{i + 1}] Track {t}: {game.track_counts[t]} notes  {'ON' if on else 'OFF'}"
            y = self._text(self.font, label, TEXT if on else DIM, y, self.x + 20)
        y += 6

        # --- відповідність MIDI -> анімація ---
        y = self._text(self.small, "MIDI  ->  ANIMATION", DIM, y)
        for line in ("pitch      ->  ring radius + color",
                     "track      ->  dot outline, wave speed",
                     "duration   ->  dot size",
                     "note_on    ->  ring appears, flash,",
                     "                wave, sound",
                     "note_off   ->  sound off"):
            y = self._text(self.small, line, TEXT, y)
        y += 6

        # --- керування ---
        y = self._text(self.small, "CONTROLS", DIM, y)
        for line in ("1 / 2          toggle track",
                     "SPACE          pause",
                     "LEFT / RIGHT   speed",
                     "R              restart"):
            y = self._text(self.small, line, TEXT, y)
        y += 6

        # --- журнал подій (нові зверху, старі тьмяніють) ---
        y = self._text(self.small, "LAST MIDI EVENTS", DIM, y)
        for t, e in reversed(game.log):
            k = max(0.35, 1.0 - (game.time - t) / 6.0)
            base = TRACK_COLORS.get(e['track'], (255, 255, 255))
            color = tuple(int(c * k) for c in base)
            line = (f"{t:5.1f}s  T{e['track']}  {note_name(e['note'])}  "
                    f"{e['duration']:.2f}s  v{e['velocity']}")
            y = self._text(self.small, line, color, y)