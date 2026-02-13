# To run the game from CMD or VS Code terminal (PyCharm runs strangely)
# Execute the program with "python -m game.main" from the root directory of the project


from os.path import join

from api.Game import Game
import pygame as pg

from api.GameObject import GameObject
from api.assets.Animation import Animation
from api.assets.Resource import Resource, ResourceType
from api.assets.Texture import Texture
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
t_p1 = Texture("0.9x parallax-demon-woods-close-trees.png", glob)
t_p2 = Texture("0.70x parallax-demon-woods-mid-trees.png", glob)
t_p3 = Texture("0.5x parallax-demon-woods-far-trees.png", glob)
t_p4 = Texture("0.25x parallax-demon-woods-bg.png", glob)

first = GameObject((0, 0), (100, 100))
second = GameObject((0, 0), (100, 100))
third = GameObject((0, 150), (300, 10))

player = GameObject((0, 0), (100, 100))
player.set_position((310,170))
background = GameObject((0, 0), (WIDTH, HEIGHT))

aaa = GameObject((0, 0), (100, 100))
aaa.set_color((0, 255, 0))

p_bg = ParallaxBackground("parallax", (RENDER_WIDTH, RENDER_HEIGHT))
p1 = ParallaxImage(pg.Vector2(0.9, 0.45), t_p1)
p2 = ParallaxImage(pg.Vector2(0.7, 0.35), t_p2)
p3 = ParallaxImage(pg.Vector2(0.5, 0.25), t_p3)
p4 = ParallaxImage(pg.Vector2(0.25, 0.125), t_p4)

p_bg.add(p1)
p_bg.add(p2)
p_bg.add(p3)
p_bg.add(p4)


global cam
cam = pg.Vector2(0, 0)

def loop():
    background.set_color((255,255,255))
    player.set_animation(anim)

    third.set_color((255,0,0))

    first.set_texture(icon)
    second.set_texture(icon)
    first.set_position((500,500))
    second.set_position(((pg.time.get_ticks() - 600)%640, int(1/1000*second.pos.x**2)))

    screen = game.screen
    screen.set_layer(0, "parallax")
    screen.set_layer(1, "a")
    screen.set_layer(2, "b")
    #screen.set_layer(0, "background")

    #screen.add(background, "background")
    screen.add(first, "b")
    screen.add(second, "a")
    #screen.add(third, "background")
    screen.add(player, "player")
    global cam
    p_bg.draw(screen, cam)

    keys_pressed = pg.key.get_pressed()

    if keys_pressed[pg.K_d]:
       cam += (5,0)
       player.set_direction("right")
    if keys_pressed[pg.K_q]:
       cam += (-5, 0)
       player.set_direction("left")
    if keys_pressed[pg.K_s]:
       cam += (0, 5)
    if keys_pressed[pg.K_z]:
       cam += (0, -5)

def main():
    game.run(loop)

if __name__ == "__main__":
    main()

