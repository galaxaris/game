#=============================================================================
#Niveau 2 : "La Forêt"
#Scénario : Robot Recovery — Forêt de Verdance
#
#Layout général (axe X) :
#  100-500   : Lisière — tutoriel implicite (ennemi, panneau, collecteur)
#  500-560   : GAP #1  — chute mortelle
#  560-900   : Troncs oscillants + plateformes mobiles
#  900-1560  : Forêt Dense — checkpoitn #1, radio Mélanie, interrupteur
#  1560-1640 : GAP #2  — franchissable via le pont déclenché par l'interrupteur
#  1640-1780 : Transition / petits sauts
#  1800-2340 : Camp industriel en ruine — gauntlet final
#  2290      : Checkpoint #2
#  2350-2530 : Arène Boss CF-7
#
#Repères système de coordonnées :
#  - rendu interne : 640×360
#  - sol principal : y=300  (surface supérieure du Solid)
#  - joueur sur sol : rect.top ≈ 252  (300 − hauteur 48)
#  - killbox : y=420
#  - caméra limits TOP : y≈−458 / BOTTOM : y≈500
#=============================================================================

import random as rd

from api.Game import Game
from api.engine.Scene import Scene
from api.environment.Solid import Solid
from api.GameObject import GameObject
from api.utils import Debug
from game.scripts.levels.level_generation import init_level
from game.scripts.levels.level_ui import update_player_health_ui, update_ammo_ui
from game.scripts.player_manager import init_player
from api.environment.Trigger import TriggerInteract, Trigger, TriggerKillBox
from api.UI.Dialog import Dialog
from api.utils.Console import print_info, print_success, print_warning
from api.entity.Enemy import Enemy
from api.entity.Boss import Boss
from api.environment.Trap import Trap
from api.assets.Animation import Animation
from api.physics.MovingPlatform import update_moving_platform

from game.Variables import game_settings
from game.scripts.levels.level2 import (
    summon_stairs1,
    refill_water,
    save_checkpoint,
    activate_switch,
    make_ecology_dialog,
    make_melanie_dialog,
    make_story_dialog,
)


#%%# Globals ###################################################################
scene = None
player = None

# Chaque entrée : {"solid", "axis", "speed", "direction", "min_x/max_x" ou
#                  "min_y/max_y", "_current"} — mis à jour dans update()
moving_platforms = []


