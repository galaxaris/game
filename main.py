# To run the game from CMD or VS Code terminal (PyCharm runs strangely)
# Execute the program with "python -m game.main" from the root directory of the project

from os.path import join

from api.Game import Game
import pygame as pg

from api.assets.Animation import Animation
from api.assets.Resource import Resource, ResourceType
from api.assets.Texture import Texture
from api.entity.Player import Player
from api.environment.Background import Background
from api.environment.Parallax import ParallaxLayer, ParallaxBackground
from api.environment.Solid import Solid

RENDER_WIDTH, RENDER_HEIGHT = 640, 360
WIDTH, HEIGHT = 1600, 900
NAME = "Omicronde"
FPS = 60

game = Game((WIDTH, HEIGHT), (RENDER_WIDTH, RENDER_HEIGHT), NAME, pg.RESIZABLE | pg.SCALED, FPS)

game.set_icon(join("assets", "icon.jpg"))

#DEBUG MODE

game.enable_debug()

glob = Resource(ResourceType.GLOBAL, "assets")
anim = Animation(Texture("run.png", glob), 12, 100)

blue_tile = Texture("Blue.png", glob)

t_p1 = Texture("0.9x parallax-demon-woods-close-trees.png", glob)
t_p2 = Texture("0.70x parallax-demon-woods-mid-trees.png", glob)
t_p3 = Texture("0.5x parallax-demon-woods-far-trees.png", glob)
t_p4 = Texture("0.25x parallax-demon-woods-bg.png", glob)

player = Player((-10, 0), (50, 50))
player.set_gravity(0.5)
player.set_position((310,410))

collections = [Solid((x,600), (100, 100)) for x in range(0, 2000, 100)]
collections += [Solid((0,y), (100, 100)) for y in range(200, 700, 100)]

for coll in collections:
    coll.set_color((200, 200, 200))

game.screen.camera.set_offset((RENDER_WIDTH//2 - player.size.x,RENDER_HEIGHT//2 - player.size.y))
game.screen.camera.set_limits((-RENDER_WIDTH*3, -RENDER_HEIGHT-100), (RENDER_WIDTH*3, RENDER_HEIGHT-100))

p_bg = ParallaxBackground((RENDER_WIDTH, RENDER_HEIGHT), [
    ParallaxLayer(pg.Vector2(0.9, 0.45), t_p1),
    ParallaxLayer(pg.Vector2(0.7, 0.35), t_p2),
    ParallaxLayer(pg.Vector2(0.5, 0.25), t_p3),
], (75, 105, 52))

bg = Background(blue_tile,True,(RENDER_WIDTH, RENDER_HEIGHT))
screen = game.screen


def debug_info():
    game.debug(f"FPS : {int(game.clock.get_fps())}", "left")
    game.debug(f"Position : {int(player.pos.x)} | {int(player.pos.y)}", "right")
    game.debug(
        f"Camera : {int(screen.camera.position.x)} | {int(screen.camera.position.y)} - {screen.camera.focused_object.__class__.__name__ if screen.camera.focused_object else "Free"}",
        "left")

    game.debug("Jump : " + ("True" if player.jump else "False"), "right")
    game.debug("Fall : " + ("True" if player.fall else "False"), "right")
    game.debug("Boost : " + ("True" if player.boost else "False"), "right")
    game.debug(f"Velocity : {player.vel.x:.1f} | {player.vel.y:.1f}" , "right")

    if player.collided_objs:
        game.debug("Collisions :", "right")
        for collision in player.collided_objs:
            game.debug(f"{collision[0].__class__.__name__} | {collision[1]}", "right", 22)



def loop():
    game.screen.default_surface.fill((0,0,0,0))

    player.set_animation(anim)

    screen.set_layer(1, "#object")
    screen.set_layer(2, "#player")

    debug_info()

    for colls in collections:
        screen.add(colls, "#object")

    screen.add(player, "#player")
    screen.set_background(p_bg)
    screen.camera.focus(player)

def main():
    game.run(loop)

if __name__ == "__main__":
    main()

