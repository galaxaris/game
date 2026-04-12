#Events
from api.Game import Game
from api.utils.Console import print_success
from game.scripts.history import start_game
from game.scripts.scene_manager import *

def register_events(game: Game):
    game.event_manager.Instances.bindInstancesDict({
        "game": game
    })
    game.event_manager.registerEvent("restart_level", [lambda e: restart_scene(game)])
    game.event_manager.registerEvent("enable_debug", [lambda e: game.enable_debug()])
    game.event_manager.registerEvent("goto_title_screen", [lambda e: load_scene("MainMenuScene", game)])
    game.event_manager.registerEvent("start_game", [lambda e: start_game(game)])
    print_success("Events registered successfully")