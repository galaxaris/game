from os.path import join

import pygame.image

from api.Game import Game
import pygame as pg

WIDTH, HEIGHT = 640, 360
NAME = "Omicronde"
FPS = 60

game = Game(WIDTH, HEIGHT, NAME, FPS)

game.set_icon(join("assets", "icon.jpg"))

def loop():
    rect = pg.rect.Rect(0, 0, 50, 50)
    screen = game.screen


def main():
    game.run(loop)

if __name__ == "__main__":
    main()

