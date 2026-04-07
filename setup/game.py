#%%################ IMPORTS ####################
################################################
from game.setup.imports_collection import *
from game.setup.game_settings import init_game_settings
from game.setup.Setup import setup_game
from game.scripts.MainScript import Start, Update

class Omicronde:
    RENDER_WIDTH: int
    RENDER_HEIGHT: int
    WIDTH: int
    HEIGHT: int
    NAME: str
    FPS: int
    GRAVITY: float

    assets_path: str
    font_G: str

    game: Game
    scene: Scene

    player: Player

    def __init__(self):
        setup_game(self)

        ####################### TODO TODO TODO ########################
        ###############################################################
        #### Ô, toi lecteur aguerri dont les yeux perçants ont décelé ce commentaire, sache que moi, GauGoth Corp., ai placé tous les élements uniques à la démo dans 
        # cette fonction. Prend NOTE que tout ce qui se trouve dedans doit être implémenté et dispaché dans les JSON du dossier `scenes`.
        # A bientôt, et que le code soit avec toi.

        def ToBeImplementedInTheLevelsJson():
            #%%################ ENTITIES INITIALIZATION ####################
            ################################################################

            #TODO: to be set later in levels JSON
            #TODO: Review Ennemy Turret
            self.entity = Enemy((650, 350), (48, 48), mode="idle", range=300)
            self.entity.set_gravity(self.GRAVITY)
            self.entity.set_animation(Animation(self.RESSOURCES["textures"]["enemy"], 11, 50))

            self.boss = Boss((700, 350), (64, 64))
            boss_texture = Animation(self.RESSOURCES["textures"]["boss"], 11, 100)
            self.boss.set_animation(boss_texture)
            self.boss.set_gravity(self.GRAVITY)


            #%%################ ENVIRONMENT SETUP ####################
            ##########################################################

            # TODO: to be implemented in a JSON BDD (when we will have a level system, with the editor)

            ##### SOLIDS ####
            self.collections = []
            self.collections += [Solid((x, 600), (100, 100)) for x in range(0, 400, 100)]  # Floor
            self.collections += [Solid((x, 600), (100, 100)) for x in range(500, 1000, 100)]  # Floor, leaving a gap for the player to fall through
            self.collections += [Solid((0, y), (100, 100)) for y in range(200, 700, 100)] # Wall at our left
            self.collections += [Solid((250, 550), (200, 20))] # First platform
            self.collections += [Solid((550, 500), (500, 50))] # Second platform

            anchor_point = Solid((600, 300), (20, 20))
            anchor_point.add_tag("anchor")
            self.collections += [anchor_point]

            for coll in self.collections:
                coll.set_color((200, 200, 200))
                coll.set_texture(self.RESSOURCES["textures"]["grass"])

            #### TRIGGERS ####
            # (see game/scripts/triggers.py for the functions (callbacks) called by the triggers)
            # A trigger is an invisible area that executes a callback function when the targeted object enter it.

            ### NOTE ### to pass a callback, use "lambda" or "functools.partial". See the Trigger module for more info. Syntax is as follows:
            # lambda obj: call_back_function(params, ...)

            ### Predefined triggers
            ### Creates a killBox that kills the player when falling too much (y > HEIGHT)
            create_killBox(self.collections, 50, self.HEIGHT)

            ### Custom triggers
            self.collections += [Trigger((832, 550), (32, 32), ["player"],[lambda obj: summon_stairs1(self.scene, self.RESSOURCES["textures"]["player"], self.RESSOURCES["textures"]["sign"], self.RESSOURCES["textures"]["sign"], self.HEIGHT, self.RESSOURCES["textures"]["grass"], self.RESSOURCES["textures"]["checkpoint_ground"], dialog_font=self.RESSOURCES["fonts"]["default"])],once=True)]

            trap = Trap((950, 550), (32, 32), "player", 10, cooldown=3000)
            trap.bind_textures({
                "idle": self.RESSOURCES["textures"]["trap_idle"],
                "active": self.RESSOURCES["textures"]["trap_active"]
            })
            self.scene.add(trap, "#object")

            #%%################ BACKGROUND SETUP ###################
            ########################################################

            ### Wonderful parallax background
            p_bg = ParallaxBackground((self.RENDER_WIDTH, self.RENDER_HEIGHT), [
                ParallaxLayer(pg.Vector2(0.9, 0.45), self.RESSOURCES["textures"]["parallax1"]),
                ParallaxLayer(pg.Vector2(0.7, 0.35), self.RESSOURCES["textures"]["parallax2"]),
                ParallaxLayer(pg.Vector2(0.5, 0.25), self.RESSOURCES["textures"]["parallax3"]),
            ], (75, 105, 52))
            self.scene.set_background(p_bg)

            b_bg = Background(self.RESSOURCES["textures"]["menu_bg"], False, (self.RENDER_WIDTH, self.RENDER_HEIGHT))


            #%%################# MAIN MENU SCENE ########################
            ############################################################

            self.menu_scene = Scene((self.RENDER_WIDTH, self.RENDER_HEIGHT))
            self.menu_scene.set_background(b_bg)
            self.menu_scene.camera.set_offset((self.RENDER_WIDTH // 2 - self.player.size.x, self.RENDER_HEIGHT // 2 - self.player.size.y))

            self.scene.add(self.player, "#player")
            self.scene.add(self.entity, "#enemies")
            self.scene.add(self.boss, "#enemies")

            self.game.scene = self.menu_scene
            self.game_event_manager.Instances.bindInstance("menu_scene", self.menu_scene)

            #%%################ UI setup ###################
            ################################################

            self.player_ui_health = ProgressBar((30, 10), (100, 10), (100, 100, 100), "green", 100)
            self.player_ui_heart = UIElement((8, 8), (16, 16))
            self.player_ui_heart.set_texture(self.RESSOURCES["textures"]["health"], True)
            self.scene.UI.add("player_health", self.player_ui_health)
            self.scene.UI.add("player_heart", self.player_ui_heart)
            self.scene.UI.show("player_health")
            self.scene.UI.show("player_heart")

            dialog = Dialog(self.RESSOURCES["fonts"]["default"])

            dialog.setup({
                "characters": [
                    {"name": "Galaxaris", "texture": self.RESSOURCES["textures"]["icon"]},
                    {"name": "You", "texture": self.RESSOURCES["textures"]["player"]}
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
            self.scene.UI.add("test", dialog)

            info_box = TriggerInteract((110, 568), (32, 32), ["player"], [lambda obj: self.scene.UI.show("test")])
            info_box.set_texture(self.RESSOURCES["textures"]["sign"])
            self.collections += [info_box]


            dialog2 = Dialog(self.RESSOURCES["fonts"]["default"])
            dialog2.add_character("Sign", self.RESSOURCES["textures"]["sign"])
            dialog2.add_message("Sign", ">>> This is the Way >>>")

            self.scene.UI.add("sign", dialog2)
            info_box2 = TriggerInteract((694, 568), (32, 32), ["player"], [lambda obj: self.scene.UI.show("sign")])
            info_box2.set_texture(self.RESSOURCES["textures"]["sign"])
            self.collections+= [info_box2]

            ### MENU
            menu = menu_in_game(self.scene, self.menu_scene, "menu", self.RENDER_WIDTH, self.RENDER_HEIGHT, self.player, self.game)
            self.scene.UI.add("menu", menu)

            menu2 = main_menu(self.menu_scene, self.scene, "main_menu", self.RENDER_WIDTH, self.RENDER_HEIGHT, self.game)
            self.menu_scene.UI.add("main_menu", menu2)
            self.menu_scene.UI.show("main_menu")


        #%% Calling ToBeImplementedInTheLevelsJson
        ToBeImplementedInTheLevelsJson()


    def debug_info(self):
        Debug.register_debug_entity(self.game, self.player)
        Debug.register_debug_entity(self.game, self.entity)

    def launch(self):
        Start(self)
        self.game.run(lambda: Update(self))

