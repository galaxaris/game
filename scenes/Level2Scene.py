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

    ### Dictionnaire qui contiendra tous les objets et seront ajoutés à la fin de start()
    collections = []     


    ### Mur gauche (barrière de départ) 
    collections += [
        Solid((80, y), (20, 30)).set_texture(game.RESSOURCES["textures"]["wall"])
        for y in range(0, 430, 30)
    ]


    #%%########################################################################
    #SECTION 1 — LISIÈRE DE LA FORÊT  (x : 100 → 500)
    ###########################################################################
    #Le joueur apparaît à [310, 110] et tombe sur le sol (y=300).

    #Sol
    collections += [
        Solid((x, 300), (80, 40)).set_texture(game.RESSOURCES["textures"]["grass"])
        for x in range(100, 500, 80)
    ]

    #Plateformes troncs — montée progressive
    collections += [Solid((185, 258), (45, 27)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]
    collections += [Solid((310, 225), (45, 27)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]
    collections += [Solid((415, 258), (45, 27)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]

    #Ledge secret haute (y=168) — récompense l'exploration verticale
    collections += [Solid((345, 168), (45, 27)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]
    rain_secret0 = TriggerInteract(
        (350, 136), (32, 32), ["player"],
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
        (150, 270), (32, 32), ["player"],
        [lambda obj: scene.UI.show("ecol1")]
    )
    sign1.set_texture(game.RESSOURCES["textures"]["sign"])
    collections += [sign1]

    ### Ennemi #1
    enemy1 = Enemy((390, 252), (48, 48), mode="patrol", range=150)
    enemy1.set_gravity(game_settings["GRAVITY"])
    enemy1.set_animation(Animation(game.RESSOURCES["textures"]["enemy"], 11, 50))
    collections += [enemy1]

    ### Piège #1
    trap1 = Trap((280, 285), (32, 15), "player", 15, cooldown=2000)
    trap1.bind_textures({
        "idle":   game.RESSOURCES["textures"]["trap_idle"],
        "active": game.RESSOURCES["textures"]["trap_active"],
    })
    scene.add(trap1, "#object")

    ### Collecteur de pluie #1 
    rain1 = TriggerInteract(
        (455, 268), (32, 32), ["player"],
        [lambda obj: refill_water(p, game)]
    )
    rain1.set_texture(game.RESSOURCES["textures"]["rain_collector"])
    collections += [rain1]


    ##########################################################################
    #GAP #1  (x : 500 → 560) — killbox active
    ##########################################################################


    ##########################################################################
    #SECTION 2 — TRONCS & PLATEFORMES MOBILES  (x : 560 → 900)
    ##########################################################################

    # Troncs fixes — motif en arc (montée puis descente)
    stump_layout = [
        (560, 285, 45, 27),
        (630, 265, 45, 27),
        (700, 248, 45, 27),
        (775, 265, 45, 27),
        (848, 285, 45, 27),
    ]
    for sx, sy, sw, sh in stump_layout:
        collections += [Solid((sx, sy), (sw, sh)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]

    #### Plateforme mobile #1 : (horizontale)
    mp1 = Solid((700, 220), (75, 15))
    mp1.set_texture(game.RESSOURCES["textures"]["moving_platform"])
    moving_platforms.append({
        "solid": mp1, "axis": "x", "speed": 0.7, "direction": 1,
        "min_x": 638, "max_x": 800, "_current": 700.0,
    })
    scene.add(mp1, "#object")

    #### Plateforme mobile #2 : (verticale)
    mp2 = Solid((800, 195), (70, 15))
    mp2.set_texture(game.RESSOURCES["textures"]["moving_platform"])
    moving_platforms.append({
        "solid": mp2, "axis": "y", "speed": 0.5, "direction": 1,
        "min_y": 175, "max_y": 265, "_current": 195.0,
    })
    scene.add(mp2, "#object")

    #### Ennemi #2
    enemy2 = Enemy((755, 200), (48, 48), mode="idle", range=200)
    enemy2.set_gravity(game_settings["GRAVITY"])
    enemy2.set_animation(Animation(game.RESSOURCES["textures"]["enemy"], 11, 50))
    collections += [enemy2]

    #### Piège #2
    trap2 = Trap((633, 250), (28, 15), "player", 20, cooldown=1500)
    trap2.bind_textures({
        "idle":   game.RESSOURCES["textures"]["trap_idle"],
        "active": game.RESSOURCES["textures"]["trap_active"],
    })
    scene.add(trap2, "#object")

    #### Panneau #2 (biodiversité)
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
        (851, 255), (32, 32), ["player"],
        [lambda obj: scene.UI.show("ecol2")]
    )
    sign2.set_texture(game.RESSOURCES["textures"]["sign"])
    collections += [sign2]


    # #########################################################################
    # CHECKPOINT #1 + DÉBUT PLANCHER 2  (x : 900)
    # #########################################################################

    #Sol 2
    collections += [
        Solid((x, 300), (80, 40)).set_texture(game.RESSOURCES["textures"]["grass"])
        for x in range(900, 1562, 80)
    ]

    #Checkpoint #1
    collections += [Solid((918, 260), (95, 15)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]

    cp1_pos = [940, 212]   # position de réapparition
    checkpoint1 = Trigger(
        (918, 240), (95, 30), ["player"],
        [lambda obj: save_checkpoint(p, cp1_pos, game)],
        once=True
    )
    collections += [checkpoint1]

    #### Dialogue #1 : journal de bord (narratif)
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
        (978, 270), (32, 32), ["player"],
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
        (1050, 150), (110, 200), ["player"],
        [lambda obj: scene.UI.show("melanie_radio")],
        once=True
    )
    collections += [melanie_trigger]


    ##########################################################################
    #SECTION 3 — FORÊT DENSE  (x : 1100 → 1560)
    ##########################################################################

    #Tier bas (y=260) — petites montées
    tier_low = [(1105, 260, 90, 15), (1235, 260, 90, 15), (1385, 260, 80, 15), (1485, 260, 70, 15)]
    for sx, sy, sw, sh in tier_low:
        collections += [Solid((sx, sy), (sw, sh)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]

    #Tier moyen (y=210)
    tier_mid = [(1145, 210, 85, 15), (1285, 210, 105, 15), (1445, 210, 80, 15)]
    for sx, sy, sw, sh in tier_mid:
        collections += [Solid((sx, sy), (sw, sh)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]

    #Tier haut (y=160) — sauts techniques
    tier_high = [(1165, 160, 72, 15), (1305, 155, 95, 15), (1462, 160, 72, 15)]
    for sx, sy, sw, sh in tier_high:
        collections += [Solid((sx, sy), (sw, sh)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]

    #Zone secrète haute (y=105) — bonus collecteur
    collections += [Solid((1195, 105), (65, 15)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]
    rain_secret1 = TriggerInteract(
        (1200, 73), (32, 32), ["player"],
        [lambda obj: refill_water(p, game)]
    )
    rain_secret1.set_texture(game.RESSOURCES["textures"]["rain_collector"])
    collections += [rain_secret1]

    #### Ennemi #3 — patrouille sur tier moyen (mode "patrol" + range)
    enemy3 = Enemy((1255, 252), (48, 48), mode="patrol", range=210)
    enemy3.set_gravity(game_settings["GRAVITY"])
    enemy3.set_animation(Animation(game.RESSOURCES["textures"]["enemy"], 11, 50))
    collections += [enemy3]

    #### Ennemi #4
    enemy4 = Enemy((1320, 107), (48, 48), mode="idle", range=120)
    enemy4.set_gravity(game_settings["GRAVITY"])
    enemy4.set_animation(Animation(game.RESSOURCES["textures"]["enemy"], 11, 50))
    collections += [enemy4]

    #### Piège #4
    trap3 = Trap((1400, 285), (32, 15), "player", 20, cooldown=2500)
    trap3.bind_textures({
        "idle":   game.RESSOURCES["textures"]["trap_idle"],
        "active": game.RESSOURCES["textures"]["trap_active"],
    })
    scene.add(trap3, "#object")

    ####Interrupteur #1 - déploie le pont du GAP #2
    # Placé sur tier_mid (y=210), accessible depuis le sol ou le tier bas.
    switch_msg = Dialog(game.RESSOURCES["fonts"]["default"])
    switch_msg.add_character("Console d'urgence", game.RESSOURCES["textures"]["sign"])
    switch_msg.add_message("Console d'urgence",
        "[SYSTÈME RÉACTIVÉ] Déploiement du pont d'urgence en cours... "
        "Accès à la zone industrielle autorisé. Bonne chance.")
    scene.UI.add("switch1_msg", switch_msg)

    switch1 = TriggerInteract(
        (1298, 178), (22, 32), ["player"],
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
        (1479, 230), (32, 32), ["player"],
        [lambda obj: scene.UI.show("ecol3")]
    )
    sign3.set_texture(game.RESSOURCES["textures"]["sign"])
    collections += [sign3]

    #### Collecteur de pluie #2
    rain2 = TriggerInteract(
        (1145, 178), (32, 32), ["player"],
        [lambda obj: refill_water(p, game)]
    )
    rain2.set_texture(game.RESSOURCES["textures"]["rain_collector"])
    collections += [rain2]


    ##########################################################################
    #GAP #2  (x : 1562 → 1640)
    #Le pont est déployé dynamiquement par activate_switch("bridge1").
    ##########################################################################


    ##########################################################################
    #SECTION 4 — TRANSITION / MINI-SAUTS  (x : 1640 → 1800)
    ##########################################################################

    jump_pads = [
        (1642, 285, 55, 15),
        (1712, 270, 55, 15),
        (1762, 285, 72, 15),
    ]
    for sx, sy, sw, sh in jump_pads:
        collections += [Solid((sx, sy), (sw, sh)).set_texture(game.RESSOURCES["textures"]["tree_stump"])]

    #### Plateforme mobile #3
    mp3 = Solid((1672, 232), (72, 15))
    mp3.set_texture(game.RESSOURCES["textures"]["moving_platform"])
    moving_platforms.append({
        "solid": mp3, "axis": "x", "speed": 1.1, "direction": 1,
        "min_x": 1642, "max_x": 1782, "_current": 1672.0,
    })
    scene.add(mp3, "#object")


    ##########################################################################
    #SECTION 5 — CAMP INDUSTRIEL EN RUINE  (x : 1800 → 2340)
    ##########################################################################

    #Sol industriel (texture wall)
    collections += [
        Solid((x, 300), (80, 40)).set_texture(game.RESSOURCES["textures"]["wall"])
        for x in range(1800, 2355, 80)
    ]

    #Plateformes 
    collections += [Solid((1842, 255), (105, 15)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]
    collections += [Solid((1985, 230), (120, 15)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]
    collections += [Solid((2135, 255), (85, 15)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]
    collections += [Solid((2245, 232), (95, 15)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]

    #### Plateforme mobile #4 (verticale)
    mp4 = Solid((1922, 208), (82, 15))
    mp4.set_texture(game.RESSOURCES["textures"]["moving_platform"])
    moving_platforms.append({
        "solid": mp4, "axis": "y", "speed": 0.9, "direction": 1,
        "min_y": 192, "max_y": 282, "_current": 208.0,
    })
    scene.add(mp4, "#object")

    #### Ennemi #5
    enemy5 = Enemy((2005, 182), (48, 48), mode="patrol", range=260)
    enemy5.set_gravity(game_settings["GRAVITY"])
    enemy5.set_animation(Animation(game.RESSOURCES["textures"]["enemy"], 11, 50))
    collections += [enemy5]

    #### Piège #4 et #5
    trap4 = Trap((1922, 285), (32, 15), "player", 20, cooldown=1200)
    trap4.bind_textures({
        "idle":   game.RESSOURCES["textures"]["trap_idle"],
        "active": game.RESSOURCES["textures"]["trap_active"],
    })
    scene.add(trap4, "#object")

    trap5 = Trap((2082, 285), (32, 15), "player", 25, cooldown=1800)
    trap5.bind_textures({
        "idle":   game.RESSOURCES["textures"]["trap_idle"],
        "active": game.RESSOURCES["textures"]["trap_active"],
    })
    scene.add(trap5, "#object")

    ####### Collecteur de pluie #3
    rain3 = TriggerInteract(
        (2148, 223), (32, 32), ["player"],
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
        (2252, 202), (32, 32), ["player"],
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
            "L'eau — sa hantise — est notre seule arme. "
            "Quelqu'un viendra bien finir le travail.",
        ]
    )
    scene.UI.add("story2", dialog_story2)
    sign_story2 = TriggerInteract(
        (2160, 225), (32, 32), ["player"],
        [lambda obj: scene.UI.show("story2")]
    )
    sign_story2.set_texture(game.RESSOURCES["textures"]["sign"])
    collections += [sign_story2]


    ##########################################################################
    #CHECKPOINT #2  (x : 2290)
    ##########################################################################

    collections += [Solid((2288, 258), (105, 15)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]

    cp2_pos = [2315, 210]
    checkpoint2 = Trigger(
        (2288, 238), (105, 30), ["player"],
        [lambda obj: save_checkpoint(p, cp2_pos, game)],
        once=True
    )
    collections += [checkpoint2]


    ##########################################################################
    #BOSS ZONE — CF-7  (x : 2350 → 2530)
    ##########################################################################

    #Sol arène
    collections += [
        Solid((x, 300), (80, 40)).set_texture(game.RESSOURCES["textures"]["wall"])
        for x in range(2350, 2535, 80)
    ]

    #Murs latéraux de l'arène
    collections += [
        Solid((2345, y), (16, 20)).set_texture(game.RESSOURCES["textures"]["wall"])
        for y in range(155, 310, 20)
    ]
    collections += [
        Solid((2514, y), (16, 20)).set_texture(game.RESSOURCES["textures"]["wall"])
        for y in range(155, 310, 20)
    ]

    #Petites plateformes dans l'arène
    collections += [Solid((2385, 248), (50, 12)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]
    collections += [Solid((2490, 248), (50, 12)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]
    collections += [Solid((2438, 210), (60, 12)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]

    #Boss CF-7
    bigBoss = Boss((2428, 252), (64, 64))
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
        (2345, 155), (20, 190), ["player"],
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


