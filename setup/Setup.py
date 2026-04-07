"""
Module gathering the whole game setup (assets, levels, events, etc.) before launching the game, (to be called in Omicronde.__init__() in `game/setup/game.py`)
"""
from game.setup.imports_collection import *

def setup_game(game_instance):
    """
    Setup the game by initializing game settings, loading assets, initializing the player, setting up the camera, music and event manager
    """

    #%%################ GAME SETTINGS ####################
    ######################################################
    init_game_settings(game_instance, debug_mode=False, mute=True)
    init_input_manager()

    #%%################ LOADING ASSETS ####################
    #######################################################
    game_instance.audio_manager = game_instance.game.audio_manager

    # Init the resource manager
    game_instance.ASSETS_PATH = ASSETS_PATH
    game_instance.resource_manager = Resource(ResourceType.GLOBAL, game_instance.ASSETS_PATH)
    game_instance.RESSOURCES = init_ressource_manager(game_instance.resource_manager, game_instance.audio_manager, game_instance.ASSETS_PATH)

    Fonts.DEFAULT_FONT = game_instance.RESSOURCES["fonts"]["default"]
    Debug.debug_font = game_instance.RESSOURCES["fonts"]["debug"]

    game_instance.game.set_icon(game_instance.RESSOURCES["textures"]["icon"])

    #%%################ PLAYER INITIALIZATION ####################
    ##############################################################
    game_instance.player = init_player(game_instance)

    #%%################ CAMERA SETUP ####################
    #####################################################

    ### Offsets the camera
    # To center the player. Thus, the camera follows the player when moving, while keeping it centered on the screen.
    game_instance.scene.camera.set_offset((game_instance.RENDER_WIDTH // 2 - game_instance.player.size.x, game_instance.RENDER_HEIGHT // 2 - game_instance.player.size.y))
    game_instance.scene.camera.set_limits((100, -game_instance.RENDER_HEIGHT - 100), (game_instance.RENDER_WIDTH * 20, game_instance.RENDER_HEIGHT - 100))


    #%%################# MUSIC SETUP ########################
    #########################################################
    """
    For now, no music or SFX for peace of mind of our dear Raphix. Can be changed with the button mute/unmute in the menu
    """
    #Music is setup in the ressource manager


    #%%################# EVENT MANAGER SETUP ########################
    #################################################################
    #To be set at the end, because it needs to bind previous initialized game instances

    game_instance.game_event_manager = game_instance.game.event_manager
    init_event_manager(game_instance)
    
    #NOTE: You can register custom events in `CustomEventsCollection`

    #Example of triggering an event:
    #game_instance.game_event_manager.triggerEvent("custom_event")