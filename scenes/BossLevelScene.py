import math

from api.Game import Game
from api.assets.Animation import Animation
from api.engine.Scene import Scene
from api.entity.Boss import Boss
from api.environment.Solid import Solid
from api.environment.Trigger import Trigger, TriggerInteract
from api.UI.Dialog import Dialog
from api.utils import Debug
from game.Variables import game_settings
from game.scripts.levels.level_generation import init_level
from game.scripts.levels.level_ui import update_player_health_ui, update_ammo_ui
from game.scripts.player_manager import init_player

scene = None
player = None


def _make_block(pos, size, color=(200, 200, 200)):
    block = Solid(pos, size)
    block.set_color(color)
    return block


def _lock_arena(obj=None):
    if scene.this.arena_locked:
        return

    scene.this.arena_locked = True
    wall_l, wall_r = scene.this.arena_walls
    wall_l.set_state(True)
    wall_r.set_state(True)
    wall_l.visible = True
    wall_r.visible = True
    # Save a safe respawn point inside the arena.
    scene.this.player.start_pos = list(scene.this.arena_checkpoint)
    game = scene.this.game
    game.audio_manager.play_sfx("switch")


def _update_boss_phase():
    boss = scene.this.boss
    if boss.destroyed or not scene.this.arena_locked:
        return

    if boss.health <= boss.original_health // 2:
        scene.this.boss_phase = 2

    left_limit = scene.this.arena_left + 40
    right_limit = scene.this.arena_right - boss.size.x - 40
    speed = 1.0 if scene.this.boss_phase == 1 else 1.6

    boss.vel.x = speed * scene.this.boss_move_dir
    if boss.pos.x <= left_limit:
        scene.this.boss_move_dir = 1
        boss.set_direction("right")
    elif boss.pos.x >= right_limit:
        scene.this.boss_move_dir = -1
        boss.set_direction("left")

    player_obj = scene.this.player
    boss_center = boss.pos + boss.size / 2
    player_center = player_obj.pos + player_obj.size / 2
    direction = player_center - boss_center




def _on_boss_defeated():
    if scene.this.boss_defeated:
        return

    scene.this.boss_defeated = True
    scene.this.arena_locked = False
    for wall in scene.this.arena_walls:
        wall.set_state(False)
        wall.visible = False

    game = scene.this.game
    game.audio_manager.play_sfx("checkpoint")
    setattr(game, "boss_victory_return", True)
    game.event_manager.triggerEvent("goto_base")

