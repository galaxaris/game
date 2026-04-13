#Events
from api.Game import Game
from api.utils.Console import print_success
from game.Variables import story
from game.scripts.history import start_game
from game.scripts.scene_manager import *

def end_level(game: Game):
    story["current_chapter"] += 1
    load_scene("BaseScene", game)

def register_events(game: Game):
    game.event_manager.Instances.bindInstancesDict({
        "game": game
    })
    game.event_manager.registerEvent("restart_level", [lambda e: restart_scene(game)])
    game.event_manager.registerEvent("enable_debug", [lambda e: game.enable_debug()])
    game.event_manager.registerEvent("goto_title_screen", [lambda e: load_scene("MainMenuScene", game)])
    game.event_manager.registerEvent("start_game", [lambda e: start_game(game)])
    game.event_manager.registerEvent("switch_scene", [lambda e: switch_scene(game)])

    game.event_manager.registerEvent("goto_tutorial", [lambda e: load_scene("Level1Scene", game)])
    game.event_manager.registerEvent("goto_forest", [lambda e: load_scene("Level2Scene", game)])
    game.event_manager.registerEvent("goto_desert", [lambda e: load_scene("Level3Scene", game)])
    game.event_manager.registerEvent("goto_industrial", [lambda e: load_scene("BossLevelScene", game)])
    game.event_manager.registerEvent("goto_base", [lambda e: load_scene("BaseScene", game)])
    game.event_manager.registerEvent("end_level", [lambda e: end_level(game)])


    print_success("Events registered successfully")