from api.Game import Game
from api.engine.Scene import Scene
from api.environment.Solid import Solid
from api.utils import Debug
from game.scripts.levels.level_generation import init_level
from game.scripts.levels.level_ui import update_ammo_ui
from game.scripts.player_manager import init_player

scene = None
player = None

def start(game: Game):
    global scene
    global player
    scene = Scene(game.render_size)
    scene.name = "Level3Scene"
    player = init_player(game)
    init_level(game, scene, player)

    collections = []
    collections += [Solid((x, 300), (100, 100)) for x in range(0, 400, 100)]  # Floor
    collections += [Solid((x, 300), (100, 100)) for x in
                         range(500, 1000, 100)]  # Floor, leaving a gap for the player to fall through
    collections += [Solid((0, y), (100, 100)) for y in range(200, 700, 100)]  # Wall at our left
    collections += [Solid((250, 350), (200, 20))]  # First platform


    anchor_block_1 = Solid((600,70), (50, 50))
    anchor_block_1.add_tag("anchor")
    collections += [anchor_block_1]

    anchor_block_2 = Solid((800, 70), (50, 50))
    anchor_block_2.add_tag("anchor")
    collections += [anchor_block_2]

    for coll in collections:
        if not "anchor" in coll.tags:
            coll.set_color((200, 200, 200))

        else:
            coll.set_color((255, 0, 0))

    for colls in collections:
        scene.add(colls, "#object")


def update(game: Game):
    Debug.register_debug_entity(game, player)


