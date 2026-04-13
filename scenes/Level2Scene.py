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

from api.Game import Game
from api.engine.Scene import Scene
from api.environment.Solid import Solid
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
    ground_w = 80

    def add_ground_strip(x_start: int, x_end: int, texture_key: str = "grass"):
        for x in range(int(x_start), int(x_end), ground_w):
            collections.append(
                Solid((x, floor_y), (ground_w, 40)).set_texture(game.RESSOURCES["textures"][texture_key])
            )

    def add_simple_platforms(
        x_start: int,
        x_end: int,
        y: int,
        step: int = 120,
        width: int = 60,
        texture_key: str = "tree_stump"
    ):
        for x in range(int(x_start), int(x_end), int(step)):
            collections.append(
                Solid((x, y), (width, 15)).set_texture(game.RESSOURCES["textures"][texture_key])
            )

    # Mur gauche (barrière de départ)
    collections += [
        Solid((80, y), (20, 30)).set_texture(game.RESSOURCES["textures"]["wall"])
        for y in range(0, 430, 30)
    ]

    #%%########################################################################
    # SECTION 1 — LISIÈRE DE LA FORÊT
    ###########################################################################
    section1_start = cursor
    section1_end = section1_start + 720
    add_ground_strip(section1_start, section1_end, "grass")

    collections += [Solid((section1_start + 115, 258), (45, 27)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]
    collections += [Solid((section1_start + 255, 225), (45, 27)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]
    collections += [Solid((section1_start + 410, 258), (45, 27)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]
    collections += [Solid((section1_start + 560, 225), (45, 27)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]

    collections += [Solid((section1_start + 340, 168), (45, 27)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]
    rain_secret0 = TriggerInteract(
        (section1_start + 345, 128), (48, 48), ["player"],
        [lambda obj: refill_water(p, game)]
    )
    rain_secret0.set_texture(game.RESSOURCES["textures"]["rain_collector"])
    collections += [rain_secret0]

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
        (section1_start + 55, 270), (32, 32), ["player"],
        [lambda obj: scene.UI.show("ecol1")]
    )
    sign1.set_texture(game.RESSOURCES["textures"]["sign"])
    collections += [sign1]

    ### Ennenmi #1
    enemy1 = Enemy((section1_start + 365, 252), (48, 48), mode="patrol", range=180)
    enemy1.set_gravity(game_settings["GRAVITY"])
    enemy1.set_animation(Animation(game.RESSOURCES["textures"]["enemy"], 11, 50))
    collections += [enemy1]

    #Piège #1
    trap1 = Trap((section1_start + 240, 285), (32, 15), "player", 15, cooldown=2000)
    trap1.bind_textures({
        "idle":   game.RESSOURCES["textures"]["trap_idle"],
        "active": game.RESSOURCES["textures"]["trap_active"],
    })
    scene.add(trap1, "#object")

    ### Collecteur de pluie #1 
    rain1 = TriggerInteract(
        (section1_start + 632, 252), (48, 48), ["player"],
        [lambda obj: refill_water(p, game)]
    )
    rain1.set_texture(game.RESSOURCES["textures"]["rain_collector"])
    collections += [rain1]

    # Plateformes simples pour rythmer les grands espaces entre triggers.
    add_simple_platforms(section1_start + 170, section1_end - 40, y=272, step=170, width=45)

    cursor = section1_end

    #%%########################################################################
    # GAP #1
    ###########################################################################
    gap1_start = cursor
    cursor += 180
    gap1_end = cursor
    add_simple_platforms(gap1_start + 40, gap1_end - 25, y=250, step=60, width=38)

    #%%########################################################################
    # SECTION 2 — TRONCS ET PLATEFORMES MOBILES
    ###########################################################################
    section2_start = cursor
    section2_end = section2_start + 700
    add_ground_strip(section2_start, section2_end, "grass")

    stump_layout = [
        (0, 285, 45, 27),
        (95, 268, 45, 27),
        (200, 248, 45, 27),
        (315, 232, 45, 27),
        (440, 248, 45, 27),
        (560, 268, 45, 27),
        (660, 285, 45, 27),
    ]
    for dx, sy, sw, sh in stump_layout:
        collections += [
            Solid((section2_start + dx, sy), (sw, sh)).set_texture(game.RESSOURCES["textures"]["tree_stump"])
        ]

    mp1 = Solid((section2_start + 220, 220), (75, 15))
    mp1.set_texture(game.RESSOURCES["textures"]["moving_platform"])
    moving_platforms.append({
        "solid": mp1, "axis": "x", "speed": 0.85, "direction": 1,
        "min_x": section2_start + 180, "max_x": section2_start + 460, "_current": float(section2_start + 220),
    })
    scene.add(mp1, "#object")

    #### Plateforme mobile #2 : (verticale)
    mp2 = Solid((section2_start + 520, 195), (70, 15))
    mp2.set_texture(game.RESSOURCES["textures"]["moving_platform"])
    moving_platforms.append({
        "solid": mp2, "axis": "y", "speed": 0.5, "direction": 1,
        "min_y": 175, "max_y": 265, "_current": 195.0,
    })
    scene.add(mp2, "#object")

    ### Ennemi #2
    enemy2 = Enemy((section2_start + 360, 200), (48, 48), mode="idle", range=220)
    enemy2.set_gravity(game_settings["GRAVITY"])
    enemy2.set_animation(Animation(game.RESSOURCES["textures"]["enemy"], 11, 50))
    collections += [enemy2]

    #### Piège #2
    trap2 = Trap((section2_start + 180, 285), (28, 15), "player", 20, cooldown=1500)
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
        (section2_end - 60, 255), (32, 32), ["player"],
        [lambda obj: scene.UI.show("ecol2")]
    )
    sign2.set_texture(game.RESSOURCES["textures"]["sign"])
    collections += [sign2]

    add_simple_platforms(section2_start + 70, section2_end - 80, y=240, step=150, width=52)

    cursor = section2_end

    #%%########################################################################
    # SECTION 3 — FORÊT DENSE
    ###########################################################################
    section3_start = cursor
    section3_end = section3_start + 820
    add_ground_strip(section3_start, section3_end, "grass")

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
        (section3_start + 120, 260, 90, 15),
        (section3_start + 300, 260, 90, 15),
        (section3_start + 470, 260, 80, 15),
        (section3_start + 650, 260, 70, 15),
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
        (section3_start + 220, 160, 72, 15),
        (section3_start + 420, 155, 95, 15),
        (section3_start + 620, 160, 72, 15),
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

    enemy3 = Enemy((section3_start + 335, 252), (48, 48), mode="patrol", range=230)
    enemy3.set_gravity(game_settings["GRAVITY"])
    enemy3.set_animation(Animation(game.RESSOURCES["textures"]["enemy"], 11, 50))
    collections += [enemy3]

    enemy4 = Enemy((section3_start + 610, 107), (48, 48), mode="idle", range=140)
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
        (section3_start + 755, 230), (32, 32), ["player"],
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

    add_simple_platforms(section3_start + 80, section3_end - 60, y=275, step=180, width=48)

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
    add_simple_platforms(gap2_start + 55, gap2_end - 45, y=210, step=85, width=34)

    #%%########################################################################
    # SECTION 4 — TRANSITION / MINI-SAUTS
    ###########################################################################
    section4_start = cursor
    section4_end = section4_start + 420
    add_ground_strip(section4_start, section4_end, "grass")

    jump_pads = [
        (section4_start + 10, 285, 65, 15),
        (section4_start + 120, 268, 60, 15),
        (section4_start + 210, 250, 60, 15),
        (section4_start + 310, 268, 60, 15),
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

    add_simple_platforms(section4_start + 55, section4_end - 40, y=246, step=120, width=46)

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
    mp4 = Solid((section5_start + 190, 208), (82, 15))
    mp4.set_texture(game.RESSOURCES["textures"]["moving_platform"])
    moving_platforms.append({
        "solid": mp4, "axis": "y", "speed": 0.9, "direction": 1,
        "min_y": 192, "max_y": 282, "_current": 208.0,
    })
    scene.add(mp4, "#object")

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
        (section5_start + 900, 202), (32, 32), ["player"],
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
    for mp in moving_platforms:
        s = mp["solid"]
        mp["_current"] += mp["speed"] * mp["direction"]

        if mp["axis"] == "x":
            x_new = int(mp["_current"])
            s.rect.x = x_new
            try:
                s.pos[0] = float(mp["_current"])
            except (TypeError, AttributeError):
                pass
            if mp["_current"] >= mp["max_x"] or mp["_current"] <= mp["min_x"]:
                mp["direction"] *= -1

        elif mp["axis"] == "y":
            y_new = int(mp["_current"])
            s.rect.y = y_new
            try:
                s.pos[1] = float(mp["_current"])
            except (TypeError, AttributeError):
                pass
            if mp["_current"] >= mp["max_y"] or mp["_current"] <= mp["min_y"]:
                mp["direction"] *= -1


    update_ammo_ui(scene.this.player_ui_ammo, scene.this.player.ammo)


