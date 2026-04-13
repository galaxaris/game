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
    scene.name = "BossLevelScene"
    player = init_player(game)

    game.audio_manager.play_music("bossLevel")

    scene.this.player = player
    init_level(game, scene, player)
    scene.camera.set_offset((scene.size.x // 2 - player.size.x, scene.size.y // 2 - player.size.y + 100))
    scene.camera.set_limits((100, -scene.size.y - 100), (scene.size.x * 20, scene.size.y - 100))


    ground = Solid((0, 320), (1000, 100))
    ground.set_color((200, 200, 200))
    scene.add(ground, "#object")


def update(game: Game):
    Debug.register_debug_entity(game, scene.this.player)
    update_player_health_ui(scene.this.player_ui_health, scene.this.player.health)
    update_ammo_ui(scene.this.player_ui_ammo, scene.this.player.ammo)


