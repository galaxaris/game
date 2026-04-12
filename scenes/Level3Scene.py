from api.Game import Game
from api.engine.Scene import Scene
from api.environment.Solid import Solid
from api.utils import Debug
from game.scripts.levels.level_generation import init_level
from game.scripts.levels.level_ui import update_player_health_ui, update_ammo_ui
from game.scripts.player_manager import init_player

scene = None
player = None

def start(game: Game):
    global scene
    global player
    scene = Scene(game.render_size)
    scene.name = "Level3Scene"
    scene.this.player = init_player(game)
    init_level(game, scene, scene.this.player)

    collections = []
    collections += [Solid((x, 300), (100, 100)) for x in range(0, 400, 100)]  # Floor
    collections += [Solid((x, 300), (100, 100)) for x in
                         range(500, 1000, 100)]  # Floor, leaving a gap for the player to fall through
    collections += [Solid((0, y), (100, 100)) for y in range(200, 700, 100)]  # Wall at our left
    collections += [Solid((250, 250), (200, 20))]  # First platform
    collections += [Solid((550, 200), (500, 50))]  # Second platform

    anchor_block = Solid((600, 100), (20, 20))
    anchor_block.add_tag("anchor")
    collections += [anchor_block]

    for coll in collections:
        if not "anchor" in coll.tags:
            coll.set_color((200, 200, 200))

        else:
            coll.set_color((255, 0, 0))

    for colls in collections:
        scene.add(colls, "#object")


def update(game: Game):
    Debug.register_debug_entity(game, scene.this.player)
    update_player_health_ui(scene.this.player_ui_health, scene.this.player.health)
    update_ammo_ui(scene.this.player_ui_ammo, scene.this.player.ammo)


