"""
=== Omicronde Project Game - Galaxaris ===

This is the entry point of the Omicronde Game. Built using the Omicronde API.

Authors: Galaxaris & Associates

v.Beta (in development)
- 03/03/2026

Copyright (c) 2026 Galaxaris & Associates. All rights reserved.

"""

### TODO: levels to be implemented and loaded in a JSON BDD (using the editor) => GameObjects, triggers, UI, background, music, etc...

### TODO: create an 'InputManager' to centralize game input handling
### TODO: create a 'SceneManager' to manage multiple game scenes (menus, levels...) and transitions between them

### TODO: create a 'ResourceManager' to centralize the loading and stock of game assets
    ## => try/except for loading function, "pink" texture as fallback
    ### TODO: create a 'TextureManager' to manage and stock game textures; texture atlases (=> sprites) and animations
        ## => TODO: define a standard for texture atlases & anims (associated .json files?)
    ### TODO: create an 'AudioManager' to manage and stock game SFX and music
    ### TODO: create a 'UIManager' to define specific game UI elements and keep an overall style (fonts, colors...)

#%%################ IMPORTS ####################
################################################
#### RUN THE GAME WITH "python -m game.main" FROM THE ROOT DIRECTORY OF THE PROJECT ####

### Libs ###
import os
from os.path import join
import time

#### CHANGE WORK DIRECTORY TO THE GAME FOLDER ####
#=> relative paths for assets loading is managed properly. Can be runned then from anywhere without issue
os.chdir(os.path.dirname(os.path.abspath(__file__)))

### API ###
from api.Game import Game

from api.UI.Button import Button
from api.UI.Dialog import Dialog
from api.UI.Modal import Modal
from api.UI.Text import Text
from api.UI.TextBox import TextBox

from api.assets.Animation import Animation
from api.assets.Resource import Resource, ResourceType
from api.assets.Texture import Texture
from api.assets.AudioManager import AudioManager

from api.engine.Scene import Scene

from api.entity.Player import Player

from api.environment.Background import Background
from api.environment.Parallax import ParallaxLayer, ParallaxBackground
from api.environment.Trigger import Trigger, TriggerInteract
from api.environment.Solid import Solid

from api.utils import Debug, Fonts
from api.utils.InputManager import get_inputs, get_once_inputs, prevent_input, get_held_inputs, onKeyDown, onKeyUp, onKeyPress
from api.utils.ResourcePath import resource_path
from api.utils.Console import *

from api.GameObject import GameObject
from api.UI.Choice import Choice
from api.UI.GameUI import UIElement
from api.UI.ProgressBar import ProgressBar
from api.entity.Boss import Boss
from api.entity.Enemy import Enemy
from api.entity.Entity import Entity
from api.environment.Trap import Trap

### Game modules ####
from game.game_actions.triggers import *
from game.game_actions.ui import menu_in_game, main_menu, toggle_audio