def start(game: Game):
    global scene
    global player
    scene = Scene(game.render_size)
    scene.name = "BossLevelScene"
    player = init_player(game)

    game.audio_manager.play_music("bossLevel")

    scene.this.player = player
    scene.this.game = game
    init_level(game, scene, player)
    scene.camera.set_offset((scene.size.x // 2 - player.size.x, scene.size.y // 2 - player.size.y + 100))
    scene.camera.set_limits((100, -scene.size.y - 100), (scene.size.x * 20, scene.size.y - 100))

    scene.this.boss_phase = 1
    scene.this.boss_move_dir = 1
    scene.this.boss_defeated = False
    scene.this.arena_locked = False

    collections = []

    eco_briefing = Dialog(game.RESSOURCES["fonts"]["default"])
    eco_briefing.add_character("Conseil Ecologique", game.RESSOURCES["textures"]["sign"])
    eco_briefing.add_message(
        "Conseil Ecologique",
        "Objectif prioritaire: neutraliser le boss Cyclope Prime. "
        "Moins il reste actif, moins il peut polluer la zone industrielle."
    )
    eco_briefing.add_message(
        "Conseil Ecologique",
        "Reste mobile, utilise les plateformes et garde des munitions pour la phase finale."
    )
    scene.UI.add("eco_boss_briefing", eco_briefing)

    eco_recycling = Dialog(game.RESSOURCES["fonts"]["default"])
    eco_recycling.add_character("Conseil Ecologique", game.RESSOURCES["textures"]["sign"])
    eco_recycling.add_message(
        "Conseil Ecologique",
        "Apres la victoire, ses composants seront tries et recycles."
    )
    eco_recycling.add_message(
        "Conseil Ecologique",
        "Acier, circuits et batteries serviront a restaurer les infrastructures vertes et sauver la planete."
    )
    scene.UI.add("eco_recycling_plan", eco_recycling)

    # Start corridor + first jumps.
    collections += [_make_block((80, y), (20, 40), (110, 110, 110)) for y in range(80, 360, 40)]
    collections += [_make_block((100, 300), (420, 60))]
    collections += [_make_block((560, 270), (70, 20))]
    collections += [_make_block((690, 235), (70, 20))]
    collections += [_make_block((820, 200), (70, 20))]
    collections += [_make_block((930, 300), (300, 60))]

    # Mid-section: light platforming before arena.
    collections += [_make_block((1280, 260), (85, 20))]
    collections += [_make_block((1430, 230), (85, 20))]
    collections += [_make_block((1580, 200), (85, 20))]
    collections += [_make_block((1720, 300), (180, 60))]

    eco_panel_1 = TriggerInteract(
        (1765, 268),
        (32, 32),
        {"player"},
        [lambda obj: scene.UI.show("eco_boss_briefing")],
    )
    eco_panel_1.set_texture(game.RESSOURCES["textures"]["sign"])
    collections.append(eco_panel_1)

    # Arena layout.
    arena_left = 1920
    arena_right = 2520
    scene.this.arena_left = arena_left
    scene.this.arena_right = arena_right

    collections += [_make_block((arena_left, 300), (arena_right - arena_left, 60), (150, 150, 150))]

    last_platform_pos = (arena_left + 415, 250)
    last_platform_size = (95, 18)
    collections += [_make_block(last_platform_pos, last_platform_size, (175, 175, 175))]
    scene.this.arena_checkpoint = [arena_left + 120, 202]

    # Lock walls are present but disabled until player enters the arena.
    arena_wall_left = _make_block((arena_left - 20, 80), (20, 280), (85, 85, 85))
    arena_wall_right = _make_block((arena_right, 80), (20, 280), (85, 85, 85))
    arena_wall_left.set_state(False)
    arena_wall_right.set_state(False)
    arena_wall_left.visible = False
    arena_wall_right.visible = False
    scene.this.arena_walls = [arena_wall_left, arena_wall_right]

    # Optional refill just before boss.
    refill_trigger = TriggerInteract(
        (last_platform_pos[0] + 22, last_platform_pos[1] - 48),
        (48, 48),
        {"player"},
        [lambda obj: setattr(scene.this.player, "ammo", 25)],
    )
    refill_trigger.set_color((60, 160, 210))
    collections.append(refill_trigger)

    # Arena entry trigger: closes doors only after the player is fully inside.
    player_entry_margin = int(scene.this.player.size.x) + 12
    arena_trigger = Trigger((arena_left + player_entry_margin, 80), (28, 280), {"player"}, [_lock_arena], once=True)
    collections.append(arena_trigger)

    eco_panel_2 = TriggerInteract(
        (1932, 268),
        (32, 32),
        {"player"},
        [lambda obj: scene.UI.show("eco_recycling_plan")],
    )
    eco_panel_2.set_texture(game.RESSOURCES["textures"]["sign"])
    collections.append(eco_panel_2)

    # Boss setup.
    boss = Boss((arena_left + 410, 204), (96, 96), health=260, name="Cyclope Prime")
    boss.set_gravity(game_settings["GRAVITY"])
    boss.damage_force = 12
    boss.mode = "idle"
    boss.equipped_weapon.cooldown = 1100
    boss.equipped_weapon.projectile_damage = 8
    boss.equipped_weapon.target = "player"
    if "boss" in game.RESSOURCES["textures"]:
        boss.set_animation(Animation(game.RESSOURCES["textures"]["boss"], 11, 100))

    scene.this.boss = boss

    for coll in collections:
        scene.add(coll, "#object")

    scene.add(arena_wall_left, "#object")
    scene.add(arena_wall_right, "#object")
    scene.add(boss, "#enemies")

def update(game: Game):
    Debug.register_debug_entity(game, scene.this.player)
    update_player_health_ui(scene.this.player_ui_health, scene.this.player.health)
    update_ammo_ui(scene.this.player_ui_ammo, scene.this.player.ammo)

    _update_boss_phase()

    if scene.this.boss.health <= 0:
        _on_boss_defeated()


