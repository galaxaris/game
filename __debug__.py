"""
=== Debug file for the game ===
"""

# To run the game from CMD or VS Code terminal (PyCharm runs strangely)
# Execute the program with "python -m game.main" from the root directory of the project

from os.path import join

from api.Game import Game
import pygame as pg

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

collections = []
collections += [Solid((x,600), (100, 100)) for x in range(0, 400, 100)] #Floor
collections += [Solid((x,600), (100, 100)) for x in range(500, 1000, 100)] #Floor, leaving a gap for the player to fall through
collections += [Solid((0,y), (100, 100)) for y in range(200, 700, 100)]
collections += [Solid((250, 550), (200, 20))]
collections += [Solid((550, 500), (500, 50))]

for coll in collections:
    coll.set_color((200, 200, 200))

#Add a killbox at 100px from the bottom of the screen, that kills the player on contact
#killbox = Trigger((0, HEIGHT), (WIDTH*10, 1000), ["player"], [lambda obj: obj.kill(game)], once=False)
killbox = Trigger_KillBox((0, HEIGHT+400), (1000, 1000), ["player"], game, once=False)
collections += [killbox]
#Killbox2 to handle the case of very long width GameObject (see TODO in Trigger_KillBox class)
killbox2 = Trigger_KillBox((1000, HEIGHT+400), (1000, 1000), ["player"], game, once=False)
collections += [killbox2]

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

