from api.Game import Game
from api.engine.Scene import Scene
from api.utils import Debug
from game.scripts.levels.level_generation import init_level
from game.scripts.levels.level_ui import update_player_health_ui, update_ammo_ui
from game.scripts.player_manager import init_player
from api.environment.Solid import *
from api.assets.Texture import *


scene = None

def start(game: Game):
    global scene
    scene = Scene(game.render_size)
    scene.name = "Level1Scene"
    scene.this.player = init_player(game)

    """
    CREATION OF COLLIDERS
    """
    l_wall = Solid((100,300),(100,450))
    l_wall.set_texture(Texture(0,0,is_missing=True))
    scene.add(l_wall)

    spawn_surf = Solid((199,600),(200,50))
    spawn_surf.set_texture(Texture(0, 0, is_missing=True))
    scene.add(spawn_surf)


    init_level(game, scene, scene.this.player)



def update(game: Game):
    Debug.register_debug_entity(game, scene.this.player)
    update_player_health_ui(scene.this.player_ui_health, scene.this.player.health)
    update_ammo_ui(scene.this.player_ui_ammo, scene.this.player.ammo)


