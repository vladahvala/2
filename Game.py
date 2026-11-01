from collections import deque

import pygame

from Effects import Ripple
from Ring import Ring
from midi import load_events
from utils import utils

# колір за доріжкою MIDI (індекс доріжки у файлі: 1 = "one:", 2 = "two:")
TRACK_COLORS = {1: (255, 150, 60), 2: (90, 180, 255)}
# швидкість розходження хвилі за доріжкою
TRACK_RIPPLE_SPEED = {1: 160, 2: 90}
# множники швидкості відтворення (клавіші вліво / вправо)
SPEED_STEPS = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0]


class Game:
    def __init__(self):
        # events: [{track, note, start, duration, velocity}, ...] відсортовані за start
        self.events, self.maxTime = load_events("jellyfish.mid")

        self.time = 0.0
        self.next_event = 0      # індекс наступної події, яка ще не спрацювала
        self.active = []         # ноти, що зараз звучать: [(кінець_у_секундах, подія)]
        self.ripples = []

        # керування
        self.paused = False
        self.speed_index = SPEED_STEPS.index(1.0)
        self.tracks = sorted({e['track'] for e in self.events})
        self.enabled = {t: True for t in self.tracks}
        self.track_counts = {t: sum(1 for e in self.events if e['track'] == t)
                             for t in self.tracks}
        self.log = deque(maxlen=10)   # останні події для панелі HUD: (час, подія)

        # одне кільце на кожну унікальну висоту; низькі ноти всередині, високі зовні
        pitches = sorted({e['note'] for e in self.events})
        maxRadius = min(utils.width - utils.hud_width, utils.height) / 2 - 20
        minRadius = 50
        step = (maxRadius - minRadius) / max(len(pitches) - 1, 1)

        self.rings = {}
        rotateDir = 1
        for i, pitch in enumerate(pitches):
            hue = i / len(pitches)                     # висота -> колір
            self.rings[pitch] = Ring(minRadius + i * step,   # висота -> радіус
                                     utils.hueToRGB(hue),
                                     self.maxTime, rotateDir)
            rotateDir *= -1

        # кожній події відповідає точка на кільці своєї висоти
        for e in self.events:
            color = TRACK_COLORS.get(e['track'], (255, 255, 255))
            e['dot'] = self.rings[e['note']].add_event(e, color)

    @property
    def speed(self):
        return SPEED_STEPS[self.speed_index]

    # ---------- клавіатура ----------
    def handle_key(self, key):
        if key == pygame.K_SPACE:
            self.toggle_pause()
        elif key == pygame.K_r:
            self.restart()
        elif key == pygame.K_RIGHT:
            self.speed_index = min(self.speed_index + 1, len(SPEED_STEPS) - 1)
        elif key == pygame.K_LEFT:
            self.speed_index = max(self.speed_index - 1, 0)
        elif key in (pygame.K_1, pygame.K_2):
            idx = key - pygame.K_1          # клавіша 1 -> перша доріжка, 2 -> друга
            if idx < len(self.tracks):
                self.toggle_track(self.tracks[idx])

    def toggle_track(self, track):
        self.enabled[track] = not self.enabled[track]
        on = self.enabled[track]
        for e in self.events:
            if e['track'] == track:
                e['dot'].hidden = not on
        if not on:  # вимикаємо звук нот цієї доріжки, що звучать зараз
            keep = []
            for end, e in self.active:
                if e['track'] == track:
                    self._note_off(e)
                else:
                    keep.append((end, e))
            self.active = keep

    def toggle_pause(self):
        self.paused = not self.paused
        for _, e in self.active:
            if self.paused:
                self._note_off(e)
            else:
                self._note_on(e)

    def shutdown(self):
        for _, e in self.active:
            self._note_off(e)
        self.active = []
        if utils.midiPlayer is not None:
            try:
                utils.midiPlayer.close()
            except Exception:
                pass

    # ---------- звук ----------
    def _channel(self, event):
        return min(max(event['track'] - 1, 0), 15)

    def _note_on(self, event):
        if utils.midiPlayer is None:
            return
        ch = self._channel(event)
        utils.midiPlayer.set_instrument(0, ch)
        utils.midiPlayer.note_on(event['note'], min(event['velocity'], 127), ch)

    def _note_off(self, event):
        if utils.midiPlayer is None:
            return
        utils.midiPlayer.note_off(event['note'], 0, self._channel(event))

    # ---------- MIDI-подія -> анімація ----------
    def _trigger(self, event):
        if not self.enabled.get(event['track'], True):
            return                         # доріжка вимкнена клавішею
        ring = self.rings[event['note']]
        ring.visible = True                # note_on: кільце з'являється
        event['dot'].trigger()             # note_on: точка спалахує
        self.ripples.append(               # note_on: від кільця йде хвиля
            Ripple(ring.center, ring.radius,
                   ring.color,  # колір хвилі = колір кільця
                   TRACK_RIPPLE_SPEED.get(event['track'], 120)))
        self._note_on(event)               # note_on: звучить нота
        self.active.append((event['start'] + event['duration'], event))
        self.log.append((self.time, event))

    def restart(self):
        for _, event in self.active:
            self._note_off(event)
        self.active = []
        self.ripples = []
        self.log.clear()
        self.time = 0.0
        self.next_event = 0
        for ring in self.rings.values():
            ring.reset()

    def update(self):
        if self.paused:
            return
        real_dt = utils.deltaTime()
        self.time += real_dt * self.speed
        if self.time >= self.maxTime:
            self.restart()

        # запускаємо всі події, час яких настав
        while (self.next_event < len(self.events)
               and self.events[self.next_event]['start'] <= self.time):
            self._trigger(self.events[self.next_event])
            self.next_event += 1

        # note_off: вимикаємо ноти, тривалість яких закінчилась
        still_active = []
        for end, event in self.active:
            if end <= self.time:
                self._note_off(event)
            else:
                still_active.append((end, event))
        self.active = still_active

        for ring in self.rings.values():
            ring.update(self.time, real_dt)
        for r in self.ripples:
            r.update(real_dt)
        self.ripples = [r for r in self.ripples if r.alive()]

    def draw(self):
        for ring in self.rings.values():
            ring.draw()
        for r in self.ripples:
            r.draw()