from api.Game import Game
from api.engine import Scene
from api.environment.Parallax import ParallaxBackground, ParallaxLayer
from api.environment.Trigger import TriggerKillBox
from game.scripts.player_manager import init_player
import pygame as pg


def init_level(game: Game, scene: Scene, player):
    game.event_manager.Instances.bindInstance("player", player)
    scene.add(player, "#player")
    p_bg = get_parallax_background(scene.name, game)
    scene.set_background(p_bg)
    scene.camera.set_offset((scene.size.x // 2 - player.size.x, scene.size.y // 2 - player.size.y))
    scene.camera.set_limits((100, -scene.size.y - 100), (scene.size.x * 20, scene.size.y - 100))
    create_killBoxes(game, scene, player, 50)
    scene.camera.focus(player)

def create_killBoxes(game, scene, player, length):
    trigger_box = TriggerKillBox((-1000, scene.size.y+400), (length*1000, 100), ["player", "projectile"], once=False, sfx=["death"])
    scene.add(trigger_box, "#objects")


def get_parallax_background(name, game):
    p_bg = None
    if name == "Level1Scene" or name == "Level2Scene":
        p_bg = ParallaxBackground(game.render_size, [
            ParallaxLayer(pg.Vector2(0.9, 0.45), game.RESSOURCES["textures"]["forest_layer3"]),
            ParallaxLayer(pg.Vector2(0.7, 0.35), game.RESSOURCES["textures"]["forest_layer2"]),
            ParallaxLayer(pg.Vector2(0.5, 0.25), game.RESSOURCES["textures"]["forest_layer1"]),
        ], (34, 59, 62), (34, 59, 62), False)
    if name == "Level3Scene":
        p_bg = ParallaxBackground(game.render_size, [
            ParallaxLayer(pg.Vector2(0.9, 0.45), game.RESSOURCES["textures"]["desert_layer5"]),
            ParallaxLayer(pg.Vector2(0.8, 0.40), game.RESSOURCES["textures"]["desert_layer4"]),
            ParallaxLayer(pg.Vector2(0.7, 0.35), game.RESSOURCES["textures"]["desert_layer3"]),
            ParallaxLayer(pg.Vector2(0.5, 0.30), game.RESSOURCES["textures"]["desert_layer2"]),
            ParallaxLayer(pg.Vector2(0.3, 0.25), game.RESSOURCES["textures"]["desert_layer1"]),
        ], (253, 248, 241), (138, 72, 54), True)
    if name == "BossLevelScene":
        p_bg = ParallaxBackground(game.render_size, [
            ParallaxLayer(pg.Vector2(0.9, 0.45), game.RESSOURCES["textures"]["industrial_layer1"]),
            ParallaxLayer(pg.Vector2(0.7, 0.35), game.RESSOURCES["textures"]["industrial_layer2"]),
            ParallaxLayer(pg.Vector2(0.5, 0.25), game.RESSOURCES["textures"]["industrial_layer3"]),
            ParallaxLayer(pg.Vector2(0.3, 0.15), game.RESSOURCES["textures"]["industrial_bg"]),
        ], (25, 40, 31), (25, 40, 31), True)
    return p_bg