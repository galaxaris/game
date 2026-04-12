from api.Game import Game
from api.engine.Scene import Scene
from api.environment.Solid import Solid
from api.utils import Debug
from game.scripts.levels.level_generation import init_level
from game.scripts.levels.level_ui import update_player_health_ui, update_ammo_ui
from game.scripts.player_manager import init_player
from api.environment.Trigger import TriggerInteract
from api.UI.Dialog import Dialog
from api.utils.Console import print_info, print_success, print_error, print_warning
from api.entity.Enemy import Enemy
from game.scripts.levels.level2 import summon_stairs1
from api.entity.Boss import Boss
from api.environment.Trap import Trap
from api.environment.Trigger import Trigger
from api.environment.Trigger import TriggerInteract
from api.environment.Solid import Solid
from api.assets.Animation import Animation

from game.Variables import game_settings, player_settings


scene = None
player = None

def start(game: Game):
    global scene
    global player
    scene = Scene(game.render_size)
    scene.name = "Level2Scene"
    scene.this.player = init_player(game)
    init_level(game, scene, scene.this.player)
    game.audio_manager.play_music("level2")


    collections = []

    #%%################ ENVIRONMENT SETUP ####################
    ##########################################################

    ##### SOLIDS ####
    # TODO: to be implemented in a JSON BDD (when we will have a level system, with the editor)
    #UPDATE: doesn't have the f***ing time, hardcoded... The editor is not used...

    collections += [Solid((x, 300), (100, 100)).set_texture(game.RESSOURCES["textures"]["grass"]) for x in range(0, 400, 100)]  # Floor

    #%%################ ENTITIES INITIALIZATION ####################
    ################################################################

    ### ENTITIES & ENEMIES ###

    #### TRIGGERS ####
    # (see game/scripts/triggers.py for the functions (callbacks) called by the triggers)
    # A trigger is an invisible area that executes a callback function when the targeted object enter it.

    ### NOTE ### to pass a callback, use "lambda" or "functools.partial". See the Trigger module for more info. Syntax is as follows:
    # lambda obj: call_back_function(params, ...)

    ### Predefined triggers
    ### Creates a killBox that kills the player when falling too much (y > HEIGHT)

    ### Custom triggers


    for colls in collections:
        scene.add(colls, "#object")



def update(game: Game):
    Debug.register_debug_entity(game, scene.this.player)
    update_player_health_ui(scene.this.player_ui_health, scene.this.player.health)
    update_ammo_ui(scene.this.player_ui_ammo, scene.this.player.ammo)


