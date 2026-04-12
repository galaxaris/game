from api.Game import Game
from api.UI.GameUI import UIElement
from api.UI.ProgressBar import ProgressBar
from api.engine.Scene import Scene
from api.utils import Debug
from game.scripts.levels.level_generation import init_level, get_parallax_background
from game.scripts.player_manager import init_player
from game.scripts.ui import update_player_health_UI

scene = None

def start(game: Game):
    global scene
    scene = Scene(game.render_size)
    scene.name = "Level3Scene"
    scene.player = init_player(game)
    init_level(game, scene, scene.player)


def update(game: Game):
    Debug.register_debug_entity(game, scene.player)
    update_player_health_UI(scene.player_ui_health, scene.this_player_health)

def init_level(game: Game, scene: Scene):
    game.event_manager.Instances.bindInstance("player", scene.this.player)
    scene.add(scene.this.player, "player")
    p_bg = get_parallax_background(scene.name, game)
    scene.set_background(p_bg)
    scene.camera.set_offset((scene.size.x // 2 - this.player.size.x, scene.size.y // 2 - this.player.size.y))
    scene.camera.set_limits((100, -scene.size.y - 100), (scene.size.x * 20, scene.size.y - 100))

    scene.this.player_ui_health = ProgressBar((30, 30), (100, 10), (100, 100, 100), (0, 200, 0))
    scene.this.player_ui_heart = UIElement((8, 8), (16, 16))
    scene.this.player_ui_heart.set_texture(game.RESSOURCES["textures"]["health"], True)
    scene.UI.add("player_health")


