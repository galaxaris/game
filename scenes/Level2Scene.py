from api.Game import Game
from api.engine.Scene import Scene
from api.environment.Solid import Solid
from api.utils import Debug
from game.scripts.levels.level_generation import init_level
from game.scripts.levels.level_ui import update_player_health_ui, update_ammo_ui
from game.scripts.player_manager import init_player
from api.environment.Trigger import TriggerInteract
from api.UI.Dialog import Dialog
from api.utils.Console import print_info, print_success, print_error, print_warning
from api.entity.Enemy import Enemy
from game.scripts.levels.level1 import summon_stairs1
from api.entity.Boss import Boss
from api.environment.Trap import Trap
from api.environment.Trigger import Trigger
from api.environment.Trigger import TriggerInteract
from api.environment.Solid import Solid
from api.assets.Animation import Animation

from game.Variables import game_settings, player_settings


scene = None
player = None

def start(game: Game):
    global scene
    global player
    scene = Scene(game.render_size)
    scene.name = "Level2Scene"
    scene.this.player = init_player(game)
    init_level(game, scene, scene.this.player)
    game.audio_manager.play_music("level2")


    collections = []

    #%%################ ENVIRONMENT SETUP ####################
    ##########################################################

    ##### SOLIDS ####
    # TODO: to be implemented in a JSON BDD (when we will have a level system, with the editor)
    #UPDATE: doesn't have the f***ing time, hardcoded... The editor is not used...

    collections += [Solid((x, 300), (100, 100)).set_texture(game.RESSOURCES["textures"]["grass"]) for x in range(0, 400, 100)]  # Floor
    collections += [Solid((x, 300), (100, 100)).set_texture(game.RESSOURCES["textures"]["grass"]) for x in
                         range(500, 1000, 100)]  # Floor, leaving a gap for the player to fall through
    collections += [Solid((0, y), (100, 100)).set_texture(game.RESSOURCES["textures"]["wall"]) for y in range(200, 700, 100)]  # Wall at our left
    collections += [Solid((250, 250), (200, 20)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]  # First platform
    collections += [Solid((550, 200), (500, 50)).set_texture(game.RESSOURCES["textures"]["checkpoint_ground"])]  # Second platform

    anchor_block = Solid((600, 100), (20, 20)).set_color((255, 0, 0))
    anchor_block.add_tag("anchor")
    collections += [anchor_block]

    #%%################ ENTITIES INITIALIZATION ####################
    ################################################################

    #TODO: to be set later in levels JSON
    #TODO: Review Ennemy Turret
    ennemy1 = Enemy((650, 350), (48, 48), mode="idle", range=300)
    ennemy1.set_gravity(game_settings["GRAVITY"])
    ennemy1.set_animation(Animation(game.RESSOURCES["textures"]["enemy"], 11, 50))


    bigBoss = Boss((700, 350), (64, 64))
    boss_texture = Animation(game.RESSOURCES["textures"]["boss"], 11, 100)
    bigBoss.set_animation(boss_texture)
    bigBoss.set_gravity(game_settings["GRAVITY"])
    collections += [ennemy1, bigBoss]

    #### TRIGGERS ####
    # (see game/scripts/triggers.py for the functions (callbacks) called by the triggers)
    # A trigger is an invisible area that executes a callback function when the targeted object enter it.

    ### NOTE ### to pass a callback, use "lambda" or "functools.partial". See the Trigger module for more info. Syntax is as follows:
    # lambda obj: call_back_function(params, ...)

    ### Predefined triggers
    ### Creates a killBox that kills the player when falling too much (y > HEIGHT)

    ### Custom triggers
    collections += [Trigger((832, 550), (32, 32), ["player"],[lambda obj: summon_stairs1(scene, game.RESSOURCES["textures"]["player"], game.RESSOURCES["textures"]["sign"], game.RESSOURCES["textures"]["sign"], game.size[1], game.RESSOURCES["textures"]["grass"], game.RESSOURCES["textures"]["checkpoint_ground"], dialog_font=game.RESSOURCES["fonts"]["default"])],once=True)]

    trap = Trap((950, 550), (32, 32), "player", 10, cooldown=3000)
    trap.bind_textures({
        "idle": game.RESSOURCES["textures"]["trap_idle"],
        "active": game.RESSOURCES["textures"]["trap_active"]
    })
    scene.add(trap, "#object")


    dialog = Dialog(game.RESSOURCES["fonts"]["default"])

    dialog.setup({
        "characters": [
            {"name": "Galaxaris", "texture": game.RESSOURCES["textures"]["icon"]},
            {"name": "You", "texture": game.RESSOURCES["textures"]["player"]}
        ],
        "messages": [
            # --- INTRODUCTION ---
            ("Galaxaris", "Ah, te voilà enfin réveillé ! Je commençais à m'inquiéter."),
            ("You", "Où... Où suis-je ? Et qui êtes-vous ?"),
            ("Galaxaris", "Je suis Galaxaris, le gardien de l'Omicronde. Bienvenue dans notre moteur de jeu !"),

            # --- PREMIER CHOIX (Test d'embranchement simple) ---
            ("Galaxaris", "Dis-moi, comment te sens-tu après ce voyage trans-dimensionnel ?", [
                ("Un peu étourdi...", "feel_dizzy", lambda e: print_info("Statut: Étourdi")),
                ("Prêt pour l'aventure !", "feel_ready", lambda e: print_info("Statut: Prêt"))
            ], "intro_choice"),

            # Branche 1 : Étourdi
            ("Galaxaris", "C'est normal, le passage en Python secoue un peu au début. Prends ton temps.",
            "feel_dizzy"),
            ("GOTO", "main_hub"),

            # Branche 2 : Prêt
            ("Galaxaris", "Parfait ! J'aime cet enthousiasme ! Le code source a besoin de héros comme toi.",
            "feel_ready"),
            ("GOTO", "main_hub"),

            # --- HUB CENTRAL (Test de boucle et choix multiples) ---
            ("Galaxaris", "Maintenant, que veux-tu tester dans cette démonstration de l'API ?", [
                ("Le système de combat", "test_combat", lambda e: print_info("Choix: Combat")),
                ("L'exploration spatiale", "test_explore", lambda e: print_info("Choix: Exploration")),
                ("Rien, je veux quitter le dialogue", "end_dialog", lambda e: print_info("Choix: Quitter"))
            ], "main_hub"),

            # Option A : Combat
            ("Galaxaris",
            "Excellent choix. Le système de collision de Pygame est redoutable. Fais attention à tes points de vie !",
            "test_combat"),
            ("You", "Je suis armé de ma fidèle épée en pixels, je ne crains rien !"),
            ("GOTO", "main_hub"),  # Retour au choix principal

            # Option B : Exploration
            ("Galaxaris", "L'univers est vaste ! Nous avons des tuiles infinies générées de manière procédurale.",
            "test_explore"),
            ("You", "J'espère qu'il y a des easter eggs cachés dans le décor..."),
            ("GOTO", "main_hub"),  # Retour au choix principal

            # Option C : Quitter
            ("Galaxaris",
            "Très bien, je te laisse te balader. Appuie sur la touche d'interaction si tu as besoin d'aide !",
            "end_dialog"),
            ("You", "Merci Galaxaris, à plus tard !"),

            # --- FIN DU DIALOGUE ---
            ("STOP")
        ]
    })
    scene.UI.add("test", dialog)

    info_box = TriggerInteract((110, 568), (32, 32), ["player"], [lambda obj: scene.UI.show("test")])
    info_box.set_texture(game.RESSOURCES["textures"]["sign"])
    collections += [info_box]


    dialog2 = Dialog(game.RESSOURCES["fonts"]["default"])
    dialog2.add_character("Sign", game.RESSOURCES["textures"]["sign"])
    dialog2.add_message("Sign", ">>> This is the Way >>>")

    scene.UI.add("sign", dialog2)
    info_box2 = TriggerInteract((694, 568), (32, 32), ["player"], [lambda obj: scene.UI.show("sign")])
    info_box2.set_texture(game.RESSOURCES["textures"]["sign"])
    collections+= [info_box2]

    for colls in collections:
        scene.add(colls, "#object")



def update(game: Game):
    Debug.register_debug_entity(game, scene.this.player)
    update_player_health_ui(scene.this.player_ui_health, scene.this.player.health)
    update_ammo_ui(scene.this.player_ui_ammo, scene.this.player.ammo)


