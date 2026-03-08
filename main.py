"""
=== Omicronde Project Game - Galaxaris ===

This is the entry point of the Omicronde Game. Built using the Omicronde API.

Authors: Galaxaris & Associates

v.Beta (in development)
- 03/03/2026

Copyright (c) 2026 Galaxaris & Associates. All rights reserved.

"""

### TODO: levels to be implemented and loaded in a JSON BDD (using the editor) => GameObjects, triggers, UI, background, music, etc...

### TODO: create an 'InputManager' to centralize game input handling
### TODO: create a 'SceneManager' to manage multiple game scenes (menus, levels...) and transitions between them

### TODO: create a 'ResourceManager' to centralize the loading and stock of game assets
    ## => try/except for loading function, "pink" texture as fallback
    ### TODO: create a 'TextureManager' to manage and stock game textures; texture atlases (=> sprites) and animations
        ## => TODO: define a standard for texture atlases & anims (associated .json files?)
    ### TODO: create an 'AudioManager' to manage and stock game SFX and music
    ### TODO: create a 'UIManager' to define specific game UI elements and keep an overall style (fonts, colors...)


#%%################ IMPORTS ####################
################################################
#### RUN THE GAME WITH "python -m game.main" FROM THE ROOT DIRECTORY OF THE PROJECT ####


### Libs ###
import os
from os.path import join
import time

#### CHANGE WORK DIRECTORY TO THE GAME FOLDER ####
#=> relative paths for assets loading is managed properly. Can be runned then from anywhere without issue 
os.chdir(os.path.dirname(os.path.abspath(__file__)))

### API ###
from api.Game import Game
from api.UI.Button import Button
from api.UI.Dialog import Dialog
from api.UI.Modal import Modal
from api.UI.Text import Text
from api.UI.TextBox import TextBox
from api.assets.Animation import Animation
from api.assets.Resource import Resource, ResourceType
from api.assets.Texture import Texture
from api.assets.AudioManager import AudioManager
from api.engine.Scene import Scene
from api.entity.Player import Player
from api.environment.Background import Background
from api.environment.Parallax import ParallaxLayer, ParallaxBackground
from api.environment.Solid import Solid
from api.utils import State, GlobalVariables, Debug
from api.utils.Inputs import get_inputs, get_once_inputs, prevent_input
from api.environment.Trigger import Trigger, TriggerInteract
from api.utils.RessourcePath import resource_path

### Game modules ###
from game.game_actions.triggers import *
from game.game_actions.ui import menu_in_game

#%%############## CLOSE SPLASH SCREEN #################
#######################################################
try:
    import pyi_splash
    time.sleep(5)
    pyi_splash.close()
except ImportError:
    # we are not in an exe file
    pass

#%%############### GLOBAL VARIABLES ###################
#######################################################

RENDER_WIDTH, RENDER_HEIGHT = 640, 360
WIDTH, HEIGHT = 1280, 720
NAME = "Omicronde"
FPS = 60

#%%############### Initializing the game ##############
#######################################################
assets_path = resource_path("assets")
font_FR = "**/" + join(assets_path, "Fonts\\Gm6x11.ttf")
GlobalVariables.set_variable("default_font", font_FR)
game = Game((WIDTH, HEIGHT), (RENDER_WIDTH, RENDER_HEIGHT), NAME, pg.RESIZABLE | pg.SCALED, FPS, debug_font=font_FR)

### DEBUG MODE ###

#Enables debug mode by default
game.enable_debug()

#Toggles fullscreen

game.toggle_fullscreen(os.environ.get("NO_FULLSCREEN") != "1")

#%%################ LOADING ASSETS ####################
#######################################################

#Init the resource manager

glob = Resource(ResourceType.GLOBAL, assets_path)

icon = Texture("Images\\icon.png", glob)
game.set_icon(resource_path(os.path.join("assets", "Images", "icon.png")))

#Loads animations
run_anim = Animation(Texture("Images\\Player\\NinjaFrog\\run.png", glob), 12, 70)
run_fast_anim = Animation(Texture("Images\\Player\\NinjaFrog\\run.png", glob), 12, 50)
idle_anim = Animation(Texture("Images\\Player\\NinjaFrog\\idle.png", glob), 11, 100)
jump_anim = Texture("Images\\Player\\NinjaFrog\\jump.png", glob)
fall_anim = Texture("Images\\Player\\NinjaFrog\\fall.png", glob)

#Textures
ggg = Texture("Images\\Background\\tiles\\ggg.png",glob)

#Loads background
blue_tile = Texture("Images\\Background\\Tiles\\Blue.png", glob)

