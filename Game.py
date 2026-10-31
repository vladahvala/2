import random

from midi import list_notes_from_midi
from utils import utils


class Game:
    def __init__(self):
      self.notes_dict = list_notes_from_midi("menuet-en-sol.mid")
      for note in self.notes_dict.values():
           print(note)

    def update(self):
        pass

    def draw(self):
       pass