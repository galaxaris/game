from api.Game import Game
from api.UI.Button import Button
from api.UI.Dialog import Dialog
from api.UI.Image import Image
from api.UI.Modal import Modal
from api.engine.Scene import Scene
from api.entity.Player import Player
from api.environment.Background import Background
from api.environment.Solid import Solid
from api.environment.Trigger import TriggerInteract
from api.utils import Debug

from api.utils.Console import print_info
from game.Variables import *


scene: Scene = None
player = None


def enable_player_control(param, scene):
    global player
    scene.global_state["player_control"] = param
    player.visible = param


def play_warning_dialogue(game):
    global scene
    global player
    dialog = Dialog(game.RESSOURCES["fonts"]["default"])

    dialog.setup({
        "characters": [
            {"name": "Mélanie Cavill", "texture": game.RESSOURCES["textures"]["melanie"]},
            {"name": "Computer", "texture": game.RESSOURCES["textures"]["ai_icon"]},
            {"name": "You", "texture": game.RESSOURCES["textures"]["player_base"]},
            {"name": "Galaxaris", "texture": game.RESSOURCES["textures"]["icon"]}
        ],
        "messages": [
            # --- RÉVEIL ET CONTEXTE ---
            ("Galaxaris", "This game is a technical demo and is still in development. Some mechanics and narrative elements have been removed."),
            ("Galaxaris", "The story and dialogues shown here are drafts and may change significantly in the final version of the game.",
             [
                 ("I understand, continue.", "continue_dialogue", lambda e: game.event_manager.triggerEvent("back_to_ship") )
             ]),
            ("Mélanie Cavill",
             "The stasis sensors indicate a complete awakening. Breathe calmly, your vital signs are stabilizing."),
            ("You", "Captain Cavill? I feel... strangely light. How much time has passed?"),

            ("Mélanie Cavill",
             "Too long. During your sleep, humanity ended up abandoning Earth. The company 'Cyclope Industries' destroyed the planet through industrial exploitation."),

            # Transition visuelle : Vue satellite de la désolation
            ("Mélanie Cavill", "Look at the main screen. This is no longer the planet you once knew.",
             [
                 ("Look", "view_desolated_earth", lambda e: game.event_manager.triggerEvent("view_desolated_earth"))
             ]),

            ("Mélanie Cavill",
             "The extraction robots they created are running in loops. With no one to guide them, they keep draining resources from already exhausted ground, worsening pollution every day.", "view_desolated_earth"),

            # --- ENJEU ÉCOLOGIQUE ---
            ("Mélanie Cavill",
             "The International Council chose you for a unique mission: reverse the trend. We are not here to exploit, but to restore."),

            ("Mélanie Cavill", "Do you accept this responsibility? To become the link between technology and life?", [
                ("I'm ready. Let's make this planet livable again.", "accept_mission",
                 lambda e: game.event_manager.triggerEvent("back_to_ship")),
                ("Alone?", "doubt_mission",
                 lambda e: game.event_manager.triggerEvent("back_to_ship"))
            ], "choice_commitment"),

            # Branche : Le doute
            ("Mélanie Cavill",
             "You are not alone. I will be your eyes and ears. And above all, we have science on our side.",
             "doubt_mission"),
            ("GOTO", "gameplay_details"),

            # Branche : L'acceptation
            ("Mélanie Cavill",
             "That's the spirit we need. Determination is the first step toward healing the ecosystem.",
             "accept_mission"),
            ("GOTO", "gameplay_details"),

            # --- EXPLICATIONS TECHNIQUES (GAMEPLAY) ---
            ("Mélanie Cavill",
             "Here is our strategy: we will use the orbital antenna to hack Cyclope Industries units on the ground.",
             "gameplay_details"),

            ("Mélanie Cavill",
             "Some models are too corrupted to be saved. We will have to dismantle them. But nothing will be lost."),

            ("Mélanie Cavill",
             "We will recycle their components to build treatment centers: water purifiers, soil stabilizers, and nurseries for local flora."),

            # Déclenchement : Activation de la console de contrôle
            ("Mélanie Cavill", "The antenna signal has just stabilized. We have an access window."),

            ("Computer",
             "Link interface activated. Remote control terminal operational. Link with unit 'Alpha-01' pending."),

            ("Mélanie Cavill",
             "This is the moment. Take control of this first robot. Your mission starts with a simple action: collect debris and prepare the ground for the future."),

            ("Mélanie Cavill", "The onboard computer is waiting for your directives. Put it to good use."),

            ("You", "For Earth!!!", [
                ("Let's go!", "start_gameplay", lambda e: enable_player_control(True,scene))
            ]),

            # --- FIN DU DIALOGUE ---
            ("Mélanie Cavill", "Good luck, Captain. We believe in you.", "start_gameplay"),
            ("STOP")
        ]
    })

    enable_player_control(False, scene)
    scene.UI.add("start_dialogue", dialog)
    scene.UI.show("start_dialogue")
    story["has_started"] = True


def exit_game_dialogue(game):
    # Exit dialogue when interacting the door trigger
    global scene
    dialog = Dialog(game.RESSOURCES["fonts"]["default"])
    dialog.setup({
        "characters": [
            {"name": "Mélanie Cavill", "texture": game.RESSOURCES["textures"]["melanie"]},
        ],
        "messages": [
            ("Mélanie Cavill", "Do you really want to quit the game?", [
                ("Yes", "quit_game", lambda e: game.event_manager.triggerEvent("QUIT")),
                ("No", "continue_game", lambda e: None)
            ]),
            ("Mélanie Cavill", "Alright, head to the onboard computer to continue your mission.", "continue_game"),
            ("STOP")
        ]
    })
    scene.UI.add("quit_dialog",dialog)
    scene.UI.show("quit_dialog")


