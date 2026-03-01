"""
=== Debug file for the game ===
"""

# To run the game from CMD or VS Code terminal (PyCharm runs strangely)
# Execute the program with "python -m game.main" from the root directory of the project

#Libs
from os.path import join
import pygame as pg

#API
from api.Game import Game
from api.UI.Dialog import Dialog
from api.UI.Text import Text
from api.UI.TextBox import TextBox
from api.assets.Animation import Animation
from api.assets.Resource import Resource, ResourceType
from api.assets.Texture import Texture
from api.entity.Player import Player
from api.environment.Background import Background
from api.environment.Parallax import ParallaxLayer, ParallaxBackground
from api.environment.Solid import Solid
from api.utils.Inputs import get_inputs
from api.environment.Trigger import Trigger, Trigger_KillBox

#Game modules
from game.game_actions.triggers import *

RENDER_WIDTH, RENDER_HEIGHT = 640, 360
WIDTH, HEIGHT = 1600, 900
NAME = "Omicronde"
FPS = 60

game = Game((WIDTH, HEIGHT), (RENDER_WIDTH, RENDER_HEIGHT), NAME, pg.RESIZABLE | pg.SCALED, FPS)

game.set_icon(join("assets", "icon.jpg"))

#DEBUG MODE

game.enable_debug()

glob = Resource(ResourceType.GLOBAL, "assets")

run_anim = Animation(Texture("player/run.png", glob), 12, 100)
run_fast_anim = Animation(Texture("player/run.png", glob), 12, 70)
idle_anim = Animation(Texture("player/idle.png", glob), 11, 100)
jump_anim = Texture("player/jump.png", glob)
fall_anim = Texture("player/fall.png", glob)


blue_tile = Texture("Blue.png", glob)

t_p1 = Texture("0.9x parallax-demon-woods-close-trees.png", glob)
t_p2 = Texture("0.70x parallax-demon-woods-mid-trees.png", glob)
t_p3 = Texture("0.5x parallax-demon-woods-far-trees.png", glob)
t_p4 = Texture("0.25x parallax-demon-woods-bg.png", glob)

player = Player((-10, 0), (50, 50))
player.set_gravity(0.5)
player.set_position((310,410))


player.bind_animations({
    "run": run_anim,
    "run_fast": run_fast_anim,
    "idle": idle_anim,
    "jump": jump_anim,
    "fall": fall_anim,

})

#Envir blocks
collections = []
collections += [Solid((x,600), (100, 100)) for x in range(0, 400, 100)] #Floor
collections += [Solid((x,600), (100, 100)) for x in range(500, 1000, 100)] #Floor, leaving a gap for the player to fall through
collections += [Solid((0,y), (100, 100)) for y in range(200, 700, 100)]
collections += [Solid((250, 550), (200, 20))]
collections += [Solid((550, 500), (500, 50))]

for coll in collections:
    coll.set_color((200, 200, 200))

#Triggers
create_killBox(collections, 5, game, HEIGHT)

collections += [Trigger((700, 400), (100, 100), ["player"], [lambda obj: print_alert_msg("Trigger that can be actived each time triggered!")])]
collections += [Trigger((832, 550), (32, 32), ["player"], [lambda obj: summon_stairs1(collections)], once=True)]


game.scene.camera.set_offset((RENDER_WIDTH//2 - player.size.x,RENDER_HEIGHT//2 - player.size.y))
game.scene.camera.set_limits((100, -RENDER_HEIGHT-100), (RENDER_WIDTH*3, RENDER_HEIGHT-100))

p_bg = ParallaxBackground((RENDER_WIDTH, RENDER_HEIGHT), [
    ParallaxLayer(pg.Vector2(0.9, 0.45), t_p1),
    ParallaxLayer(pg.Vector2(0.7, 0.35), t_p2),
    ParallaxLayer(pg.Vector2(0.5, 0.25), t_p3),
], (75, 105, 52))

bg = Background(blue_tile,True,(RENDER_WIDTH, RENDER_HEIGHT))
scene = game.scene

icon = Texture("icon.jpg", glob)


text = Text((110, 500), 32, "Galaxaris")
dialog = Dialog("**/assets/FRm6x11.ttf")
dialog.add_character("Galaxaris", icon)
dialog.add_character("Omicronde", icon)
dialog.add_message("Galaxaris", "Hello there, I'm Galaxaris !")
dialog.add_message("Omicronde", "And I'm Omicronde, nice to meet you !")
dialog.add_message("Galaxaris", "This is a demo of the Omicronde API, a game engine made in Python with Pygame. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vel sapien eget nunc commodo efficitur. Sed ac nisl a enim efficitur efficitur.")

scene.UI.add("test", dialog)

def debug_info():
    game.register_debug_entity(player)


def loop():
    game.scene.default_surface.fill((0,0,0,0))
 

    scene.set_layer(1, "#object")
    scene.set_layer(2, "#player")

    debug_info()

    for colls in collections:
        scene.add(colls, "#object")

    scene.add(player, "#player")

    inputs = pg.key.get_pressed()

    if inputs[pg.K_a]:
        scene.UI.show("test")



    scene.set_background(p_bg)
    scene.camera.focus(player)



def main():
    game.run(loop)

if __name__ == "__main__":
    main()