#%%#############################################################################
def start(game: Game):
##############################################################################
    global scene, player, moving_platforms
    moving_platforms = []

    #%%## Init scène #############################################
    scene = Scene(game.render_size)
    scene.name = "Level2Scene"
    scene.this.player = init_player(game)
    init_level(game, scene, scene.this.player)

    scene.camera.set_offset((scene.size.x // 2 - scene.this.player.size.x, scene.size.y // 2 - scene.this.player.size.y + 50))
    scene.camera.set_limits((150, -scene.size.y - 100), (scene.size.x * 20, scene.size.y - 100))

    p = scene.this.player          # alias court, capturé dans les lambdas
    player = p

    game.audio_manager.play_music("level2")

    #%%## EventManager : bind instances ####################################
    em = game.event_manager
    em.Instances.bindInstancesDict({
        "game":          game,
        "scene":         scene,
        "player":        p,
        "audio_manager": game.audio_manager,
    })

    # Tous les objets statiques sont collectés ici, puis ajoutés en fin de start().
    collections = []

    # curseur de progression horizontal: chaque section incrémente cursor
    cursor = 100
    floor_y = 300
    ground_w = 640

    def add_ground_strip(x_start: int, x_end: int, texture_key: str = "platform_forest"):
        collections.append(
            Solid((x_start, floor_y), (x_end - x_start, 150)).set_texture(game.RESSOURCES["textures"][texture_key])
        )

    def add_simple_platforms(
        x_start: int,
        x_end: int,
        y: int,
        step: int = 120,
        width: int = 45,
        texture_key: str = "tree_stump"
    ):
        for x in range(int(x_start), int(x_end), int(step)):
            collections.append(
                Solid((x, y), (width, 27)).set_texture(game.RESSOURCES["textures"][texture_key])
            )

    def fillLevelWithALotOfWonderfulStuff(
        x_start: int,
        x_end: int,
        y_min: int,
        y_max: int,
        density: float = 0.12,
        platform_forest: bool = True,
        checkpoint_ground: bool = True,
        tree_stump: bool = True,
        wall: bool = True,
        platform_forest1: bool = True,
        platform_forest2: bool = True,
        tree1: bool = True,
        tree2: bool = True,
        plant1: bool = True,
        moving_platform: bool = True,
        anchor: bool = True,
        checkpoint_switch: bool = True,
        middle_dialog_key: str = "mid_progress_notice",
        bridge_plank: bool = True,
        trap_idle: bool = True,
        rain_collector: bool = True,
        enemy: bool = True,
    ):
        """
        Genere un segment de foret procedurale jouable et fortement vertical.
        Tous les elements sont calibres sur la taille native de leur texture,
        sauf platform_forest (texture faite pour se repeter).
        """
        textures = game.RESSOURCES["textures"]

        def has_texture(texture_key: str) -> bool:
            return texture_key in textures and textures[texture_key] is not None

        def texture_size(texture_key: str, fallback: tuple[int, int] = (32, 32)) -> tuple[int, int]:
            if not has_texture(texture_key):
                return fallback
            tex = textures[texture_key]
            try:
                if hasattr(tex, "image") and tex.image is not None:
                    w, h = tex.image.get_size()
                else:
                    w, h = tex.get_size()
                return max(1, int(w)), max(1, int(h))
            except Exception:
                return fallback

        def add_scaled_solid(x: int, y: int, texture_key: str, tiles_x: int = 1, tiles_y: int = 1):
            tex_w, tex_h = texture_size(texture_key)
            width = max(1, int(tex_w * max(1, tiles_x)))
            height = max(1, int(tex_h * max(1, tiles_y)))
            solid = Solid((int(x), int(y)), (width, height))
            solid.set_texture(textures[texture_key], rescale=texture_key != "platform_forest")
            collections.append(solid)
            return solid, width, height

        def add_scaled_decor(texture_key: str, x: int, y: int, align_bottom: bool = False):
            tex_w, tex_h = texture_size(texture_key)
            top_y = int(y - tex_h) if align_bottom else int(y)
            deco = GameObject((int(x), top_y), (tex_w, tex_h))
            deco.set_texture(textures[texture_key], rescale=True)
            collections.append(deco)
            return deco, tex_w, tex_h

        def add_custom_solid(
            x: int,
            y: int,
            width: int,
            height: int,
            texture_key: str,
            rescale: bool | None = None,
        ):
            solid = Solid((int(x), int(y)), (int(width), int(height)))
            use_rescale = (texture_key != "platform_forest") if rescale is None else rescale
            solid.set_texture(textures[texture_key], rescale=use_rescale)
            collections.append(solid)
            return solid, int(width), int(height)

        def add_anchor_decor(x: int, y: int):
            if not (anchor and has_texture("industrial_tile")) and x >= x_start + 450:
                return None
            anchor_obj = Solid((int(x), int(y)), (25, 25))
            anchor_obj.set_texture(textures["industrial_tile"], rescale=True)
            anchor_obj.add_tag("anchor")
            collections.append(anchor_obj)
            return anchor_obj

        def add_platform_staircase(
            x_origin: int,
            from_y: int,
            to_y: int,
            direction: int = 1,
            add_landing: bool = False,
        ):
            step_count = max(3, min(8, int(abs(to_y - from_y) / 34) + 1))
            step_spacing_x = 58
            min_x = None
            max_x = None
            step_records = []

            for i in range(step_count):
                t = float(i + 1) / float(step_count)
                step_y = int(from_y + (to_y - from_y) * t)
                step_x = int(x_origin + (i * step_spacing_x * direction))
                step_w = 72
                add_custom_solid(step_x, step_y, step_w, 30, "platform_forest", rescale=False)
                step_records.append((step_x, step_y, step_w))

                if min_x is None:
                    min_x = step_x
                    max_x = step_x + step_w
                else:
                    min_x = min(min_x, step_x)
                    max_x = max(max_x, step_x + step_w)

                if plant1 and has_texture("plant1"):
                    plant_w, _ = texture_size("plant1")
                    if step_w > plant_w + 8:
                        plant_x = step_x + rd.randint(4, max(4, step_w - plant_w - 4))
                        add_scaled_decor("plant1", plant_x, step_y + 2, align_bottom=True)

            if add_landing and step_records:
                top_step_x, top_step_y, top_step_w = step_records[-1] if direction >= 0 else step_records[0]

                # Plateforme d'arrivee placee reellement a la sortie de l'escalier.
                platform_w = 0
                platform_h = 30
                platform_x = top_step_x + top_step_w + 14 if direction >= 0 else top_step_x - platform_w - 14
                platform_y = max(safe_min_y, min(safe_max_y, top_step_y - 8))
                add_custom_solid(platform_x, platform_y, platform_w, platform_h, "platform_forest", rescale=False)

                for decor_key in ["plant1", "tree1", "tree2"]:
                    if has_texture(decor_key):
                        decor_w, _ = texture_size(decor_key)
                        if platform_w > decor_w + 8:
                            decor_x = platform_x + rd.randint(4, max(4, platform_w - decor_w - 4))
                            add_scaled_decor(decor_key, decor_x, platform_y + 2, align_bottom=True)

                if anchor and has_texture("industrial_tile"):
                    anchor_x = platform_x + platform_w + 42 if direction >= 0 else platform_x - 67
                    anchor_y = platform_y - 100
                    add_anchor_decor(anchor_x, anchor_y)
            
            

            return {
                "start_x": int(min_x if min_x is not None else x_origin),
                "end_x": int(max_x if max_x is not None else x_origin),
            }

        start_x = int(min(x_start, x_end))
        end_x = int(max(x_start, x_end))
        if end_x - start_x < 260:
            return

        segment_length = end_x - start_x
        middle_checkpoint_enabled = segment_length > 2000
        middle_center_x = start_x + (segment_length // 2)
        middle_platform_w = 400
        middle_safety_margin = 24
        middle_safe_start = middle_center_x - (middle_platform_w // 2) - middle_safety_margin
        middle_safe_end = middle_center_x + (middle_platform_w // 2) + middle_safety_margin

        def in_middle_safe(x: int, width: int = 1) -> bool:
            x_end = x + max(1, width)
            return not (x_end < middle_safe_start or x > middle_safe_end)

        spawn_density = max(0.08, min(float(density), 1.0))

        requested_low_y = int(min(y_min, y_max))
        requested_high_y = int(max(y_min, y_max))

        # Si y_max depasse le sol, on l'interprete comme une demande de verticalite plus forte.
        if requested_high_y > floor_y:
            requested_span = max(110, min(requested_high_y - requested_low_y + 60, floor_y + 360))
            safe_max_y = floor_y - 60
            safe_min_y = max(-260, safe_max_y - requested_span)
        else:
            safe_min_y = max(-260, requested_low_y)
            safe_max_y = min(floor_y - 60, requested_high_y)

        if safe_max_y - safe_min_y < 110:
            safe_min_y = max(-260, safe_max_y - 110)

        playable_start = start_x + 70
        playable_end = end_x - 70
        if playable_end - playable_start < 320:
            return

        y_span = safe_max_y - safe_min_y
        tier_count = max(40, min(7, 3 + y_span // 85))
        tiers = [
            safe_max_y - int(i * y_span / (tier_count - 1))
            for i in range(tier_count)
        ]

        tier_min_idx = 1 if tier_count > 3 else 0
        tier_max_idx = tier_count - 1

        # Chemin principal plus lisible: petits gaps et delta vertical controle.
        main_step = int(max(105, min(165, 220 - spawn_density * 65)))
        main_jitter = int(max(14, min(36, 40 - spawn_density * 10)))
        max_vertical_step = 82

        if not (platform_forest and has_texture("platform_forest")):
            return

        has_pf1 = platform_forest1 and has_texture("platform-forest1")
        has_pf2 = platform_forest2 and has_texture("platform-forest2")
        has_moving = moving_platform and has_texture("moving_platform")
        if not (has_pf1 or has_pf2 or has_moving):
            return

        moving_lane_reservations = []
        platform_forest2_reservations = []

        def reserve_moving_lane(travel_min_x: int, travel_max_x: int, y: int, h: int = 15) -> bool:
            # Reserve an expanded lane so dynamic platforms do not stack on the same path.
            lane_min_x = int(travel_min_x) - 16
            lane_max_x = int(travel_max_x) + 16
            lane_top = int(y) - 20
            lane_bottom = int(y + h) + 20
            for min_x_r, max_x_r, top_r, bottom_r in moving_lane_reservations:
                if lane_max_x < min_x_r or lane_min_x > max_x_r:
                    continue
                if lane_bottom < top_r or lane_top > bottom_r:
                    continue
                return False
            moving_lane_reservations.append((lane_min_x, lane_max_x, lane_top, lane_bottom))
            return True

        def reserve_platform_forest2(
            x: int,
            y: int,
            w: int = 50,
            h: int = 33,
            padding: int = 4,
        ) -> bool:
            left = int(x) - padding
            top = int(y) - padding
            right = int(x + w) + padding
            bottom = int(y + h) + padding
            for r_left, r_top, r_right, r_bottom in platform_forest2_reservations:
                if right <= r_left or left >= r_right or bottom <= r_top or top >= r_bottom:
                    continue
                return False
            platform_forest2_reservations.append((left, top, right, bottom))
            return True

        def add_platform_forest2_if_free(x: int, y: int) -> bool:
            if not has_pf2:
                return False
            if not reserve_platform_forest2(x, y, 50, 33):
                return False
            add_custom_solid(x, y, 50, 33, "platform-forest2", rescale=True)
            return True

        main_slots = []
        min_main_platform_gap = 50

        def has_min_main_platform_gap(x: int, width: int) -> bool:
            cand_left = int(x)
            cand_right = cand_left + int(width)
            for slot in main_slots:
                slot_left = int(slot["x"])
                slot_right = slot_left + int(slot["w"])
                if cand_left < (slot_right + min_main_platform_gap) and (cand_right + min_main_platform_gap) > slot_left:
                    return False
            return True

        tier_idx = min(tier_max_idx, max(tier_min_idx, tier_min_idx + (tier_max_idx - tier_min_idx) // 2))
        tier_dir = rd.choice([-1, 1])

        x_cursor = playable_start + rd.randint(300, 415)
        while x_cursor < playable_end - 60:
            if middle_checkpoint_enabled and middle_safe_start - 20 <= x_cursor <= middle_safe_end + 20:
                x_cursor = middle_safe_end + rd.randint(18, 40) + 70
                continue

            plat_width = rd.randint(80, 150)
            y_target = tiers[tier_idx] + rd.randint(-8, 8)
            if main_slots:
                prev_y = main_slots[-1]["y"]
                delta_y = rd.randint(-140, 140)
                if -14 < delta_y < 14:
                    delta_y = 14 if rd.random() < 0.5 else -14
                y_slot = prev_y + delta_y
            else:
                y_slot = y_target
            y_slot = max(safe_min_y, min(safe_max_y, y_slot))

            if main_slots:
                min_x_for_gap = main_slots[-1]["x"] + main_slots[-1]["w"] + min_main_platform_gap
                if x_cursor < min_x_for_gap:
                    x_cursor = min_x_for_gap

            if middle_checkpoint_enabled and middle_safe_start - 20 <= x_cursor <= middle_safe_end + 20:
                x_cursor = middle_safe_end + rd.randint(18, 40) + 70
                continue

            if not has_min_main_platform_gap(x_cursor, plat_width):
                x_cursor += min_main_platform_gap
                continue

            _, width, height = add_custom_solid(
                x_cursor,
                y_slot,
                plat_width,
                30,
                "platform_forest",
                rescale=False,
            )
            main_slots.append({"x": int(x_cursor), "y": int(y_slot), "w": int(width), "h": int(height)})

            target_gap = int(max(300, min(118, (main_step - 58) + rd.randint(-main_jitter, main_jitter))))
            x_cursor += width + target_gap

            if rd.random() < 0.85:
                tier_idx += tier_dir * rd.choice([1, 1, 1, 2])

            if tier_idx >= tier_max_idx:
                tier_idx = tier_max_idx
                tier_dir = -1
            elif tier_idx <= tier_min_idx:
                tier_idx = tier_min_idx
                tier_dir = 1

        if not main_slots:
            return

        # Escalier d'entree et de sortie pour connecter sol <-> zone procedurale.
        first_slot = main_slots[0]
        last_slot = main_slots[-1]
        first_stair_steps = max(3, min(8, int(abs((floor_y - 30) - first_slot["y"]) / 34) + 1))
        first_stair_origin = max(start_x + 20, first_slot["x"] - (first_stair_steps * 58) - 20)
        first_stair_info = add_platform_staircase(
            first_stair_origin,
            floor_y - 30,
            first_slot["y"],
            direction=1,
            add_landing=True,
        )

        end_stair_origin = last_slot["x"] + last_slot["w"] + 20
        add_platform_staircase(end_stair_origin, last_slot["y"], floor_y - 30, direction=1)

        # Zone de securite resserree: protege l'escalier sans creer un grand vide apres.
        protected_until_x = first_stair_info["end_x"] + 6

        # Checkpoint central impose pour les longs segments (> 2000px), sans aleatoire concurrent.
        if middle_checkpoint_enabled:
            if main_slots:
                ref_slot = min(main_slots, key=lambda slot: abs((slot["x"] + slot["w"] // 2) - middle_center_x))
                middle_platform_y = max(safe_min_y + 25, min(safe_max_y, ref_slot["y"] + rd.randint(-8, 8)))
            else:
                middle_platform_y = max(safe_min_y + 25, min(safe_max_y, floor_y - 95))

            middle_platform_x = middle_center_x - (middle_platform_w // 2)
            add_custom_solid(middle_platform_x, middle_platform_y, middle_platform_w, 30, "platform_forest", rescale=False)

            if plant1 and has_texture("plant1"):
                plant_w_mid, _ = texture_size("plant1")
                for px in [middle_platform_x + 26, middle_platform_x + 110, middle_platform_x + 210, middle_platform_x + 320]:
                    if px + plant_w_mid <= middle_platform_x + middle_platform_w - 4:
                        add_scaled_decor("plant1", px, middle_platform_y + 2, align_bottom=True)

            #Add an anchor on the left side of the middle checkpoint so player can grapple
            if anchor and has_texture("industrial_tile"):
                add_anchor_decor(middle_platform_x + 20, middle_platform_y - 100)

            if rain_collector and has_texture("rain_collector"):
                rain_w_mid, rain_h_mid = texture_size("rain_collector")
                rain_mid_x = middle_platform_x + middle_platform_w - rain_w_mid - 20
                rain_mid_y = middle_platform_y - rain_h_mid
                rain_mid = TriggerInteract(
                    (rain_mid_x, rain_mid_y),
                    (rain_w_mid, rain_h_mid),
                    ["player"],
                    [lambda obj: refill_water(p, game)],
                )
                rain_mid.set_texture(textures["rain_collector"], rescale=True)
                collections.append(rain_mid)

            if checkpoint_switch and has_texture("switch_on"):
                sw_w_mid, sw_h_mid = (64, 64)
                cp_mid_x = middle_platform_x + 168
                cp_mid_y = middle_platform_y - sw_h_mid
                cp_mid_pos = [cp_mid_x + (sw_w_mid // 2) - 4, middle_platform_y - 48]
                checkpoint_mid = Trigger(
                    (cp_mid_x, cp_mid_y),
                    (sw_w_mid, sw_h_mid),
                    ["player"],
                    [lambda obj, cp=cp_mid_pos: save_checkpoint(p, cp, game)],
                    once=True,
                )
                checkpoint_mid.set_texture(textures["switch_on"], rescale=True)
                collections.append(checkpoint_mid)

            mid_dialog = Dialog(game.RESSOURCES["fonts"]["default"])
            mid_dialog.setup({
                "characters": [
                    {"name": "Mélanie Cavill", "texture": game.RESSOURCES["textures"]["melanie"]},
                    {"name": "System", "texture": game.RESSOURCES["textures"]["ai_icon"]},
                    {"name": "You", "texture": game.RESSOURCES["textures"]["player_base"]},
                ],
                "messages": [
                    ("System", "Checkpoint atteint : zone de sécurité établie."),
                    ("System", "Contact radio entrant !"),
                    ("System", "Interlocuteur : Mélanie Cavill. Accepter l'appel ?", [
                        ("Accepter l'appel", "accept_call", lambda e: print_info("Choix radio: appel accepté")),
                        ("Ignorer pour l'instant", "delay_call", lambda e: print_info("Choix radio: appel différé")),
                    ], "radio_choice"),

                    ("Mélanie Cavill", "Allô ? Tu me reçois ?", "accept_call"),
                    ("You", "Reçu 5 sur 5 Mélanie. Je t'écoute.", "accept_call"),
                    ("Mélanie Cavill", "C'est un soulagement, j'ai cru que tu avais été touché par les robots.", "accept_call"),
                    ("Mélanie Cavill", "D'après ta position, tu es presque arrivé à la zone industrielle au fond de la forêt. Continue !", "accept_call"),
                    ("You", "Bien reçu. Je vais essayer de trouver un chemin à travers la forêt. A plus tard !", "accept_call"),
                    #Choice unique pour terminer l'appel :
                    ("System", "Appel terminé...", [
                        ("Continuer", "dialog_end", lambda e: print_info("Choix radio: appel terminé")),
                    ], "radio_choice2"),

                    ("System", "Canal radio mis en attente. Reconnexion possible plus loin.", "delay_call"),
                    ("You", "Je rappellerai après la prochaine plateforme.", "delay_call"),
                    ("GOTO", "dialog_end"),

                    ("System", "Transmission terminée.", "dialog_end"),
                    ("STOP",),
                ],
            })
            scene.UI.add(middle_dialog_key, mid_dialog)

            dialog_trigger_mid = Trigger(
                (middle_platform_x + 170, middle_platform_y - 140),
                (160, 170),
                ["player"],
                [lambda obj, key=middle_dialog_key: scene.UI.show(key)],
                once=True,
            )
            collections.append(dialog_trigger_mid)

            # Plateformes d'approche fixes pour eviter un vide excessif autour du checkpoint central.
            approach_w = rd.randint(95, 140)
            approach_gap = rd.randint(26, 40)
            left_approach_x = middle_safe_start - approach_gap - approach_w
            right_approach_x = middle_safe_end + approach_gap
            left_approach_y = max(safe_min_y, min(safe_max_y, middle_platform_y + rd.randint(-14, 10)))
            right_approach_y = max(safe_min_y, min(safe_max_y, middle_platform_y + rd.randint(-10, 14)))

            if (
                left_approach_x + approach_w + 14 < middle_safe_start
                and left_approach_x >= playable_start
                and has_min_main_platform_gap(left_approach_x, approach_w)
            ):
                _, left_w, left_h = add_custom_solid(
                    left_approach_x,
                    left_approach_y,
                    approach_w,
                    30,
                    "platform_forest",
                    rescale=False,
                )
                main_slots.append({"x": int(left_approach_x), "y": int(left_approach_y), "w": int(left_w), "h": int(left_h)})

            if (
                right_approach_x > middle_safe_end + 14
                and right_approach_x + approach_w <= playable_end
                and has_min_main_platform_gap(right_approach_x, approach_w)
            ):
                _, right_w, right_h = add_custom_solid(
                    right_approach_x,
                    right_approach_y,
                    approach_w,
                    30,
                    "platform_forest",
                    rescale=False,
                )
                main_slots.append({"x": int(right_approach_x), "y": int(right_approach_y), "w": int(right_w), "h": int(right_h)})

            main_slots.sort(key=lambda slot: slot["x"])

        # Deuxieme chemin plus haut, regulier et deconnecte du chemin principal.
        upper_slots = []
        upper_stride = 2
        upper_offset = 1
        upper_step_limit = 14

        upper_key = None
        upper_w = 0
        upper_h = 0
        if platform_forest1 and has_texture("platform-forest1"):
            upper_key = "platform-forest1"
            upper_w, upper_h = (99, 78)
        elif platform_forest2 and has_texture("platform-forest2"):
            upper_key = "platform-forest2"
            upper_w, upper_h = (50, 33)

        if upper_key is not None:
            for idx, slot in enumerate(main_slots):
                if idx % upper_stride != upper_offset:
                    continue
                if middle_checkpoint_enabled and in_middle_safe(slot["x"], slot["w"]):
                    continue
                up_x = int(slot["x"] + (slot["w"] // 2) - (upper_w // 2))
                target_up_y = max(-320, min(safe_min_y - 42, slot["y"] - 140))
                if upper_slots:
                    prev_up_y = upper_slots[-1]["y"]
                    up_y = prev_up_y + max(-upper_step_limit, min(upper_step_limit, target_up_y - prev_up_y))
                else:
                    up_y = target_up_y

                add_custom_solid(up_x, up_y, upper_w, upper_h, upper_key, rescale=True)
                if upper_key == "platform-forest2":
                    reserve_platform_forest2(up_x, up_y, upper_w, upper_h, padding=2)
                elif upper_key == "platform-forest1" and anchor and has_texture("industrial_tile"):
                    add_anchor_decor(up_x - 35, up_y + 20)
                upper_slots.append({"x": up_x, "y": up_y, "w": upper_w, "h": upper_h})

            for i in range(len(upper_slots) - 1):
                left_u = upper_slots[i]
                right_u = upper_slots[i + 1]
                gap_u = right_u["x"] - (left_u["x"] + left_u["w"])
                if gap_u < 70:
                    continue
                upper_span_start = left_u["x"] + left_u["w"]
                upper_span_end = right_u["x"]
                if middle_checkpoint_enabled and upper_span_start <= middle_safe_end and upper_span_end >= middle_safe_start:
                    continue

                if has_pf2 and gap_u >= 120:
                    support_u_x = left_u["x"] + left_u["w"] + max(8, gap_u // 2 - 25)
                    support_u_y = int((left_u["y"] + right_u["y"]) / 2)
                    support_u_y = max(safe_min_y, min(safe_max_y, support_u_y))
                    add_platform_forest2_if_free(support_u_x, support_u_y)

                if has_moving and gap_u >= 140:
                    mp_w_u = 100
                    mp_h_u = 15
                    min_x_u = left_u["x"] + left_u["w"] + 8
                    max_x_u = right_u["x"] - mp_w_u - 8
                    if max_x_u - min_x_u >= 30:
                        mp_u_y = int((left_u["y"] + right_u["y"]) / 2)
                        travel_min_u = min_x_u
                        travel_max_u = max_x_u + mp_w_u
                        if reserve_moving_lane(travel_min_u, travel_max_u, mp_u_y, mp_h_u):
                            mp_u = Solid((min_x_u, mp_u_y), (mp_w_u, mp_h_u))
                            mp_u.set_texture(textures["moving_platform"], rescale=True)
                            moving_platforms.append({
                                "solid": mp_u,
                                "axis": "x",
                                "speed": round(rd.uniform(0.55, 1.05), 2),
                                "direction": 1,
                                "min_x": min_x_u,
                                "max_x": max_x_u,
                                "_current": float(min_x_u),
                            })
                            scene.add(mp_u, "#object")

                prev_anchor_x = x_start
                if anchor and has_texture("industrial_tile") and rd.random() < 0.35:
                    anchor_mid_x = left_u["x"] + left_u["w"] + max(6, gap_u // 2 - 12)
                    
                    #Prevents anchors from being placed too close
                    if abs(anchor_mid_x - prev_anchor_x) >= 120:
                        anchor_mid_y = min(left_u["y"], right_u["y"]) - rd.randint(55, 145)
                        add_anchor_decor(anchor_mid_x, anchor_mid_y)

        anchor_stride = 2
        anchor_offset = rd.randint(0, anchor_stride - 1)

        # Relier les grandes plateformes avec les connecteurs demandes.
        for i in range(len(main_slots) - 1):
            left_slot = main_slots[i]
            right_slot = main_slots[i + 1]
            gap = right_slot["x"] - (left_slot["x"] + left_slot["w"])
            vertical_gap = abs(right_slot["y"] - left_slot["y"])
            connector_start_x = left_slot["x"] + left_slot["w"] + 8
            connector_span_start = left_slot["x"] + left_slot["w"]
            connector_span_end = right_slot["x"]

            if connector_start_x < protected_until_x:
                continue
            if middle_checkpoint_enabled and connector_span_start <= middle_safe_end and connector_span_end >= middle_safe_start:
                continue

            if gap <= 70 and vertical_gap <= 50:
                continue

            bridge_start = left_slot["x"] + left_slot["w"] + 8
            bridge_end = right_slot["x"] - 8
            span = max(0, bridge_end - bridge_start)
            if span < 70 and vertical_gap < 50:
                continue

            support_count = 1
            if gap >= 80:
                support_count += 1
            if gap >= 140:
                support_count += 1
            if gap >= 210:
                support_count += 1
            if vertical_gap >= 55:
                support_count += 1
            support_count = max(1, min(5, support_count))

            prev_support_y = left_slot["y"]
            for s in range(1, support_count + 1):
                t = float(s) / float(support_count + 1)
                support_x = int(bridge_start + t * span)
                target_y = int(left_slot["y"] + (right_slot["y"] - left_slot["y"]) * t)
                delta_y = target_y - prev_support_y
                support_y = prev_support_y + max(-56, min(56, delta_y))
                support_y = support_y + rd.randint(-8, 8)
                support_y = max(safe_min_y, min(safe_max_y, support_y))

                placed = False
                can_place_moving = has_moving and span >= 110 and (s == ((support_count + 1) // 2) or rd.random() < 0.35)
                if can_place_moving:
                    mp_w_fb, mp_h_fb = (100, 15)
                    min_x_fb = max(bridge_start, support_x - 32)
                    max_x_fb = min(bridge_end - mp_w_fb, support_x + 32)
                    if max_x_fb - min_x_fb >= 12:
                        travel_min_fb = min_x_fb
                        travel_max_fb = max_x_fb + mp_w_fb
                        if reserve_moving_lane(travel_min_fb, travel_max_fb, support_y, mp_h_fb):
                            mp_fb = Solid((min_x_fb, support_y), (mp_w_fb, mp_h_fb))
                            mp_fb.set_texture(textures["moving_platform"], rescale=True)
                            moving_platforms.append({
                                "solid": mp_fb,
                                "axis": "x",
                                "speed": round(rd.uniform(0.60, 1.0), 2),
                                "direction": 1,
                                "min_x": min_x_fb,
                                "max_x": max_x_fb,
                                "_current": float(min_x_fb),
                            })
                            scene.add(mp_fb, "#object")
                            placed = True

                if not placed:
                    prefer_narrow = has_pf2 and (rd.random() < 0.68 or not has_pf1)
                    if prefer_narrow:
                        placed = add_platform_forest2_if_free(support_x - 25, support_y)
                        if (not placed) and has_pf1:
                            add_custom_solid(support_x - 49, support_y, 99, 78, "platform-forest1", rescale=True)
                            placed = True
                    elif has_pf1:
                        add_custom_solid(support_x - 49, support_y, 99, 78, "platform-forest1", rescale=True)
                        placed = True
                    elif has_pf2:
                        placed = add_platform_forest2_if_free(support_x - 25, support_y)

                if placed and anchor and has_texture("industrial_tile") and s % max(1, anchor_stride) == anchor_offset and rd.random() < 0.65:
                    anc_x = support_x - 12
                    anc_y = support_y - rd.randint(95, 145)
                    add_anchor_decor(anc_x, anc_y)

                prev_support_y = support_y

        if wall and has_texture("wall"):
            wall_w, wall_h = texture_size("wall")
            wall_offset = rd.randint(0, 3)
            for idx, slot in enumerate(main_slots):
                if slot["x"] < protected_until_x:
                    continue
                if middle_checkpoint_enabled and in_middle_safe(slot["x"], slot["w"]):
                    continue
                if slot["w"] < 145:
                    continue
                if idx <= 0 or idx >= len(main_slots) - 1:
                    continue
                if idx % 4 != wall_offset:
                    continue

                left_gap = slot["x"] - (main_slots[idx - 1]["x"] + main_slots[idx - 1]["w"])
                right_gap = main_slots[idx + 1]["x"] - (slot["x"] + slot["w"])
                if left_gap > 120 or right_gap > 120:
                    continue

                col_tiles_h = rd.randint(1, 2)
                col_height = wall_h * col_tiles_h
                col_y = floor_y - col_height
                col_x = slot["x"] + rd.choice([8, max(8, slot["w"] - wall_w - 8)])
                add_scaled_solid(col_x, col_y, "wall", tiles_y=col_tiles_h)

        if plant1 and has_texture("plant1"):
            plant_w, _ = texture_size("plant1")
            for slot in main_slots:
                if slot["x"] < protected_until_x:
                    continue
                if middle_checkpoint_enabled and in_middle_safe(slot["x"], slot["w"]):
                    continue
                plant_count = 1 + (1 if spawn_density > 0.55 and rd.random() < 0.50 else 0)
                for _ in range(plant_count):
                    if slot["w"] <= plant_w + 10:
                        break
                    plant_x = slot["x"] + rd.randint(4, max(4, slot["w"] - plant_w - 4))
                    add_scaled_decor("plant1", plant_x, slot["y"] + 2, align_bottom=True)

        if tree2 and has_texture("tree2"):
            tree2_w, _ = texture_size("tree2")
            tree2_offset = rd.randint(0, 1)
            for idx, slot in enumerate(main_slots):
                if slot["x"] < protected_until_x:
                    continue
                if middle_checkpoint_enabled and in_middle_safe(slot["x"], slot["w"]):
                    continue
                if idx % 2 != tree2_offset or slot["w"] < tree2_w + 12:
                    continue
                tree_x = slot["x"] + rd.randint(4, max(4, slot["w"] - tree2_w - 4))
                add_scaled_decor("tree2", tree_x, slot["y"] + 2, align_bottom=True)

        if tree1 and has_texture("tree1"):
            tree1_w, _ = texture_size("tree1")
            tree1_offset = rd.randint(0, 3)
            for idx, slot in enumerate(main_slots):
                if slot["x"] < protected_until_x:
                    continue
                if middle_checkpoint_enabled and in_middle_safe(slot["x"], slot["w"]):
                    continue
                if idx % 4 != tree1_offset or slot["w"] < tree1_w + 12:
                    continue
                tree_x = slot["x"] + rd.randint(2, max(2, slot["w"] - tree1_w - 2))
                add_scaled_decor("tree1", tree_x, slot["y"] + 2, align_bottom=True)

        if checkpoint_switch and has_texture("switch_on"):
            cp_stride = 3 if spawn_density < 0.65 else 2
            cp_offset = rd.randint(0, cp_stride - 1)
            cp_w, cp_h = (64, 64)

            for idx, slot in enumerate(main_slots):
                if slot["x"] < protected_until_x:
                    continue
                if middle_checkpoint_enabled and in_middle_safe(slot["x"], slot["w"]):
                    continue
                if idx % cp_stride != cp_offset:
                    continue
                if slot["w"] < cp_w + 8:
                    continue

                cp_x = slot["x"] + max(0, min(slot["w"] - cp_w, slot["w"] // 2 - cp_w // 2))
                cp_y = slot["y"] - cp_h
                cp_pos = [cp_x + (cp_w // 2) - 4, slot["y"] - 48]
                checkpoint_regular = Trigger(
                    (cp_x, cp_y),
                    (cp_w, cp_h),
                    ["player"],
                    [lambda obj, cp=cp_pos: save_checkpoint(p, cp, game)],
                    once=True,
                )
                checkpoint_regular.set_texture(textures["switch_on"], rescale=True)
                collections.append(checkpoint_regular)

        if rain_collector and has_texture("rain_collector"):
            rain_w, rain_h = texture_size("rain_collector")
            rain_stride = 3 if spawn_density < 0.65 else 2
            rain_offset = rd.randint(0, rain_stride - 1)
            high_limit = safe_min_y + int((safe_max_y - safe_min_y) * 0.80)

            for idx, slot in enumerate(main_slots):
                if slot["x"] < protected_until_x:
                    continue
                if middle_checkpoint_enabled and in_middle_safe(slot["x"], slot["w"]):
                    continue
                if idx % rain_stride != rain_offset:
                    continue
                if slot["y"] > high_limit:
                    continue
                if slot["w"] < rain_w + 8:
                    continue

                rain_x = slot["x"] + max(0, min(slot["w"] - rain_w, slot["w"] // 2 - rain_w // 2))
                rain_y = slot["y"] - rain_h
                rain = TriggerInteract(
                    (rain_x, rain_y),
                    (rain_w, rain_h),
                    ["player"],
                    [lambda obj: refill_water(p, game)],
                )
                rain.set_texture(textures["rain_collector"], rescale=True)
                collections.append(rain)

        if trap_idle and has_texture("trap_idle") and has_texture("trap_active"):
            trap_w, trap_h = texture_size("trap_idle")
            trap_stride = 3 if spawn_density < 0.60 else 2
            trap_offset = rd.randint(0, trap_stride - 1)

            for idx, slot in enumerate(main_slots):
                if slot["x"] < protected_until_x:
                    continue
                if middle_checkpoint_enabled and in_middle_safe(slot["x"], slot["w"]):
                    continue
                if idx < 1 or idx > len(main_slots) - 2:
                    continue
                if idx % trap_stride != trap_offset:
                    continue
                if slot["w"] < trap_w + 16:
                    continue

                trap_x = slot["x"] + slot["w"] - trap_w - 6
                trap_y = slot["y"] - trap_h
                trap = Trap(
                    (trap_x, trap_y),
                    (trap_w, trap_h),
                    "player",
                    rd.randint(12, 20),
                    cooldown=rd.randint(1200, 2200),
                )
                trap.bind_textures({
                    "idle": textures["trap_idle"],
                    "active": textures["trap_active"],
                })
                scene.add(trap, "#object")

        if enemy and has_texture("enemy"):
            enemy_sheet_w, enemy_sheet_h = texture_size("enemy")
            enemy_w = max(28, enemy_sheet_w // 11)
            enemy_h = max(28, enemy_sheet_h)

            enemy_stride = 2 if spawn_density >= 0.55 else 3
            enemy_offset = rd.randint(0, enemy_stride - 1)
            enemy_budget = max(2, min(7, len(main_slots) // enemy_stride + 1))
            enemy_count = 0

            for idx, slot in enumerate(main_slots):
                if slot["x"] < protected_until_x:
                    continue
                if middle_checkpoint_enabled and in_middle_safe(slot["x"], slot["w"]):
                    continue
                if idx < 1 or idx > len(main_slots) - 2:
                    continue
                if idx % enemy_stride != enemy_offset:
                    continue
                if enemy_count >= enemy_budget:
                    break
                if slot["w"] < enemy_w + 10:
                    continue

                enemy_x = slot["x"] + max(0, min(slot["w"] - enemy_w, slot["w"] // 2 - enemy_w // 2))
                enemy_y = slot["y"] - enemy_h
                enemy_mode = "patrol" if idx % 2 == 0 else "chase"
                enemy_range = max(120, min(280, int(slot["w"] * 0.95)))

                enemy_obj = Enemy(
                    (enemy_x, enemy_y),
                    (enemy_w, enemy_h),
                    mode=enemy_mode,
                    range=enemy_range,
                )
                enemy_obj.set_gravity(game_settings["GRAVITY"])
                enemy_obj.set_animation(Animation(textures["enemy"], 11, 50))
                collections.append(enemy_obj)
                enemy_count += 1
    

    # Mur gauche (barrière de départ) - laisser visible
    collections += [
        Solid((100, y), (60, 30)).set_texture(game.RESSOURCES["textures"]["wall"])
        for y in range(0, 430, 30)
    ]

    #%%########################################################################
    # SECTION 1 — LISIÈRE DE LA FORÊT
    ###########################################################################
    section1_start = cursor
    section1_end = section1_start + 4000
    add_ground_strip(section1_start, section1_end-3000, "platform_forest")

    #collections += [Solid((section1_start + 115, 258), (45, 27)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]
    #collections += [Solid((section1_start + 255, 225), (45, 27)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]
    #collections += [Solid((section1_start + 410, 258), (45, 27)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]
    #collections += [Solid((section1_start + 560, 225), (45, 27)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]

    # Add a lot of tree1
    pas = rd.randint(100, 250)
    x = int(section1_start)
    while x < int(section1_end-3200):
        collections += [GameObject((x, 185), (123, 116)).set_texture(game.RESSOURCES["textures"]["tree1"])]
        # Add a second tree on the right if the random number is superior to 200
        if rd.randint(1, 100) > 200:
            collections += [GameObject((x + 50, 185), (123, 116)).set_texture(game.RESSOURCES["textures"]["tree1"])]

        pas = rd.randint(100, 250)
        x += pas

   # #### Collecteur de pluie #0
   # collections += [Solid((section1_start + 440, 250), (45, 27)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]
   # rain_secret0 = TriggerInteract(
   #     (section1_start + 445, 128), (48, 48), ["player"],
   #     [lambda obj: refill_water(p, game)]
   # )
   # rain_secret0.set_texture(game.RESSOURCES["textures"]["rain_collector"])
   # collections += [rain_secret0]
#
    #Panneau #1 (situation & direction à suivre)
    dialog_ecol1 = make_ecology_dialog(
        game.RESSOURCES["fonts"]["default"],
        game.RESSOURCES["textures"]["sign"],
        "Forêt de Verdance",
        "Autrefois, cette forêt filtrait des milliers de tonnes de CO₂ par an "
        "et abritait des centaines d'espèces. Les robots de Cyclope Industries "
        "ont tout ravagé. Neutralise-les pour relancer la reforestation !"
    )
    scene.UI.add("ecol1", dialog_ecol1)
    sign1 = TriggerInteract(
        (section1_start + 300, 270), (32, 32), ["player"],
        [lambda obj: scene.UI.show("ecol1")]
    )
    sign1.set_texture(game.RESSOURCES["textures"]["sign"])
    collections += [sign1]

    #Génération procédurale de zinzin
    fillLevelWithALotOfWonderfulStuff(section1_start + 500, section1_end, 150, 800, density=1)


    ### Ennenmi #1
    #enemy1 = Enemy((section1_start + 700, 252), (48, 48), mode="patrol", range=180)
    #enemy1.set_gravity(game_settings["GRAVITY"])
    #enemy1.set_animation(Animation(game.RESSOURCES["textures"]["enemy"], 11, 50))
    #collections += [enemy1]
#
    ##Piège #1
    #trap1 = Trap((section1_start + 840, 285), (32, 15), "player", 15, cooldown=2000)
    #trap1.bind_textures({
    #    "idle":   game.RESSOURCES["textures"]["trap_idle"],
    #    "active": game.RESSOURCES["textures"]["trap_active"],
    #})
    #scene.add(trap1, "#object")
#
    #### Collecteur de pluie #1 
    #rain1 = TriggerInteract(
    #    (section1_start + 800, 252), (48, 48), ["player"],
    #    [lambda obj: refill_water(p, game)]
    #)
    #rain1.set_texture(game.RESSOURCES["textures"]["rain_collector"])
    #collections += [rain1]

    # Plateformes simples pour rythmer les grands espaces entre triggers.
    #add_simple_platforms(section1_start + 170, section1_end - 40, y=272, step=170, width=45)

    cursor = section1_end

    #%%########################################################################
    # GAP #1
    ###########################################################################
    gap1_start = cursor
    cursor += 180
    gap1_end = cursor
    #add_simple_platforms(gap1_start + 40, gap1_end - 25, y=250, step=60, width=45)

    #%%########################################################################
    # SECTION 2 — TRONCS ET PLATEFORMES MOBILES
    ###########################################################################
    section2_start = cursor
    section2_end = section2_start + 700
    add_ground_strip(section2_start, section2_end)

    ###############################################################################
##############################################################################################################################################################
###############################################################################

    #TP the player here for debug
    p.set_position((section2_start + 200, 150))


    mp1 = Solid((section2_start + 220, 220), (75, 15))
    mp1.set_texture(game.RESSOURCES["textures"]["moving_platform"])
    moving_platforms.append({
        "solid": mp1, "axis": "x", "speed": 0.85, "direction": 1,
        "min_x": section2_start + 180, "max_x": section2_start + 460, "_current": float(section2_start + 220),
    })
    scene.add(mp1, "#object")


    ### Ennemi #2
    enemy2 = Enemy((section2_start + 420, 100), (48, 48), mode="chase", range=220)
    enemy2.set_gravity(game_settings["GRAVITY"])
    enemy2.set_animation(Animation(game.RESSOURCES["textures"]["enemy"], 11, 50))
    collections += [enemy2]

    #### Piège #2
    trap2 = Trap((section2_start + 180, 185), (28, 15), "player", 20, cooldown=1500)
    trap2.bind_textures({
        "idle":   game.RESSOURCES["textures"]["trap_idle"],
        "active": game.RESSOURCES["textures"]["trap_active"],
    })
    scene.add(trap2, "#object")

    #### Panneau #2 (alerte biodiversité)
    dialog_ecol2 = make_ecology_dialog(
        game.RESSOURCES["fonts"]["default"],
        game.RESSOURCES["textures"]["sign"],
        "Alerte biodiversité",
        "Ces troncs sont les derniers vestiges d'une forêt qui couvrait "
        "800 km². Chaque unité ennemie neutralisée libère une zone "
        "pour la reforestation naturelle."
    )
    scene.UI.add("ecol2", dialog_ecol2)
    sign2 = TriggerInteract(
        (section2_end - 80, 268), (32, 32), ["player"],
        [lambda obj: scene.UI.show("ecol2")]
    )
    sign2.set_texture(game.RESSOURCES["textures"]["sign"])
    collections += [sign2]

    #add_simple_platforms(section2_start + 70, section2_end - 80, y=240, step=150, width=45)

    cursor = section2_end

    #%%########################################################################
    # SECTION 3 — FORÊT DENSE
    ###########################################################################
    section3_start = cursor
    section3_end = section3_start + 820
    add_ground_strip(section3_start, section3_end)

    cp1_x = section3_start + 40
    collections += [Solid((cp1_x, 260), (95, 15)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]

    #### Checkpoint #1
    cp1_pos = [cp1_x + 28, 212]
    checkpoint1 = Trigger(
        (cp1_x, 240), (95, 30), ["player"],
        [lambda obj: save_checkpoint(p, cp1_pos, game)],
        once=True
    )
    collections += [checkpoint1]

    #### Dialogue #1 : journal de bord
    dialog_story1 = make_story_dialog(
        game.RESSOURCES["fonts"]["default"],
        game.RESSOURCES["textures"]["sign"],
        "Journal de bord",
        [
            "Jour 14 — Les unités CF-4 carbonisent les sous-bois pour extraire "
            "les minéraux. La forêt brûle. Personne pour les arrêter.",
            "Jour 31 — Signal détecté depuis la station orbitale. "
            "Un opérateur humain serait en route. Il y a encore de l'espoir.",
        ]
    )
    scene.UI.add("story1", dialog_story1)
    sign_story1 = TriggerInteract(
        (cp1_x + 240, 270), (32, 32), ["player"],
        [lambda obj: scene.UI.show("story1")]
    )
    sign_story1.set_texture(game.RESSOURCES["textures"]["sign"])
    collections += [sign_story1]

    #### Dialogue #2 : radio de Mélanie Cavill
    dialog_melanie = make_melanie_dialog(
        game.RESSOURCES["fonts"]["default"],
        game.RESSOURCES["textures"]["melanie"],
        game.RESSOURCES["textures"]["player_base"]
    )
    scene.UI.add("melanie_radio", dialog_melanie)
    melanie_trigger = Trigger(
        (cp1_x + 440, 150), (120, 200), ["player"],
        [lambda obj: scene.UI.show("melanie_radio")],
        once=True
    )
    collections += [melanie_trigger]

    tier_low = [
        (section3_start + 120, 260, 45, 27),
        (section3_start + 300, 260, 45, 27),
        (section3_start + 470, 260, 45, 27),
        (section3_start + 650, 260, 45, 27),
    ]
    for sx, sy, sw, sh in tier_low:
        collections += [Solid((sx, sy), (sw, sh)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]

    tier_mid = [
        (section3_start + 170, 210, 85, 15),
        (section3_start + 360, 210, 105, 15),
        (section3_start + 540, 210, 80, 15),
    ]
    for sx, sy, sw, sh in tier_mid:
        collections += [Solid((sx, sy), (sw, sh)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]

    tier_high = [
        (section3_start + 220, 160, 45, 27),
        (section3_start + 420, 155, 45, 27),
        (section3_start + 620, 160, 45, 27),
    ]
    for sx, sy, sw, sh in tier_high:
        collections += [Solid((sx, sy), (sw, sh)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]

    collections += [Solid((section3_start + 385, 105), (65, 15)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]
    rain_secret1 = TriggerInteract(
        (section3_start + 382, 57), (48, 48), ["player"],
        [lambda obj: refill_water(p, game)]
    )
    rain_secret1.set_texture(game.RESSOURCES["textures"]["rain_collector"])
    collections += [rain_secret1]

    #### Ennemis #3 & #4
    enemy3 = Enemy((section3_start + 300, 152), (48, 48), mode="chase", range=230)
    enemy3.set_gravity(game_settings["GRAVITY"])
    enemy3.set_animation(Animation(game.RESSOURCES["textures"]["enemy"], 11, 50))
    collections += [enemy3]

    enemy4 = Enemy((section3_start + 610, 157), (48, 48), mode="chase", range=140)
    enemy4.set_gravity(game_settings["GRAVITY"])
    enemy4.set_animation(Animation(game.RESSOURCES["textures"]["enemy"], 11, 50))
    collections += [enemy4]

    trap3 = Trap((section3_start + 530, 285), (32, 15), "player", 20, cooldown=2500)
    trap3.bind_textures({
        "idle":   game.RESSOURCES["textures"]["trap_idle"],
        "active": game.RESSOURCES["textures"]["trap_active"],
    })
    scene.add(trap3, "#object")

    #### Interrupteur & pont d'urgence
    switch_msg = Dialog(game.RESSOURCES["fonts"]["default"])
    switch_msg.add_character("Console d'urgence", game.RESSOURCES["textures"]["sign"])
    switch_msg.add_message("Console d'urgence",
        "[SYSTÈME RÉACTIVÉ] Déploiement du pont d'urgence en cours... "
        "Accès à la zone industrielle autorisé. Bonne chance.")
    scene.UI.add("switch1_msg", switch_msg)

    switch1 = TriggerInteract(
        (section3_start + 680, 178), (22, 32), ["player"],
        [
            lambda obj: activate_switch(scene, game, "bridge1"),
            lambda obj: scene.UI.show("switch1_msg"),
        ]
    )
    switch1.set_texture(game.RESSOURCES["textures"]["switch_off"])
    collections += [switch1]

    #### Panneau #3 : sol vivant
    dialog_ecol3 = make_ecology_dialog(
        game.RESSOURCES["fonts"]["default"],
        game.RESSOURCES["textures"]["sign"],
        "Les sols vivants",
        "Un sol forestier sain abrite plus de micro-organismes "
        "que la Terre ne compte d'êtres humains. "
        "Cyclope a tout compacté. Restaurer les sols prendra des décennies. "
        "Mais on peut commencer maintenant."
    )
    scene.UI.add("ecol3", dialog_ecol3)
    sign3 = TriggerInteract(
        (section3_start + 755, 268), (32, 32), ["player"],
        [lambda obj: scene.UI.show("ecol3")]
    )
    sign3.set_texture(game.RESSOURCES["textures"]["sign"])
    collections += [sign3]

    #### Collecteur de pluie #2
    rain2 = TriggerInteract(
        (section3_start + 162, 162), (48, 48), ["player"],
        [lambda obj: refill_water(p, game)]
    )
    rain2.set_texture(game.RESSOURCES["textures"]["rain_collector"])
    collections += [rain2]

    add_simple_platforms(section3_start + 80, section3_end - 60, y=275, step=180, width=45)

    cursor = section3_end

    #%%########################################################################
    # GAP #2 — Le pont est deploie via activate_switch("bridge1")
    ###########################################################################
    gap2_start = cursor
    cursor += 220
    gap2_end = cursor

    scene.this.bridge1_range = (gap2_start, gap2_end)
    scene.this.bridge1_rows = (238, 288)

    # Guide visuel minimal en attendant l'activation du switch.
    add_simple_platforms(gap2_start + 55, gap2_end - 45, y=210, step=85, width=45)

    #%%########################################################################
    # SECTION 4 — TRANSITION / MINI-SAUTS
    ###########################################################################
    section4_start = cursor
    section4_end = section4_start + 420
    add_ground_strip(section4_start, section4_end)

    jump_pads = [
        (section4_start + 10, 285, 45, 27),
        (section4_start + 120, 268, 45, 27),
        (section4_start + 210, 250, 45, 27),
        (section4_start + 310, 268, 45, 27),
    ]
    for sx, sy, sw, sh in jump_pads:
        collections += [Solid((sx, sy), (sw, sh)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]

    #### Plateforme mobile #3 : (horizontale)
    mp3 = Solid((section4_start + 130, 232), (72, 15))
    mp3.set_texture(game.RESSOURCES["textures"]["moving_platform"])
    moving_platforms.append({
        "solid": mp3, "axis": "x", "speed": 1.1, "direction": 1,
        "min_x": section4_start + 90, "max_x": section4_start + 330, "_current": float(section4_start + 130),
    })
    scene.add(mp3, "#object")

    add_simple_platforms(section4_start + 55, section4_end - 40, y=246, step=120, width=45)

    cursor = section4_end

    #%%########################################################################
    # SECTION 5 — CAMP INDUSTRIEL EN RUINE
    ###########################################################################
    section5_start = cursor
    section5_end = section5_start + 980
    add_ground_strip(section5_start, section5_end, "wall")

    collections += [Solid((section5_start + 90, 255), (105, 15)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]
    collections += [Solid((section5_start + 250, 230), (120, 15)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]
    collections += [Solid((section5_start + 430, 255), (85, 15)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]
    collections += [Solid((section5_start + 610, 232), (95, 15)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]
    collections += [Solid((section5_start + 790, 252), (90, 15)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]

    #### Plateforme mobile #4 : (verticale)
    #mp4 = Solid((section5_start + 190, 208), (82, 15))
    #mp4.set_texture(game.RESSOURCES["textures"]["moving_platform"])
    #moving_platforms.append({
    #    "solid": mp4, "axis": "y", "speed": 0.9, "direction": 1,
    #    "min_y": 192, "max_y": 282, "_current": 208.0,
    #})
    #scene.add(mp4, "#object")

    #### Ennemi #5
    enemy5 = Enemy((section5_start + 320, 182), (48, 48), mode="patrol", range=300)
    enemy5.set_gravity(game_settings["GRAVITY"])
    enemy5.set_animation(Animation(game.RESSOURCES["textures"]["enemy"], 11, 50))
    collections += [enemy5]

    #### Pièges #4 & #5
    trap4 = Trap((section5_start + 200, 285), (32, 15), "player", 20, cooldown=1200)
    trap4.bind_textures({
        "idle":   game.RESSOURCES["textures"]["trap_idle"],
        "active": game.RESSOURCES["textures"]["trap_active"],
    })
    scene.add(trap4, "#object")

    trap5 = Trap((section5_start + 520, 285), (32, 15), "player", 25, cooldown=1800)
    trap5.bind_textures({
        "idle":   game.RESSOURCES["textures"]["trap_idle"],
        "active": game.RESSOURCES["textures"]["trap_active"],
    })
    scene.add(trap5, "#object")

    ####### Collecteur de pluie #3
    rain3 = TriggerInteract(
        (section5_start + 632, 207), (48, 48), ["player"],
        [lambda obj: refill_water(p, game)]
    )
    rain3.set_texture(game.RESSOURCES["textures"]["rain_collector"])
    collections += [rain3]

    #### Panneau #4 : camp CF-7
    dialog_ecol4 = make_ecology_dialog(
        game.RESSOURCES["fonts"]["default"],
        game.RESSOURCES["textures"]["sign"],
        "Quartier général CF-7",
        "Ce camp coordonne 200+ unités dans un rayon de 5 km. "
        "Le CF-7 est un robot de commandement modèle Cyclope Elite. "
        "Neutralise-le et toutes les unités de la zone se désactiveront."
    )
    scene.UI.add("ecol4", dialog_ecol4)
    sign4 = TriggerInteract(
        (section5_start + 900, 268), (32, 32), ["player"],
        [lambda obj: scene.UI.show("ecol4")]
    )
    sign4.set_texture(game.RESSOURCES["textures"]["sign"])
    collections += [sign4]

    #### Journal de bord #2
    dialog_story2 = make_story_dialog(
        game.RESSOURCES["fonts"]["default"],
        game.RESSOURCES["textures"]["sign"],
        "Journal de bord",
        [
            "Rapport de terrain, Jour 47 — Le CF-7 a renforcé son blindage "
            "avec des pièces prélevées sur les arbres abattus. Ironie amère.",
            "Son refroidisseur dorsal reste le seul point vulnérable. "
            "L'eau est notre seule arme. "
            "Quelqu'un viendra bien finir le travail.",
        ]
    )
    scene.UI.add("story2", dialog_story2)
    sign_story2 = TriggerInteract(
        (section5_start + 450, 225), (32, 32), ["player"],
        [lambda obj: scene.UI.show("story2")]
    )
    sign_story2.set_texture(game.RESSOURCES["textures"]["sign"])
    collections += [sign_story2]

    #### Checkpoint #2
    cp2_x = section5_start + 760
    collections += [Solid((cp2_x, 258), (105, 15)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]

    cp2_pos = [cp2_x + 27, 210]
    checkpoint2 = Trigger(
        (cp2_x, 238), (105, 30), ["player"],
        [lambda obj: save_checkpoint(p, cp2_pos, game)],
        once=True
    )
    collections += [checkpoint2]

    add_simple_platforms(section5_start + 120, section5_end - 140, y=268, step=170, width=56, texture_key="checkpoint_ground")

    cursor = section5_end

    #%%########################################################################
    # BOSS ZONE — CF-7
    ###########################################################################
    add_simple_platforms(cursor + 20, cursor + 100, y=270, step=40, width=30)
    cursor += 120

    boss_start = cursor
    boss_end = boss_start + 260
    add_ground_strip(boss_start, boss_end, "wall")

    collections += [
        Solid((boss_start - 5, y), (16, 20)).set_texture(game.RESSOURCES["textures"]["wall"])
        for y in range(155, 310, 20)
    ]
    collections += [
        Solid((boss_end - 16, y), (16, 20)).set_texture(game.RESSOURCES["textures"]["wall"])
        for y in range(155, 310, 20)
    ]

    collections += [Solid((boss_start + 40, 248), (50, 12)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]
    collections += [Solid((boss_start + 165, 248), (50, 12)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]
    collections += [Solid((boss_start + 100, 210), (60, 12)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]

    #### Boss : CF-7
    bigBoss = Boss((boss_start + 110, 252), (64, 64))
    boss_anim = Animation(game.RESSOURCES["textures"]["boss"], 11, 100)
    bigBoss.set_animation(boss_anim)
    bigBoss.set_gravity(game_settings["GRAVITY"])
    collections += [bigBoss]

    #### Dialogue #3 (intro boss)
    dialog_boss = Dialog(game.RESSOURCES["fonts"]["default"])
    dialog_boss.add_character("Mélanie Cavill", game.RESSOURCES["textures"]["melanie"])
    dialog_boss.add_character("CF-7", game.RESSOURCES["textures"]["boss"])
    dialog_boss.add_message("Mélanie Cavill",
        "Attention ! Signal thermique immense devant toi. C'est le CF-7. "
        "Son blindage est renforcé — mais son refroidisseur dorsal est exposé. "
        "Vise-le avec ton pistolet à eau !")
    dialog_boss.add_message("CF-7",
        "[PROTOCOLE ROUGE ACTIVÉ] CIBLE ORGANIQUE DÉTECTÉE. "
        "ORDRES : ÉLIMINATION. IMMÉDIATE.")
    dialog_boss.add_message("Mélanie Cavill",
        "Les décharges électriques font mal. Reste mobile et utilise "
        "les plateformes surélevées pour éviter ses attaques au sol !")
    scene.UI.add("boss_intro", dialog_boss)

    boss_trigger = Trigger(
        (boss_start - 20, 155), (20, 190), ["player"],
        [lambda obj: scene.UI.show("boss_intro")],
        once=True
    )
    collections += [boss_trigger]


    #%%### Ajout de tous les objets à la scène
    for obj in collections:
        scene.add(obj, "#object")


#%%#############################################################################
def update(game: Game):
##############################################################################
    global moving_platforms

    Debug.register_debug_entity(game, scene.this.player)
    update_player_health_ui(scene.this.player_ui_health, scene.this.player.health)
    update_ammo_ui(scene.this.player_ui_ammo, scene.this.player.ammo)

    #%%### Animation des plateformes mobiles 
    update_moving_platform(moving_platforms)

    update_ammo_ui(scene.this.player_ui_ammo, scene.this.player.ammo)


