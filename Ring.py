from pygame import Vector2

import pygame
from utils import utils

class Ring:
    def __init__(self,radius, color, noteData, maxTime, angle,rotateDir):
        self.radius = radius
        self.color = color
        self.noteData = noteData
        self.center = Vector2(utils.width / 2, utils.height / 2)
        self.minTime = 0
        self.maxTime = maxTime
        self.rotateDir = rotateDir
        self.playAt = 0
        self.angle = angle
        self.pFlag = False

        self.justPlay = {}
        for i, start_time in enumerate(self.noteData['start_times']):
            self.justPlay[i] = False

    def playSound(self, time):
        # Update justPlay status based on start_times and time
        for i, start_time in enumerate(self.noteData['start_times']):
            if i not in self.justPlay:
                self.justPlay[i] = False
            if start_time <= time and not self.justPlay[i]:
                self.justPlay[i] = True
                self.playAt = i

        # Turn off notes where velocity is zero
        for i, start_time in enumerate(self.noteData['start_times']):
            if start_time <= time and self.justPlay[i] and self.noteData['velocities'][i] == 0:
                self.justPlay[i] = False

        # Play the note if it should be played
        if self.justPlay[self.playAt] and not self.pFlag:
            velocity = self.noteData['velocities'][self.playAt]
            instrument = self.noteData['instruments'][self.playAt]
            # if instrument == 10:
            #     instrument = 53
            utils.midiPlayer.set_instrument(instrument)
            utils.midiPlayer.note_on(self.noteData['name'],
                                 min(velocity * utils.volumeScale, 127))  # Corrected max to min for velocity
            self.pFlag = True
        elif not self.justPlay[self.playAt] and self.pFlag:
            utils.midiPlayer.note_off(self.noteData['name'], 0)
            self.pFlag = False

    def reset(self):
      self.justPlay = {}
      for i, start_time in enumerate(self.noteData['start_times']):
          self.justPlay[i] = False

    
    def update(self, time):
        self.playSound(time)

    def draw(self):
        pygame.draw.circle(utils.screen, self.color, self.center, self.radius, 2)
