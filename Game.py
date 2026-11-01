import random

from Ring import Ring
from midi import list_notes_from_midi
from utils import utils


class Game:
    def __init__(self):
      self.notes_dict = list_notes_from_midi("menuet-en-sol.mid")
      for note in self.notes_dict.values():
           print(note)
      
      self.time = 0
      self.minTime = 0
      self.maxTime = 19.8 # duration of the file

      self.angle = 0

      self.rings = []
      radius = 50
      hue = 0
      hueStep = 1 / len(self.notes_dict.values())
      # self.list_notes = self.shuffle_dict(self.list_notes)
      rotateDir = 1
      maxWidth = min(utils.width, utils.height) / 2
      for note in reversed(self.notes_dict.values()):
          ring = Ring(radius, utils.hueToRGB(hue), self.notes_dict[note['name']], self.maxTime,
                      random.uniform(0, 360), rotateDir)
          rotateDir *= -1
          hue += hueStep
          self.rings.append(ring)
          radius += (maxWidth - 50) / len(self.notes_dict.values())


    def update(self):
        self.time += utils.clock.get_time() / 1000.0
        if self.time >= self.maxTime:
            self.time = 0
            for ring in self.rings:
                ring.reset()
        for ring in self.rings:
            ring.update(self.time)

    def draw(self):
        for ring in self.rings:
            ring.draw()