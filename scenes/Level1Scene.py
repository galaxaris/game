from api.Game import Game
from api.engine.Scene import Scene
from api.utils import Debug
from game.scripts.levels.level_generation import init_level
from game.scripts.levels.level_ui import update_player_health_ui, update_ammo_ui
from game.scripts.player_manager import init_player
from api.environment.Solid import *
from api.assets.Texture import *
from api.entity.Enemy import *
from api.environment.Trigger import *
from api.assets.Animation import *
from game.scripts.levels.level2 import (
    summon_stairs1,
    refill_water,
    save_checkpoint,
    activate_switch,
    make_ecology_dialog,
    make_melanie_dialog,
    make_story_dialog,
)


scene = None

def start(game: Game):
    global scene
    scene = Scene(game.render_size)
    scene.name = "Level1Scene"
    scene.this.player = init_player(game)
    p = scene.this.player

    game.audio_manager.play_music("level1")

    """
    CREATION OF COLLIDERS
    """
    l_wall = Solid((100,100),(50,500))
    l_wall.set_texture(game.RESSOURCES["textures"]["mossy_steel"])
    scene.add(l_wall)

    new_obj = Solid((150,400),(350,300))
    new_obj.set_texture(game.RESSOURCES["textures"]["platform_forest"])
    scene.add(new_obj)

    dialog_story = make_story_dialog(
        game.RESSOURCES["fonts"]["default"],
        game.RESSOURCES["textures"]["sign"],
        "Tutorial",
        [
            "ATTENTION PLEASE NEW ROBOT.\n"
            "To move to the left : USE Q\nTO move to right : USE D",
            "To jump : press \"SPACE\""
        ]
    )
    scene.UI.add("tuto1", dialog_story)
    sign_story = TriggerInteract(
        (250, 370), (32, 32), ["player"],
        [lambda obj: scene.UI.show("tuto1")]
    )
    sign_story.set_texture(game.RESSOURCES["textures"]["sign"])
    scene.add(sign_story)

    new_obj =Solid((575,400),(150,300))
    new_obj.set_texture(game.RESSOURCES["textures"]["platform_forest"])
    scene.add(new_obj)

    new_obj = Solid((625, 376), (10, 25))
    new_obj.set_texture(game.RESSOURCES["textures"]["platform_forest"])
    scene.add(new_obj)

    new_obj =Solid((775,400),(50,300))
    new_obj.set_texture(game.RESSOURCES["textures"]["platform_forest"])
    scene.add(new_obj)

    new_obj =Solid((875,375),(25,25))
    new_obj.set_texture(game.RESSOURCES["textures"]["platform_forest"])
    scene.add(new_obj)

    new_obj = Solid((975, 350), (250, 300))
    new_obj.set_texture(game.RESSOURCES["textures"]["platform_forest"])
    scene.add(new_obj)

    dialog_story = make_story_dialog(
        game.RESSOURCES["fonts"]["default"],
        game.RESSOURCES["textures"]["sign"],
        "Tutorial",
        [
            "ATTENTION PLEASE NEW ROBOT.\n"
            "To sprint : HOLD \"SHIFT\"\nThis allow you to go faster...",
            "But also to jump further if you hold the sprint while you jump."
        ]
    )
    scene.UI.add("tuto2", dialog_story)
    sign_story = TriggerInteract(
        (1050, 320), (32, 32), ["player"],
        [lambda obj: scene.UI.show("tuto2")]
    )
    sign_story.set_texture(game.RESSOURCES["textures"]["sign"])
    scene.add(sign_story)

    new_obj = Solid((1350, 300), (225, 300))
    new_obj.set_texture(game.RESSOURCES["textures"]["platform_forest"])
    scene.add(new_obj)

    new_obj = Solid((1725, 400), (250, 300))
    new_obj.set_texture(game.RESSOURCES["textures"]["platform_forest"])
    scene.add(new_obj)

    dialog_melanie = make_story_dialog(
        game.RESSOURCES["fonts"]["default"],
        game.RESSOURCES["textures"]["melanie"],
        "Mélanie Cavill",
        ["Halo, do you hear me ?","Well, to go further i think you're gonna need the \ngrappling pistol",
         "To use it, press \"TAB\" and select it in the menu.\nThen press the left mouse button to aim and fire with the right one."]

    )
    scene.UI.add("melanie_radio", dialog_melanie)
    melanie_trigger = Trigger((1875, 200), (120, 250), ["player"],
        [lambda obj: scene.UI.show("melanie_radio")],
        once=True
    )
    scene.add(melanie_trigger)

    new_obj = Solid((2200, 400), (220, 300))
    new_obj.set_texture(game.RESSOURCES["textures"]["platform_forest"])
    scene.add(new_obj)

    new_obj = Solid((2250, 320), (25, 25))
    new_obj.set_texture(Texture(0, 0, is_missing=True))
    new_obj.add_tag("anchor")
    scene.add(new_obj)

    new_obj = Solid((2550, 310), (275, 300))
    new_obj.set_texture(game.RESSOURCES["textures"]["platform_forest"])
    scene.add(new_obj)

    new_obj = Solid((2595, 220), (25, 25))
    new_obj.set_texture(Texture(0, 0, is_missing=True))
    new_obj.add_tag("anchor")
    scene.add(new_obj)

    dialog_melanie = make_story_dialog(
        game.RESSOURCES["fonts"]["default"],
        game.RESSOURCES["textures"]["melanie"],
        "Mélanie Cavill",
        ["The radar didn't told me a Cyclope's robot was there.\nReload your water tank in the rain collector and select a weapon in the weapon's selection menu (\"TAB\".",
         "Then, like you did with the grappling gun, aim the robot and shoot."]

    )
    scene.UI.add("melanie_radio2", dialog_melanie)
    melanie_trigger = Trigger((2625, 100), (120, 250), ["player"],
        [lambda obj: scene.UI.show("melanie_radio2")],
        once=True
    )
    scene.add(melanie_trigger)

    rain1 = TriggerInteract((2750,265), (48, 48), ["player"],
        [lambda obj: refill_water(p, game)])
    rain1.set_texture(game.RESSOURCES["textures"]["rain_collector"])
    scene.add(rain1)

    checkpoint1 = Trigger((2650, 100), (95, 500), ["player"],
        [lambda obj: save_checkpoint(p, (2650, 262), game)],
        once=True)
    scene.add(checkpoint1)


    new_obj = Solid((2850, 400), (200, 300))
    new_obj.set_texture(game.RESSOURCES["textures"]["platform_forest"])
    scene.add(new_obj)

    new_obj = Enemy((2925,350),(30,50))
    new_obj.set_animation(Animation(game.RESSOURCES["textures"]["enemy"], 11, 50))
    scene.add(new_obj)

    init_level(game, scene, scene.this.player)
    scene.camera.set_offset((scene.size.x // 2 - scene.this.player.size.x, scene.size.y // 2 - scene.this.player.size.y + 50))
    scene.camera.set_limits((150, -scene.size.y - 100), (scene.size.x * 20, scene.size.y - 100))



def update(game: Game):
    Debug.register_debug_entity(game, scene.this.player)
    update_player_health_ui(scene.this.player_ui_health, scene.this.player.health)
    update_ammo_ui(scene.this.player_ui_ammo, scene.this.player.ammo)


