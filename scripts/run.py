from api.utils.Console import print_info
from game.scripts.player_manager import init_player
from game.scripts.scene_manager import *
from game.scripts.ui import toggle_audio, toggle_menu_inGame
#Import inputs
from api.utils.InputManager import onKeyDown, onKeyUp

def Start(game):
    print_info("Welcome to the Omicronde Game - [bold]Galaxaris Demo[/bold] !\nIf you don't see the game window, it might be behind your current window, please check!\nAnd... [green]HAVE FUN![/green]")


    load_scene("Level2Scene", game)

    #TODO: TO BE REMOVED
    toggle_audio(game.audio_manager)

    

def update(game):
    scene = game.scene
    refresh_screen(scene)
    update_scene(game)
    toggle_menu_inGame(game)

    if onKeyDown(pg.K_n):
        game.event_manager.triggerEvent("switch_scene")