#Loads parallax layers
t_p1 = Texture("Images\\Background\\Parallax\\Forest\\0.9x parallax-demon-woods-close-trees.png", glob)
t_p2 = Texture("Images\\Background\\Parallax\\Forest\\0.70x parallax-demon-woods-mid-trees.png", glob)
t_p3 = Texture("Images\\Background\\Parallax\\Forest\\0.5x parallax-demon-woods-far-trees.png", glob)
t_p4 = Texture("Images\\Background\\Parallax\\Forest\\0.25x parallax-demon-woods-bg.png", glob)

#Loads music
audio_manager = game.audio_manager

audio_manager.load_music("inGame", join(assets_path, "Music\\Gestral Beach - My Grandma Hits Harder!.mp3"))
audio_manager.load_music("pause", join(assets_path, "Music\\Alicia.mp3"))

#Loads SFX
audio_manager.load_sfx("jump", join(assets_path, "SFX\\frog-sound.mp3"))
audio_manager.load_sfx("hit_ground", join(assets_path, "SFX\\Casserole.mp3"))
audio_manager.load_sfx("death", join(assets_path, "SFX\\blblblbl.mp3"))



#%%################ PLAYER INITIALIZATION ####################
##############################################################
player = Player((310,410), (48,48), sfx_list={"jump": "jump", "hit_ground": "hit_ground", "death": "death"})
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


grass = Texture("Images\\grass.png", glob)
#Setting a texture for all solids (to be better implemented with a "Tile" class, allowing to repeat a texture on a surface of any size, and also use a texture atlas)
for coll in collections:
    coll.set_color((200, 200, 200))
    coll.set_texture(grass)

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


me = Texture("Images\\Player\\NinjaFrog\\jump.png", glob)
#%%################ UI setup ####################
################################################



dialog = Dialog(font_FR)
dialog.add_character("Galaxaris", icon)
dialog.add_character("You", me)
dialog.add_message("Galaxaris", "Hello there, I'm Galaxaris !")
dialog.add_message("You", "And I'm me, nice to meet you !")
dialog.add_message("Galaxaris", "This is a demo of the Omicronde API, a game engine made in Python with Pygame. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vel sapien eget nunc commodo efficitur. (T'as vu je sais parler Latin XD)")

scene.UI.add("test", dialog)

info_box = TriggerInteract((110, 568), (32, 32), ["player"], [lambda obj: scene.UI.show("test")])
info_box.set_texture(icon)
collections += [info_box]

### MENU INGAME
menu = menu_in_game(scene, "menu", RENDER_WIDTH, RENDER_HEIGHT, player, game)
scene.UI.add("menu", menu)

#%%################# MUSIC SETUP ########################
#########################################################
"""
For now, no music or SFX for peace of mind of our dear Raphix. Can be changed with the button mute/unmute in the menu
"""
audio_manager.set_sfx_volume(0)
audio_manager.set_music_volume(0)

audio_manager.play_music("inGame") #Play the main theme in loop


#%%################# NEW SCENE TEST ########################
############################################################

new_scene = Scene((RENDER_WIDTH, RENDER_HEIGHT))
new_scene.set_background(bg)
new_scene.camera.set_offset((RENDER_WIDTH//2 - player.size.x,RENDER_HEIGHT//2 - player.size.y))



#%%############### UTILS FUNCTIONS ####################
#######################################################
def debug_info():
    game.register_debug_entity(player)


#%%################ MAIN LOOP ####################
##################################################

def loop():
    game.scene.default_surface.fill((0,0,0,0))
 

    scene.set_layer(1, "#object")
    scene.set_layer(2, "#player")

    debug_info()

    for colls in collections:
        scene.add(colls, "#object")

    scene.add(player, "#player")
    new_scene.add(player, "#player")
    new_scene.camera.focus(player)

    inputs = pg.key.get_pressed()

    if inputs[pg.K_o]:
        player.kill()

    scene.set_background(p_bg)
    scene.camera.focus(player)

    if inputs[pg.K_p]:
        game.scene = new_scene
    if inputs[pg.K_m]:
        game.scene = scene

    if not "menu" in scene.UI.enabled_elements:
        if get_once_inputs()["pause"]:
            prevent_input("pause")
            #print("Opening menu: menu")
            scene.UI.show("menu")
            audio_manager.play_music("pause")
    elif "menu" in scene.UI.enabled_elements:
        if get_once_inputs()["pause"]:
            prevent_input("pause")
            #print("Closing menu: menu")
            scene.UI.hide("menu")
            audio_manager.play_music("inGame") #Resume the main theme when closing the menu

def main():
    """
    Main loop starting the game
    """
    game.run(loop)


#%%################ RUNNING THE GAME #########################
##############################################################
if __name__ == "__main__":
    main()

