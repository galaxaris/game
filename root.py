##################################
#         ROBOT RECOVERY         #
##################################

# Imports
from api.Game import Game
from api.assets.ResourceManager import ResourceType, Resource
from api.utils import Fonts, Debug
from api.utils.Console import print_info
from api.utils.ResourcePath import resource_path

import pygame as pg
import os

from game.scripts.resource_manager import init_ressource_manager
from game.scripts.scene_manager import load_scene

ASSETS_PATH = resource_path("assets")

from game.Variables import *

# Main game initialization
game = Game(
        (game_settings["SCREEN_WIDTH"], game_settings["SCREEN_HEIGHT"]),
        (game_settings["RENDER_WIDTH"], game_settings["RENDER_HEIGHT"]),
        game_settings["WINDOW_TITLE"],
        pg.RESIZABLE | pg.SCALED,
        game_settings["FPS"])

game.resource_manager = Resource(ResourceType.GLOBAL, ASSETS_PATH)
game.RESSOURCES = init_ressource_manager(game.resource_manager, game.audio_manager, ASSETS_PATH)

Fonts.DEFAULT_FONT = game.RESSOURCES["fonts"]["default"]
Debug.debug_font = game.RESSOURCES["fonts"]["debug"]

game.toggle_fullscreen(os.environ.get("NO_FULLSCREEN") != "1")
game.set_icon(game.RESSOURCES["textures"]["icon"])

scene = game.scene # Alias

from game.scripts.run import update, Start
from game.scripts.events import *
register_events(game)
Start(game)
game.run(lambda: update(game))


