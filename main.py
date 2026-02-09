from os.path import join

import pygame.image

from api.Game import Game
import pygame as pg

from api.GameObject import GameObject
from api.assets.Resource import Resource, ResourceType
from api.assets.Texture import Texture

WIDTH, HEIGHT = 640, 360
WIN_WIDTH, WIN_HEIGHT = 1600, 900
NAME = "Omicronde"
FPS = 60

game = Game(WIN_WIDTH, WIN_HEIGHT, WIDTH, HEIGHT, NAME, pg.SCALED | pg.RESIZABLE, FPS)

game.set_icon(join("assets", "icon.jpg"))

def loop(self):
    first = GameObject(0,0,100,100)
    second = GameObject(0,0,100,100)
    third = GameObject(0,150,300,10)
    third.set_color((255,0,0))
    glob = Resource(ResourceType.GLOBAL, "assets")
    icon = Texture("icon.jpg", glob)
    first.set_texture(icon)
    second.set_texture(icon)
    first.set_position(100,100)
    second.set_position(150,150)
    screen = self.screen
    screen.set_layer(1, "a")
    screen.set_layer(0, "b")

    screen.add(first, "b")
    screen.add(second, "a")
    screen.add(third, "b")



def main():
    game.run(loop)

if __name__ == "__main__":
    main()

