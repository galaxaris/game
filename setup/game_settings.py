"""
All settings for the game, such as screen size, FPS, window title, etc.
Initializes the game according to these settings and returns them as a dictionary.
"""

#Do not import `imports_collection` directly to avoid circular imports
import os
import pygame as pg
from api.Game import Game
from api.utils import Fonts, Debug
from api.utils.ResourcePath import resource_path

#The "" around Omicronde is to avoid trying to import it before it's defined
def init_game_settings(game_class, debug_mode: bool = False, mute: bool = False, override_settings: dict = None):
    """
    Initializes game settings and returns them as a dictionary.

    :param game_class: The main game class to initialize settings for (ex: Omicronde).
    :param debug_mode: Whether to enable debug mode (default: False).
    :param mute: Whether to start the game with audio muted (default: False).
    :param override_settings: A dictionary of settings to override the defaults (default: None).
    :return: A dictionary containing the initialized game settings.
    """

    settings = {
        "RENDER_WIDTH": 640,
        "RENDER_HEIGHT": 360,
        "SCREEN_WIDTH": 1280,
        "SCREEN_HEIGHT": 720,
        "FPS": 60,
        "WINDOW_TITLE": "Robot Recovery",
        "GRAVITY": 0.5,
    }

    if override_settings:
        settings.update(override_settings)

    #%%############### GLOBAL VARIABLES ###################
    #######################################################
    game_class.RENDER_WIDTH, game_class.RENDER_HEIGHT = settings["RENDER_WIDTH"], settings["RENDER_HEIGHT"]
    game_class.WIDTH, game_class.HEIGHT = settings["SCREEN_WIDTH"], settings["SCREEN_HEIGHT"]
    game_class.NAME = settings["WINDOW_TITLE"]
    game_class.FPS = settings["FPS"]
    game_class.GRAVITY = settings["GRAVITY"]
    
    #%%############### Initializing the game ##############
    #######################################################
    game_class.game = Game(
        (game_class.WIDTH, game_class.HEIGHT), 
        (game_class.RENDER_WIDTH, game_class.RENDER_HEIGHT), 
        game_class.NAME, 
        pg.RESIZABLE | pg.SCALED, 
        game_class.FPS)
    
    game_class.scene = game_class.game.scene

    ### DEBUG MODE ###
    if debug_mode:
        game_class.game.enable_debug()

    #Toggles fullscreen
    game_class.game.toggle_fullscreen(os.environ.get("NO_FULLSCREEN") != "1") 


    return settings