def play_boss_end_dialogue(game):
    global scene
    dialog = Dialog(game.RESSOURCES["fonts"]["default"])
    dialog.add_character("Mélanie Cavill", game.RESSOURCES["textures"]["melanie"])
    dialog.add_message(
        "Mélanie Cavill",
        "Great job, we can save the planet now that you defeated the evil robots!"
    )
    dialog.add_message(
        "Mélanie Cavill",
        "We will recycle their components to restore Earth."
    )
    scene.UI.add("boss_end_dialogue", dialog)
    scene.UI.show("boss_end_dialogue")


def launch_computer(game):
    global scene
    menu = Modal((75, 37), (510, 286))



    scene.UI.add("computer_menu", menu)
    scene.UI.show("computer_menu")

    button = Button((420,0), (70, 30), "Fermer", [(255,255,255),(255,0,0),(255,50,50),(255,100,100)], game.RESSOURCES["fonts"]["default"])
    button.set_callback(lambda e: scene.UI.hide("computer_menu"))

    # Définition des boutons avec des palettes de couleurs spécifiques à chaque biome
    # Ordre : [Font, Normal BG, Hover BG, Click BG]

    tutoriel_button = Button((40, 160), (100, 40), "Tutoriel",
                             [(255, 255, 255), (76, 175, 80), (129, 199, 132), (46, 125, 50)],
                             game.RESSOURCES["fonts"]["default"])

    tutoriel_button.set_callback(lambda e: game.event_manager.triggerEvent("goto_tutorial"))

    foret_button = Button((110, 60), (120, 40), "Forêt",
                          [(245, 245, 220), (101, 67, 33), (121, 87, 63), (141, 107, 83)],
                          game.RESSOURCES["fonts"]["default"])
    foret_button.set_callback(lambda e: game.event_manager.triggerEvent("goto_forest"))

    desert_button = Button((240, 120), (110, 40), "Désert",
                           [(255, 253, 231), (218, 165, 32), (255, 215, 0), (184, 134, 11)],
                           game.RESSOURCES["fonts"]["default"])
    desert_button.set_callback(lambda e: game.event_manager.triggerEvent("goto_desert"))

    industrial_button = Button((360, 200), (120, 40), "Industriel",
                               [(236, 240, 241), (127, 140, 141), (189, 195, 199), (52, 73, 94)],
                               game.RESSOURCES["fonts"]["default"])
    industrial_button.set_callback(lambda e: game.event_manager.triggerEvent("goto_industrial"))

    background_image = Image((0, 0), (490, 266), game.RESSOURCES["textures"]["computer_menu"])
    menu.add_element(background_image)
    menu.add_element(button)



    if(story["current_chapter"] >= 1):
        menu.add_element(foret_button, x=0)
    if(story["current_chapter"] >= 2):
        menu.add_element(desert_button, x=1)
    if(story["current_chapter"] >= 3):
        menu.add_element(industrial_button, x=2)
    menu.add_element(tutoriel_button, x=0)



def start(game: Game):
    global scene
    global player
    scene = Scene(game.render_size)
    scene.name = "BaseScene"
    bg = Background(game.RESSOURCES["textures"]["ship"], False, scene.size)

    #Condition, because this music is launched in the main menu, but not the same in the levels
    print_info(f"Current music : {game.audio_manager.current_music()}")

    if game.audio_manager.current_music() != "titleScreen":
        print_info("Replaying title screen music")
        game.audio_manager.play_music("titleScreen")


    ground = Solid((0,270), (640,360))
    left_wall = Solid((-50,0),(50,360))
    right_wall = Solid((640,0),(50,360))
    scene.add(left_wall, "#objects")
    scene.add(right_wall, "#objects")
    scene.add(ground, "#objects")

    player = Player((550, 0), (32, 64))

    player.bind_animations(
        {
            "idle": game.RESSOURCES["animations"]["you_idle"],
            "run": game.RESSOURCES["animations"]["you_run"],
            "run_fast": game.RESSOURCES["animations"]["you_run_fast"]
        }
    )

    scene.add(player, "#player")


    if story["has_started"] == False:
        desolated_earth_bg = Background(game.RESSOURCES["textures"]["desolated_earth"], False, scene.size)
        game.event_manager.registerEvent("view_desolated_earth", [lambda e: scene.set_background(desolated_earth_bg)])
        game.event_manager.registerEvent("back_to_ship", [lambda e: scene.set_background(bg)])
        play_warning_dialogue(game)
    else:
        scene.set_background(bg)

    computer = TriggerInteract((155,183),(130,86), ["player"], [lambda e:launch_computer(game)])
    exit = TriggerInteract((14,157),(68,111), ["player"], [lambda e:exit_game_dialogue(game)])

    scene.add(computer)
    scene.add(exit)

    if getattr(game, "boss_victory_return", False):
        setattr(game, "boss_victory_return", False)
        play_boss_end_dialogue(game)

    """player = init_player(game)
    scene.add(player, "#player")"""

def update(game: Game):
    Debug.register_debug_entity(game, player)


