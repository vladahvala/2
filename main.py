import sys

import pygame

from utils import utils
from Game import Game
from HUD import HUD


game = Game()
hud = HUD()

while True:
    utils.screen.fill((0, 0, 0), (0, 0, utils.width, utils.height))
    utils.initDeltaTime()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.shutdown()   # вимкнути ноти, що ще звучать
            sys.exit(0)
        if event.type == pygame.KEYDOWN:
            game.handle_key(event.key)

    game.update()
    game.draw()
    hud.draw(game)

    pygame.display.flip()