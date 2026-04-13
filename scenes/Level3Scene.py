from api.Game import Game
from api.engine.GameCamera import GameCamera
from api.engine.Scene import Scene
from api.environment.Solid import Solid
from api.utils import Debug
from game.scripts.levels.level_generation import init_level
from game.scripts.levels.level_ui import update_player_health_ui, update_ammo_ui
from game.scripts.player_manager import init_player
from api.physics.MovingPlatform import update_moving_platform

import pygame as pg

import math

# a level is 13000 pixels wide

scene = None
player = None

running = True

def start(game: Game):
    global scene, player
    moving_platforms = []
    scene = Scene(game.render_size)
    scene.name = "Level3Scene"
    scene.this.player = init_player(game)
    scene.this.moving_platform = []
    init_level(game, scene, scene.this.player)

    scene.camera.set_offset((scene.size.x // 2 - scene.this.player.size.x, scene.size.y // 2 - scene.this.player.size.y + 100))
    scene.camera.set_limits((150, -scene.size.y - 100), (scene.size.x * 20, scene.size.y - 100))

    collections = []

    collections += [Solid((0, y), (100, 100)) for y in range(200, 700, 100)]  # Wall at our left

    collections += [Solid((100, 280), (630, 100))]  # Floor

    anchor_block = Solid((1045, 110), (20, 20))
    anchor_block.add_tag("anchor")
    collections += [anchor_block]

    collections += [Solid((1000, 280), (200, 100))]

    anchor_block = Solid((1300, 0), (20, 20))
    anchor_block.add_tag("anchor")
    collections += [anchor_block]

    moving_floor = Solid((1300, 100), (100, 100))
    moving_floor.add_tag("anchor")
    scene.this.moving_platform.append({
        "solid": moving_floor, "axis": "x", "speed": 0.85, "direction": 1,
        "min_x": 1300 - 100, "max_x": 1300 + 100, "_current": float(1300),
    })

    collections += [moving_floor]

    for coll in collections:
        if "anchor" in coll.tags:
            coll.set_color((255, 0, 0))

        elif "moving_floor" in coll.tags:
            coll.set_color((0, 255, 0))

        else:
            coll.set_color((200, 200, 200))

    for colls in collections:
        scene.add(colls, "#object")


def update(game: Game):
    global scene, player

    Debug.register_debug_entity(game, scene.this.player)
    update_player_health_ui(scene.this.player_ui_health, scene.this.player.health)
    update_ammo_ui(scene.this.player_ui_ammo, scene.this.player.ammo)

    update_moving_platform(scene.this.moving_platform)