class Omicronde:
    def __init__(self):
        #%%############### GLOBAL VARIABLES ###################
        #######################################################
        self.RENDER_WIDTH, self.RENDER_HEIGHT = 640, 360
        self.WIDTH, self.HEIGHT = 1280, 720
        self.NAME = "Robot Recovery"
        self.FPS = 60

        #%%############### Initializing the game ##############
        #######################################################
        self.assets_path = resource_path("assets")
        self.font_G = "**/" + join(self.assets_path, "Fonts\\Gm6x11.ttf")
        Fonts.DEFAULT_FONT = self.font_G
        Debug.debug_font = self.font_G
        self.game = Game((self.WIDTH, self.HEIGHT), (self.RENDER_WIDTH, self.RENDER_HEIGHT), self.NAME, pg.RESIZABLE | pg.SCALED, self.FPS)
        self.scene = self.game.scene

        ### DEBUG MODE ###
        #self.game.enable_debug() # Enables debug mode by default
        self.game.toggle_fullscreen(os.environ.get("NO_FULLSCREEN") != "1") # Toggles fullscreen

        #%%################ LOADING ASSETS ####################
        #######################################################

        # Init the resource manager
        self.glob = Resource(ResourceType.GLOBAL, self.assets_path)

        self.game.set_icon(resource_path(join("assets", "Images", "icon.png")))

        # Load animations
        run_anim = Animation(Texture("Images\\Player\\NinjaFrog\\run_scaled.png", self.glob), 12, 70)
        run_fast_anim = Animation(Texture("Images\\Player\\NinjaFrog\\run_scaled.png", self.glob), 12, 50)
        idle_anim = Animation(Texture("Images\\Player\\NinjaFrog\\idle_scaled.png", self.glob), 11, 100)
        jump_anim = Texture("Images\\Player\\NinjaFrog\\jump_scaled.png", self.glob)
        fall_anim = Texture("Images\\Player\\NinjaFrog\\fall_scaled.png", self.glob)
        hit_anim = Animation(Texture("Images\\Player\\NinjaFrog\\hit_scaled.png", self.glob), 7, 50)

        # Textures
        icon_texture = Texture("Images\\icon.png", self.glob)
        grass_texture = Texture("Images\\Terrain\\grass.png", self.glob)
        checkpoint_texture = Texture("Images\\Terrain\\beach_sand.png", self.glob)
        sign_texture = Texture("Images\\sign.png", self.glob)
        player_face_texture = Texture("Images\\Player\\NinjaFrog\\jump.png", self.glob)

        # Loads background
        space_background = Texture("Images\\Background\\Background_space.png", self.glob)

        # Loads parallax layers
        t_p1 = Texture("Images\\Background\\Parallax\\Forest\\0.9x parallax-demon-woods-close-trees.png", self.glob)
        t_p2 = Texture("Images\\Background\\Parallax\\Forest\\0.70x parallax-demon-woods-mid-trees.png", self.glob)
        t_p3 = Texture("Images\\Background\\Parallax\\Forest\\0.5x parallax-demon-woods-far-trees.png", self.glob)
        t_p4 = Texture("Images\\Background\\Parallax\\Forest\\0.25x parallax-demon-woods-bg.png", self.glob)

        # Loads music
        self.audio_manager = self.game.audio_manager

        self.audio_manager.load_music("titleScreen", join(self.assets_path, "Music\\The_Legend_of_Zelda_Ocarina_of_Time_OST_N64_Title_Screen_Track_1.mp3"))
        self.audio_manager.load_music("inGame", join(self.assets_path, "Music\\Original_Super_Mario_Bros_Soundtrack_Full.mp3"))
        self.audio_manager.load_music("pause", join(self.assets_path, "Music\\Alicia.mp3"))

        # Loads SFX
        self.audio_manager.load_sfx("jump", join(self.assets_path, "SFX\\frog-sound.mp3"))
        #self.audio_manager.load_sfx("hit_ground", join(self.assets_path, "SFX\\Casserole.mp3"))
        self.audio_manager.load_sfx("death", join(self.assets_path, "SFX\\Mario died _(.mp3"))
        self.audio_manager.load_sfx("death2", join(self.assets_path, "SFX\\Mario died _(.mp3"))
        self.audio_manager.load_sfx("fire", join(self.assets_path, "SFX\\piou1.mp3"))


        #REMOVEME : remove audio

        self.audio_manager.toggle_audio()

        #%%################ PLAYER INITIALIZATION ####################
        ##############################################################
        self.player = Player((310, 410), (48, 48))
        #TODO: Review Ennemy Turret
        self.entity = Enemy((650, 350), (48, 48), mode="idle", range=300)

        self.boss = Boss((700, 350), (64, 64))

        boss_texture = Animation(Texture("Images\\Player\\MaskDude\\idle.png", self.glob), 11, 100)
        self.boss.set_animation(boss_texture)
        self.boss.set_gravity(0.5)



        self.player.set_gravity(0.5)
        self.player.set_sfx_list(sfx_list={"jump": "jump", "death": "death", "death2": "death2", "fire": "fire"})
        self.player.bind_animations({"run": run_anim, "run_fast": run_fast_anim, "idle": idle_anim, "jump": jump_anim, "fall": fall_anim, "hit": hit_anim})

        self.player_ui_health = ProgressBar((30, 10), (100, 10), (100, 100, 100), "green", 100)
        self.heart = Texture("Images\\heart.png", self.glob)
        self.player_ui_heart = UIElement((8, 8), (16, 16))
        self.player_ui_heart.set_texture(self.heart, True)
        self.scene.UI.add("player_health", self.player_ui_health)
        self.scene.UI.add("player_heart", self.player_ui_heart)
        self.scene.UI.show("player_health")
        self.scene.UI.show("player_heart")

        self.entity.set_gravity(1)
        self.entity.set_animation(Animation(Texture("Images\\Player\\little robot\\idle_robot_scaled.png", self.glob), 11, 50))

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

        for coll in self.collections:
            coll.set_color((200, 200, 200))
            coll.set_texture(grass_texture)

        #### TRIGGERS ####
        # (see game/game_actions/triggers.py for the functions (callbacks) called by the triggers)
        # A trigger is an invisible area that executes a callback function when the targeted object enter it.

        ### NOTE ### to pass a callback, use "lambda" or "functools.partial". See the Trigger module for more info. Syntax is as follows:
        # lambda obj: call_back_function(params, ...)

        ### Predefined triggers
        ### Creates a killBox that kills the player when falling too much (y > HEIGHT)
        create_killBox(self.collections, 50, self.HEIGHT)

        ### Custom triggers
        self.collections += [Trigger((700, 400), (100, 100), ["player"],[lambda obj: print_info("Trigger that can be actived each time triggered!")])]
        self.collections += [Trigger((832, 550), (32, 32), ["player"],[lambda obj: summon_stairs1(self.scene, player_face_texture, sign_texture, sign_texture, self.HEIGHT, grass_texture, checkpoint_texture)],once=True)]

        trap = Trap((950, 550), (32, 32), "player", 10, cooldown=3000)
        trap.bind_textures({
            "idle": Texture("Images\\Background\\Tiles\\ggg.png", self.glob),
            "active": Texture("Images\\Background\\Tiles\\blue.png", self.glob)
        })
        self.scene.add(trap, "#object")

        #%%################ CAMERA SETUP ####################
        #####################################################

        ### Offsets the camera
        # To center the player. Thus, the camera follows the player when moving, while keeping it centered on the screen.
        self.scene.camera.set_offset((self.RENDER_WIDTH // 2 - self.player.size.x, self.RENDER_HEIGHT // 2 - self.player.size.y))
        self.scene.camera.set_limits((100, -self.RENDER_HEIGHT - 100), (self.RENDER_WIDTH * 20, self.RENDER_HEIGHT - 100))

        #%%################ BACKGROUND SETUP ###################
        ########################################################

        ### Wonderful parallax background
        p_bg = ParallaxBackground((self.RENDER_WIDTH, self.RENDER_HEIGHT), [
            ParallaxLayer(pg.Vector2(0.9, 0.45), t_p1),
            ParallaxLayer(pg.Vector2(0.7, 0.35), t_p2),
            ParallaxLayer(pg.Vector2(0.5, 0.25), t_p3),
        ], (75, 105, 52))
        self.scene.set_background(p_bg)

        b_bg = Background(space_background, False, (self.RENDER_WIDTH, self.RENDER_HEIGHT))

        #%%################# MAIN MENU SCENE ########################
        ############################################################

        self.menu_scene = Scene((self.RENDER_WIDTH, self.RENDER_HEIGHT))
        self.menu_scene.set_background(b_bg)
        self.menu_scene.camera.set_offset((self.RENDER_WIDTH // 2 - self.player.size.x, self.RENDER_HEIGHT // 2 - self.player.size.y))

        self.scene.add(self.player, "#player")
        self.scene.add(self.entity, "#enemies")
        self.scene.add(self.boss, "#enemies")

        self.game.scene = self.menu_scene

        #%%################ UI setup ###################
        ################################################

        dialog = Dialog(self.font_G)

        dialog.setup({
            "characters": [
                {"name": "Galaxaris", "texture": icon_texture},
                {"name": "You", "texture": player_face_texture}
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
        info_box.set_texture(sign_texture)
        self.collections += [info_box]


        dialog2 = Dialog(self.font_G)
        dialog2.add_character("Sign", sign_texture)
        dialog2.add_message("Sign", ">>> This is the Way >>>")

        self.scene.UI.add("sign", dialog2)
        info_box2 = TriggerInteract((694, 568), (32, 32), ["player"], [lambda obj: self.scene.UI.show("sign")])
        info_box2.set_texture(sign_texture)
        self.collections+= [info_box2]




        ### MENU
        menu = menu_in_game(self.scene, self.menu_scene, "menu", self.RENDER_WIDTH, self.RENDER_HEIGHT, self.player, self.game)
        self.scene.UI.add("menu", menu)

        menu2 = main_menu(self.menu_scene, self.scene, "main_menu", self.RENDER_WIDTH, self.RENDER_HEIGHT, self.game)
        self.menu_scene.UI.add("main_menu", menu2)
        self.menu_scene.UI.show("main_menu")
        self.audio_manager.play_music("titleScreen")

        #%%################# MUSIC SETUP ########################
        #########################################################
        """
        For now, no music or SFX for peace of mind of our dear Raphix. Can be changed with the button mute/unmute in the menu
        """
        #toggle_audio(self.audio_manager)  # Mute the music by default, can be changed with the button in the menu
        #self.audio_manager.play_music("inGame")  # Play the main theme in loop


        #%%################# EVENT MANAGER SETUP ########################
        #################################################################
        self.game_event_manager = self.game.event_manager
        self.game_event_manager.Instances.bindInstancesDict({
            "game": self.game,
            "scene": self.scene,
            "player": self.player,
            "entity": self.entity,
            "menu_scene": self.menu_scene,
            "audio_manager": self.audio_manager
        })

        #self.game_event_manager.registerDefaultEventCollection() #Registers default events (see api/events/DefaultEventCollection.py)
        
        #Example of registering a custom event:
        self.game_event_manager.registerEvent("custom_event", [lambda em: print_info("Custom event triggered!"), 
            lambda em: self.audio_manager.play_music("pause"), lambda em: self.scene.UI.show("test")]) #Registers a custom event with multiple callbacks (see api/events/EventManager.py for more info on registering events)

        #print_info(f"Registered events:\n\n {self.game_event_manager.getRegisteredEvents()}")

        #Example of triggering an event:
        #self.game_event_manager.triggerEvent("custom_event")
        #self.game_event_manager.triggerEvent("test_error_instance")

        #%%################# INPUT MANAGER SETUP ########################
        #################################################################
        

    #%%################ GAME LOOP ########################
    ######################################################

    def loop(self):
        self.scene.default_surface.fill((0,0,0,0))
        self.scene.set_layer(1, "#object")
        self.scene.set_layer(2, "#player")
        self.scene.set_layer(3, "#enemies")
        self.scene.set_layer(4, "_trajectory")
        self.scene.set_layer(5, "#projectile")

        self.player_ui_health.set_progress(self.player.health)
        if self.player.health > 60:
            self.player_ui_health.set_color("green")
        elif self.player.health > 30:
            self.player_ui_health.set_color("yellow")
        else:
            self.player_ui_health.set_color("red")

        self.debug_info()

        for colls in self.collections:
            self.scene.add(colls, "#object")

        #self.scene.add(self.player, "#player")

        self.scene.camera.focus(self.player)

        inputs = pg.key.get_pressed()

        if inputs[pg.K_o]:
            self.player.respawn()

        if inputs[pg.K_p]:
            self.game.scene = self.menu_scene

        def change_ennemy(event):
            if event.key == pg.K_i:
                self.entity.mode = "patrol" if self.entity.mode == "chase" else "chase"

        self.game.bind(pg.KEYDOWN, change_ennemy)


        if inputs[pg.K_m]:
            self.game.scene = self.scene

        if inputs[pg.K_n]:
            self.game_event_manager.triggerEvent("player_jump")
            self.game_event_manager.triggerEvent("custom_event")

        if inputs[pg.K_b]:
            get_held_inputs()

        if not "menu" in self.scene.UI.enabled_elements:
            if onKeyUp("pause"):
                self.scene.UI.show("menu")
                self.audio_manager.play_music("pause")

        elif "menu" in self.scene.UI.enabled_elements:
            if onKeyUp("pause"):
                self.scene.UI.hide("menu")
                self.audio_manager.play_music("inGame") #Resume the main theme when closing the menu

    def debug_info(self):
        Debug.register_debug_entity(self.game, self.player)
        Debug.register_debug_entity(self.game, self.entity)

    def launch(self):
        self.game.run(self.loop)

#%%############# ON START #############################
#######################################################
print_info("Welcome to the Omicronde Game - [bold]Galaxaris Demo[/bold] !\nIf you don't see the game window, it might be behind your current window, please check!\nAnd... [green]HAVE FUN![/green]")

#%%################ MAIN ##############################
#######################################################
if __name__ == "__main__":
    try:
        #%%############## CLOSE SPLASH SCREEN #################
        #######################################################
        in_an_exe = True
        try:
            import pyi_splash

            time.sleep(5)
            pyi_splash.close()
        except ImportError:
            # we are not in an exe file
            in_an_exe = False

        #%%############## LAUNCH THE GAME #####################
        #######################################################
        app = Omicronde()
        app.launch()

    except Exception:
        #%%############## CLOSE PG WINDOW #####################
        #######################################################
        try:
            import pygame as pg

            pg.quit()

        except ImportError:
            pass

        #%%############## CLOSE CMD ###########################
        #######################################################
        from api.utils.Console import *

        print_error("[bold red]=== FATAL ERROR ===[/bold red]\nAn unexpected error occurred while running the game. Please check the error message above and try to fix it. If you need help, don't hesitate to contact us with the error message and the steps to reproduce it. We will be happy to help you!")
        import traceback

        error = traceback.format_exc()
        print_error(f"[bold red]{error}[/bold red]", width=100)

        if in_an_exe:
            print_warning("CMD is self closing in 10 seconds...")
            print("")
            print_countdown(10)
            print("")

        print_info("Goodbye !")