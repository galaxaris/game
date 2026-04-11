from game.scripts.player_manager import init_player
from game.scripts.scene_manager import *
from game.scripts.ui import toggle_menu_inGame


def update(game):
    scene = game.scene
    refresh_screen(scene)
    update_scene(game)
    toggle_menu_inGame(game)


