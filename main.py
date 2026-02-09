from os.path import join

from api.Game import Game
import pygame as pg

from api.GameObject import GameObject
from api.assets.Animation import Animation
from api.assets.Resource import Resource, ResourceType
from api.assets.Texture import Texture

RENDER_WIDTH, RENDER_HEIGHT = 640, 360
WIDTH, HEIGHT = 1920, 1080
NAME = "Omicronde"
FPS = 60

game = Game((WIDTH, HEIGHT), NAME, pg.RESIZABLE, FPS, (RENDER_WIDTH, RENDER_HEIGHT))

game.set_icon(join("assets", "icon.jpg"))

glob = Resource(ResourceType.GLOBAL, "assets")
anim = Animation(Texture("run.png", glob), 12, 100)
icon = Texture("icon.jpg", glob)

first = GameObject((0, 0), (100, 100))
second = GameObject((0, 0), (100, 100))
third = GameObject((0, 150), (300, 10))

player = GameObject((0, 0), (100, 100))
background = GameObject((0, 0), (WIDTH, HEIGHT))

aaa = GameObject((0, 0), (100, 100))
aaa.set_color((0, 255, 0))

def loop(self):

    background.set_color((255,255,255))
    player.set_animation(anim)

    third.set_color((255,0,0))

    first.set_texture(icon)
    second.set_texture(icon)
    first.set_position((100,100))
    second.set_position(((pg.time.get_ticks() - 600)%640, int(1/1000*second.pos.x**2)))

    screen = self.screen
    screen.set_layer(1, "a")
    screen.set_layer(2, "b")
    screen.set_layer(0, "background")

    screen.add(background, "background")
    screen.add(first, "b")
    screen.add(second, "a")
    screen.add(third, "background")
    screen.add(player, "player")

    keys_pressed = pg.key.get_pressed()

    #FOR AXEL
    screen.set_layer(3, "render")
    screen.default_surface.blit(aaa.image, aaa.rect)

    if keys_pressed[pg.K_d]:
       player.set_position(player.pos + (5,0))
       player.set_direction("right")
    if keys_pressed[pg.K_q]:
       player.set_position(player.pos + (-5, 0))
       player.set_direction("left")
    if keys_pressed[pg.K_s]:
       player.set_position(player.pos + (0, 5))
    if keys_pressed[pg.K_z]:
       player.set_position(player.pos + (0, -5))

def main():
    game.run(loop)

if __name__ == "__main__":
    main()

