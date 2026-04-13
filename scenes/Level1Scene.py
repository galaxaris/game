from api.Game import Game
from api.engine.Scene import Scene
from api.utils import Debug
from game.scripts.levels.level_generation import init_level
from game.scripts.levels.level_ui import update_player_health_ui, update_ammo_ui
from game.scripts.player_manager import init_player
from api.environment.Solid import *
from api.assets.Texture import *
from api.entity.Enemy import *

scene = None

def start(game: Game):
    global scene
    scene = Scene(game.render_size)
    scene.name = "Level1Scene"
    scene.this.player = init_player(game)

    """
    CREATION OF COLLIDERS
    """
    l_wall = Solid((100,100),(50,500))
    l_wall.set_texture(Texture(0,0,is_missing=True))
    scene.add(l_wall)

    new_obj = Solid((150,400),(350,25))
    new_obj.set_texture(Texture(0, 0, is_missing=True))
    scene.add(new_obj)

    new_obj =Solid((575,400),(150,25))
    new_obj.set_texture(Texture(0, 0, is_missing=True))
    scene.add(new_obj)

    new_obj = Solid((625, 376), (10, 25))
    new_obj.set_texture(Texture(0, 0, is_missing=True))
    scene.add(new_obj)

    new_obj =Solid((775,400),(50,25))
    new_obj.set_texture(Texture(0, 0, is_missing=True))
    scene.add(new_obj)

    new_obj =Solid((875,375),(25,25))
    new_obj.set_texture(Texture(0, 0, is_missing=True))
    scene.add(new_obj)

    new_obj = Solid((975, 350), (250, 25))
    new_obj.set_texture(Texture(0, 0, is_missing=True))
    scene.add(new_obj)

    new_obj = Solid((1325, 300), (250, 25))
    new_obj.set_texture(Texture(0, 0, is_missing=True))
    scene.add(new_obj)

    new_obj = Solid((1725, 400), (250, 25))
    new_obj.set_texture(Texture(0, 0, is_missing=True))
    scene.add(new_obj)

    new_obj = Solid((2200, 400), (220, 25))
    new_obj.set_texture(Texture(0, 0, is_missing=True))
    scene.add(new_obj)

    new_obj = Solid((2250, 320), (25, 25))
    new_obj.set_texture(Texture(0, 0, is_missing=True))
    new_obj.add_tag("anchor")
    scene.add(new_obj)

    new_obj = Solid((2550, 310), (275, 25))
    new_obj.set_texture(Texture(0, 0, is_missing=True))
    scene.add(new_obj)

    new_obj = Solid((2595, 220), (25, 25))
    new_obj.set_texture(Texture(0, 0, is_missing=True))
    new_obj.add_tag("anchor")
    scene.add(new_obj)

    new_obj = Solid((2850, 400), (200, 25))
    new_obj.set_texture(Texture(0, 0, is_missing=True))
    scene.add(new_obj)

    new_obj = Enemy((2925,350),(30,50))
    new_obj.set_texture(Texture(0, 0, is_missing=True))
    scene.add(new_obj)

    init_level(game, scene, scene.this.player)



def update(game: Game):
    Debug.register_debug_entity(game, scene.this.player)
    update_player_health_ui(scene.this.player_ui_health, scene.this.player.health)
    update_ammo_ui(scene.this.player_ui_ammo, scene.this.player.ammo)


