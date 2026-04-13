from api.Game import Game
from api.engine.Scene import Scene
from api.environment.Background import Background
from api.utils import Debug
from game.scripts.ui import main_menu

scene = None
player = None

def start(game: Game):
    global scene
    global player
    scene = Scene(game.render_size)
    scene.name = "MainMenuScene"

    game.audio_manager.play_music("titleScreen")

    b_bg = Background(game.RESSOURCES["textures"]["menu_bg"], False, scene.size)
    scene.set_background(b_bg)
    menu2 = main_menu(game, scene)
    scene.UI.add("main_menu", menu2)
    scene.UI.show("main_menu")

def update(game: Game):
    Debug.register_debug_entity(game, player)


