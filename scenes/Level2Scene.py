from api.Game import Game
from api.engine.Scene import Scene
from api.utils import Debug
from game.scripts.levels.level_generation import init_level
from game.scripts.player_manager import init_player

scene = None
player = None

def start(game: Game):
    global scene
    global player
    scene = Scene(game.render_size)
    scene.name = "Level2Scene"
    player = init_player(game)
    init_level(game, scene, player)


def update(game: Game):
    Debug.register_debug_entity(game, player)


