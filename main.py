# To run the game from CMD or VS Code terminal (PyCharm runs strangely)
# Execute the program with "python -m game.main" from the root directory of the project

from os.path import join

from pygame.surface import Surface

from api.Game import Game
import pygame as pg

from api.GameObject import GameObject
from api.assets.Animation import Animation
from api.assets.Resource import Resource, ResourceType
from api.assets.Texture import Texture
from api.environment.Background import Background
from api.environment.Parallax import ParallaxImage, ParallaxBackground

RENDER_WIDTH, RENDER_HEIGHT = 640, 360
WIDTH, HEIGHT = 1600, 900
NAME = "Omicronde"
FPS = 60

game = Game((WIDTH, HEIGHT), (RENDER_WIDTH, RENDER_HEIGHT), NAME, pg.RESIZABLE | pg.SCALED, FPS)

game.set_icon(join("assets", "icon.jpg"))

glob = Resource(ResourceType.GLOBAL, "assets")
anim = Animation(Texture("run.png", glob), 12, 100)
icon = Texture("icon.jpg", glob)
blue_tile = Texture("Blue.png", glob)
t_p1 = Texture("0.9x parallax-demon-woods-close-trees.png", glob)
t_p2 = Texture("0.70x parallax-demon-woods-mid-trees.png", glob)
t_p3 = Texture("0.5x parallax-demon-woods-far-trees.png", glob)
t_p4 = Texture("0.25x parallax-demon-woods-bg.png", glob)

player = GameObject((0, 0), (50, 50))
player.set_position((310,170))

block = GameObject((0, 0), (100, 100))
block.set_color((255, 255, 0))
block.set_position((310,270))

game.screen.camera.set_offset((RENDER_WIDTH//2 - player.size.x,RENDER_HEIGHT//2 - player.size.y))

aaa = GameObject((0, 0), (100, 100))
aaa.set_color((255, 255, 255))

p_bg = ParallaxBackground((RENDER_WIDTH, RENDER_HEIGHT))
p1 = ParallaxImage(pg.Vector2(0.9, 0.45), t_p1)
p2 = ParallaxImage(pg.Vector2(0.7, 0.35), t_p2)
p3 = ParallaxImage(pg.Vector2(0.5, 0.25), t_p3)
p4 = ParallaxImage(pg.Vector2(0.25, 0.125), t_p4)

bg = Background(blue_tile,True,(RENDER_WIDTH, RENDER_HEIGHT))

p_bg.add(p1)
p_bg.add(p2)
p_bg.add(p3)
p_bg.add(p4)

def loop():

    player.set_animation(anim)

    screen = game.screen
    screen.set_layer(1, "#object")
    screen.set_layer(2, "player")

    screen.add(block, "#object")

    screen.add(player, "player")
    screen.set_background(p_bg)
    screen.camera.focus(player)

    keys_pressed = pg.key.get_pressed()



    if keys_pressed[pg.K_d]:
       player.set_position(player.pos + (1.5, 0))
       player.set_direction("right")
    if keys_pressed[pg.K_q]:
       player.set_position(player.pos + (-1.5, 0))
       player.set_direction("left")
    if keys_pressed[pg.K_s]:
        player.set_position(player.pos + (0, 1.5))
    if keys_pressed[pg.K_z]:
        player.set_position(player.pos + (0, -1.5))

def main():
    game.run(loop)

if __name__ == "__main__":
    main()

