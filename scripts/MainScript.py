"""
This module contains the main game script: functions and instructions shared by all scenes.

- def start(): to be executed once at the start of the game

- def update(): to be executed at each frame of the game loop
"""

from game.setup.imports_collection import *


#%%############# ON START #############################
#######################################################

#Place here any instruction you want to be executed once at the start.
#NOTE: for init and setup functions, place them in the Omicronde.__init__() function
def Start(game_instance):        
    game_instance.audio_manager.play_music("titleScreen")
    toggle_audio(game_instance.audio_manager)  # Mute the music by default, can be changed with the button in the menu
    #EventManager.triggerEvent("toggle_audio") #Trigger the start_game event to initialize the first scene (main menu)

    print_info("Welcome to the Omicronde Game - [bold]Galaxaris Demo[/bold] !\nIf you don't see the game window, it might be behind your current window, please check!\nAnd... [green]HAVE FUN![/green]")



#%%################ GAME LOOP ########################
######################################################

def Update(game_instance):
    ### Refresh scene and layers order.
    refresh_screen(game_instance)

    ### Displays debug info if debug mode was enabled in the game settings or toggled later
    game_instance.debug_info()

    ### Updates the player health UI
    if game_instance.player and game_instance.player_ui_health:
        update_player_health_UI(game_instance.player_ui_health, game_instance.player.health)

    #### Update all GameObjects (stored in collections list)
    for colls in game_instance.collections:
        game_instance.scene.add(colls, "#object")

    #### Updates camera position
    game_instance.scene.camera.focus(game_instance.player)

    ### Key inputs checking
    ### There for debugging purposes only
    if onKeyDown(pg.K_o):
        game_instance.player.respawn()

    if onKeyDown(pg.K_p):
        game_instance.game.scene = game_instance.menu_scene

    if onKeyDown(pg.K_i):
        game_instance.entity.mode = "patrol" if game_instance.entity.mode == "chase" else "chase"

    if onKeyDown(pg.K_m):
        game_instance.game.scene = game_instance.scene

    #Tests EventManager + InputManager
    if onKeyDown(pg.K_n):
        #game_instance.game_event_manager.triggerEvent("player_jump")
        game_instance.game_event_manager.triggerEvent("custom_event")

    toggle_menu_inGame(game_instance.scene, "menu", game_instance.menu_scene, game_instance)


#%%################# GAME SCRIPTS #####################
#######################################################

def refresh_screen(game_instance):
    ### Refresh scene and layers order. Avoid modifying this part!
    #You can add layers if needed
    game_instance.scene.default_surface.fill((0,0,0,0))
    game_instance.scene.set_layer(1, "#object")
    game_instance.scene.set_layer(2, "#player")
    game_instance.scene.set_layer(3, "#enemies")
    game_instance.scene.set_layer(4, "_trajectory")
    game_instance.scene.set_layer(5, "#projectile")