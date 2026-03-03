"""
=== Omicronde Project Game - Galaxaris ===

This is the entry point of the Omicronde Game. Built using the Omicronde API.

Authors: Galaxaris & Associates

v.Beta (in development)
- 03/03/2026

Copyright (c) 2024 Galaxaris & Associates. All rights reserved.

"""

#%%################ IMPORTS ####################
################################################
import os
# To run the game from CMD or VS Code terminal (PyCharm runs strangely)
# Execute the program with "python -m game.main" from the root directory of the project

### Libs ###
from os.path import join
import pygame as pg

### API ###
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

### Game modules ###
from game.game_actions.triggers import *


#%%############### GLOBAL VARIABLES ###################
#######################################################

RENDER_WIDTH, RENDER_HEIGHT = 640, 360
WIDTH, HEIGHT = 1280, 720
NAME = "Omicronde"
FPS = 60

#%%############### Initializing the game ##############
#######################################################
game = Game((WIDTH, HEIGHT), (RENDER_WIDTH, RENDER_HEIGHT), NAME, pg.RESIZABLE | pg.SCALED, FPS)

game.set_icon(join("assets", "icon.jpg"))

### DEBUG MODE ###
game.enable_debug()
game.toggle_fullscreen(True)

#Toggles fullscreen
if os.environ.get("NO_FULLSCREEN") == "1":
    game.toggle_fullscreen(False)


#%%################ LOADING ASSETS ####################
#######################################################

#Init the resource manager
glob = Resource(ResourceType.GLOBAL, "assets")

#Loads animations
run_anim = Animation(Texture("player/run.png", glob), 12, 70)
run_fast_anim = Animation(Texture("player/run.png", glob), 12, 50)
idle_anim = Animation(Texture("player/idle.png", glob), 11, 100)
jump_anim = Texture("player/jump.png", glob)
fall_anim = Texture("player/fall.png", glob)

#Loads the background tile (if no parallax)
blue_tile = Texture("Blue.png", glob)

#Loads parallax layers
t_p1 = Texture("0.9x parallax-demon-woods-close-trees.png", glob)
t_p2 = Texture("0.70x parallax-demon-woods-mid-trees.png", glob)
t_p3 = Texture("0.5x parallax-demon-woods-far-trees.png", glob)
t_p4 = Texture("0.25x parallax-demon-woods-bg.png", glob)


#%%################ PLAYER INITIALIZATION ####################
##############################################################
player = Player((310,410), (50, 50))
player.set_gravity(0.5)


player.bind_animations({
    "run": run_anim,
    "run_fast": run_fast_anim,
    "idle": idle_anim,
    "jump": jump_anim,
    "fall": fall_anim,

})


#%%################ ENVIRONMENT SETUP ####################
##########################################################

# TODO: to be implemented in a JSON BDD (when we will have a level system, with the editor)

##### SOLIDS ####
collections = []
collections += [Solid((x,600), (100, 100)) for x in range(0, 400, 100)] #Floor
collections += [Solid((x,600), (100, 100)) for x in range(500, 1000, 100)] #Floor, leaving a gap for the player to fall through
collections += [Solid((0,y), (100, 100)) for y in range(200, 700, 100)]
collections += [Solid((250, 550), (200, 20))]
collections += [Solid((550, 500), (500, 50))]

#Setting a color for all solids (awaiting for sprite support)
for coll in collections:
    coll.set_color((200, 200, 200))

#### TRIGGERS #### 
# (see game/game_actions/triggers.py for the functions (callbacks) called by the triggers)
# A trigger is an invisible area that executes a callback function when the targeted object enter it.

### NOTE ### to pass a callback, use "lambda" or "functools.partial". See the Trigger module for more info. Syntax is as follows:
# lambda obj: call_back_function(params, ...)

### Predefined triggers
### Creates a killBox that kills the player when falling too much (y > HEIGHT)
create_killBox(collections, 50, game, HEIGHT)

### Custom triggers
collections += [Trigger((700, 400), (100, 100), ["player"], [lambda obj: print_alert_msg("Trigger that can be actived each time triggered!")])]
collections += [Trigger((832, 550), (32, 32), ["player"], [lambda obj: summon_stairs1(collections, HEIGHT)], once=True)]

#%%################ CAMERA SETUP ####################
#####################################################

### Offsets the camera
#To center the player. Thus the camera follows the player when moving, while keeping it centered on the screen.
game.scene.camera.set_offset((RENDER_WIDTH//2 - player.size.x,RENDER_HEIGHT//2 - player.size.y))
game.scene.camera.set_limits((100, -RENDER_HEIGHT-100), (RENDER_WIDTH*20, RENDER_HEIGHT-100))

#%%################ BACKGROUND SETUP ####################
########################################################
### Wonderful parallax background
p_bg = ParallaxBackground((RENDER_WIDTH, RENDER_HEIGHT), [
    ParallaxLayer(pg.Vector2(0.9, 0.45), t_p1),
    ParallaxLayer(pg.Vector2(0.7, 0.35), t_p2),
    ParallaxLayer(pg.Vector2(0.5, 0.25), t_p3),
], (75, 105, 52))

bg = Background(blue_tile,True,(RENDER_WIDTH, RENDER_HEIGHT))
scene = game.scene

#%%################ UI setup ####################
################################################

# TODO: to be implemented in a JSON BDD (when we will have a level system, with the editor)

icon = Texture("icon.jpg", glob)

### Sample dialogs.
text = Text((110, 500), 32, "Galaxaris")
dialog = Dialog("**/assets/FRm6x11.ttf")
dialog.add_character("Galaxaris", icon)
dialog.add_character("Omicronde", icon)
dialog.add_message("Galaxaris", "Hello there, I'm Galaxaris !")
dialog.add_message("Omicronde", "And I'm Omicronde, nice to meet you !")
dialog.add_message("Galaxaris", "This is a demo of the Omicronde API, a game engine made in Python with Pygame. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vel sapien eget nunc commodo efficitur. Sed ac nisl a enim efficitur efficitur.")

scene.UI.add("test", dialog)

#%%############### UTILS FUNCTIONS ####################
#######################################################

def debug_info():
    """
    FOR DEBUG PURPOSES ONLY -

    Displays debug information on the screen.
    """
    game.register_debug_entity(player)


#%%################ MAIN LOOP ####################
##################################################
def loop():
    """
    Main game loop. Handles game logic, rendering, and input processing. Called every frame (60fps) by the game engine (API).
    """
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
    """
    Main loop starting the game
    """
    game.run(loop)


#%%################ RUNNING THE GAME GUYS ####################
##############################################################
if __name__ == "__main__":
    main()

