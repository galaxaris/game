from game.scenes import MainMenuScene, BaseScene, Level1Scene, Level2Scene, Level3Scene, BossLevelScene
from game.scripts.ui import menu_in_game
from api.utils.Console import print_info
from api.utils.InputManager import onKeyDown, onKeyUp
import pygame as pg

scenes = {
    "MainMenuScene": MainMenuScene,
    "BaseScene": BaseScene,
    "Level1Scene": Level1Scene,
    "Level2Scene": Level2Scene,
    "Level3Scene": Level3Scene,
    "BossLevelScene": BossLevelScene,
}

current_scene_instance = None

def refresh_screen(scene):
    scene.default_surface.fill((0,0,0,0))
    scene.set_layer(1, "#object")
    scene.set_layer(2, "#player")
    scene.set_layer(3, "#enemies")
    scene.set_layer(4, "_trajectory")
    scene.set_layer(5, "#projectile")

def load_scene(scene_name: str, game):
    global current_scene_instance
    if scene_name in scenes:
        scene_instance = scenes[scene_name]
        scene_instance.start(game)
        if not scene_instance:
            raise ValueError(f"Failed to load scene '{scene_name}'.")
        scene = scene_instance.scene
        current_scene_instance = scene_instance

        if scene:
            game.scene = scene
            refresh_screen(scene)
            menu = menu_in_game(game, "menu")
            if menu:
                scene.UI.add("menu", menu)

        return scene_instance
    else:
        raise ValueError(f"Scene '{scene_name}' not found.")

def restart_scene(game):
    global current_scene_instance
    if current_scene_instance:
        scene_name = current_scene_instance.scene.name
        load_scene(scene_name, game)

def update_scene(game):
    global current_scene_instance
    if current_scene_instance:
        game.scene = current_scene_instance.scene
        current_scene_instance.update(game)


def switch_scene(game):
    """
    Switches to the next scene in the list of scenes. If the current scene is the last one, it loops back to the first scene.
    """
    list_scenes = list(scenes.keys())

    current_scene_name = game.scene.name
    if current_scene_name in list_scenes:
        current_index = list_scenes.index(current_scene_name)
        next_index = (current_index + 1) % len(list_scenes)
        next_scene_name = list_scenes[next_index]
        load_scene(next_scene_name, game)