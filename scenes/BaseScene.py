from api.Game import Game
from api.engine.Scene import Scene
from api.utils import Debug
from game.scripts.player_manager import init_player

scene = None
player = None

def start(game: Game):
    global scene
    global player
    scene = Scene(game.render_size)
    scene.name = "BaseScene"
    player = init_player(game)
    scene.add(player, "#player")


def update(game: Game):
    Debug.register_debug_entity(game, player)


