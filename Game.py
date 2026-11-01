from Effects import Ripple
from Ring import Ring
from midi import load_events
from utils import utils

# колір за доріжкою MIDI (індекс доріжки у файлі: 1 = "one:", 2 = "two:")
TRACK_COLORS = {1: (255, 150, 60), 2: (90, 180, 255)}
# швидкість розходження хвилі за доріжкою
TRACK_RIPPLE_SPEED = {1: 160, 2: 90}


class Game:
    def __init__(self):
        # events: [{track, note, start, duration, velocity}, ...] відсортовані за start
        self.events, self.maxTime = load_events("jellyfish.mid")

        self.time = 0.0
        self.next_event = 0      # індекс наступної події, яка ще не спрацювала
        self.active = []         # ноти, що зараз звучать: [(кінець_у_секундах, подія)]
        self.ripples = []

        # одне кільце на кожну унікальну висоту; низькі ноти всередині, високі зовні
        pitches = sorted({e['note'] for e in self.events})
        maxRadius = min(utils.width, utils.height) / 2 - 20
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
        ring = self.rings[event['note']]
        ring.visible = True                # note_on: кільце з'являється
        event['dot'].trigger()             # note_on: точка спалахує
        self.ripples.append(               # note_on: від кільця йде хвиля
            Ripple(ring.center, ring.radius,
                   ring.color,  # колір хвилі = колір кільця
                   TRACK_RIPPLE_SPEED.get(event['track'], 120)))
        self._note_on(event)
        self.active.append((event['start'] + event['duration'], event))

    def restart(self):
        for _, event in self.active:
            self._note_off(event)
        self.active = []
        self.ripples = []
        self.time = 0.0
        self.next_event = 0
        for ring in self.rings.values():
            ring.reset()

    def update(self):
        dt = utils.deltaTime()
        self.time += dt
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
            ring.update(self.time, dt)
        for r in self.ripples:
            r.update(dt)
        self.ripples = [r for r in self.ripples if r.alive()]

    def draw(self):
        for ring in self.rings.values():
            ring.draw()
        for r in self.ripples:
            r.draw()