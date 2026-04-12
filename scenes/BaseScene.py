from api.Game import Game
from api.UI.Dialog import Dialog
from api.assets.Animation import Animation
from api.engine.Scene import Scene
from api.entity.Player import Player
from api.environment.Background import Background
from api.environment.Solid import Solid
from api.environment.Trigger import TriggerInteract
from api.utils import Debug
from api.utils.Console import print_info
from game.scripts.player_manager import init_player
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
            {"name": "Ordinateur", "texture": game.RESSOURCES["textures"]["ai_icon"]},
            {"name": "Toi", "texture": game.RESSOURCES["textures"]["player_base"]},
            {"name": "Galaxaris", "texture": game.RESSOURCES["textures"]["icon"]}
        ],
        "messages": [
            # --- RÉVEIL ET CONTEXTE ---
            ("Galaxaris", "Ce jeu est une démonstration technique et est encore en développement. Certaines mécaniques et éléments narratifs ont été enlevés."),
            ("Galaxaris", "L'histoire et les dialogues présentés ici sont des ébauches et peuvent être sujets à des changements importants dans la version finale du jeu.",
             [
                 ("Je comprends, continuez.", "continue_dialogue", lambda e: game.event_manager.triggerEvent("back_to_ship") )
             ]),
            ("Mélanie Cavill",
             "Les capteurs de stase indiquent un réveil complet. Respire calmement, tes fonctions vitales se stabilisent."),
            ("Toi", "Capitaine Cavill ? Je me sens... étrangement léger. Combien de temps s'est écoulé ?"),

            ("Mélanie Cavill",
             "Trop longtemps. Pendant ton sommeil, l'humanité a fini par abandonner la Terre. L'entreprise 'Cyclope Industries' a détruit la planète à cause de l'exploitation industrielle."),

            # Transition visuelle : Vue satellite de la désolation
            ("Mélanie Cavill", "Regarde l'écran principal. Ce n'est plus la planète que tu as connue.",
             [
                 ("Regarder", "view_desolated_earth", lambda e: game.event_manager.triggerEvent("view_desolated_earth"))
             ]),

            ("Mélanie Cavill",
             "Les robots d'extraction qu'ils ont créés tournent en boucle. Sans personne pour les guider, ils continuent de puiser des ressources dans un sol déjà épuisé, aggravant la pollution chaque jour.", "view_desolated_earth"),

            # --- ENJEU ÉCOLOGIQUE ---
            ("Mélanie Cavill",
             "Le Conseil International t'a choisi pour une mission unique : inverser la tendance. Nous ne sommes pas ici pour exploiter, mais pour restaurer."),

            ("Mélanie Cavill", "Acceptes-tu cette responsabilité ? Devenir le lien entre la technologie et la vie ?", [
                ("Je suis prêt. Rendons cette planète habitable.", "accept_mission",
                 lambda e: game.event_manager.triggerEvent("back_to_ship")),
                ("Toute seule ?", "doubt_mission",
                 lambda e: game.event_manager.triggerEvent("back_to_ship"))
            ], "choice_commitment"),

            # Branche : Le doute
            ("Mélanie Cavill",
             "Tu n'es pas seule. Je serai tes yeux et tes oreilles. Et surtout, nous avons la science pour nous.",
             "doubt_mission"),
            ("GOTO", "gameplay_details"),

            # Branche : L'acceptation
            ("Mélanie Cavill",
             "C'est l'esprit dont nous avons besoin. La détermination est le premier pas vers la guérison de l'écosystème.",
             "accept_mission"),
            ("GOTO", "gameplay_details"),

            # --- EXPLICATIONS TECHNIQUES (GAMEPLAY) ---
            ("Mélanie Cavill",
             "Voici notre stratégie : nous allons utiliser l'antenne orbitale pour pirater les unités de Cyclope Industries au sol.",
             "gameplay_details"),

            ("Mélanie Cavill",
             "Certains modèles sont trop corrompus pour être sauvés. Il faudra les démanteler. Mais rien ne sera perdu."),

            ("Mélanie Cavill",
             "Nous recyclerons leurs composants pour construire des centres de traitement : purificateurs d'eau, stabilisateurs de sols et nurseries pour la flore locale."),

            # Déclenchement : Activation de la console de contrôle
            ("Mélanie Cavill", "Le signal de l'antenne vient de se stabiliser. Nous avons une fenêtre d'accès."),

            ("Ordinateur",
             "Interface de liaison activée. Terminal de contrôle à distance opérationnel. Liaison avec l'unité 'Alpha-01' en attente."),

            ("Mélanie Cavill",
             "C'est le moment. Prends les commandes de ce premier robot. Ta mission commence par un geste simple : ramasser les débris et préparer le terrain pour le futur."),

            ("Mélanie Cavill", "L'ordinateur de bord n'attend plus que tes directives. Fais-en bon usage."),

            ("Toi", "Pour la Terre !!!", [
                ("Allons-y !", "start_gameplay", lambda e: enable_player_control(True,scene))
            ]),

            # --- FIN DU DIALOGUE ---
            ("Mélanie Cavill", "Bonne chance, Capitaine. Nous avons confiance en toi.", "start_gameplay"),
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
            ("Mélanie Cavill", "Veux-tu vraiement quitter la partie ?", [
                ("Oui", "quit_game", lambda e: game.event_manager.triggerEvent("QUIT")),
                ("Non", "continue_game", lambda e: None)
            ]),
            ("Mélanie Cavill", "Très bien, dirige toi vers l'ordinateur de bord pour continuer ta mission.", "continue_game"),
            ("STOP")
        ]
    })
    scene.UI.add("quit_dialog",dialog)
    scene.UI.show("quit_dialog")


def launch_computer(game):
    pass


def start(game: Game):
    global scene
    global player
    scene = Scene(game.render_size)
    scene.name = "BaseScene"
    bg = Background(game.RESSOURCES["textures"]["ship"], False, scene.size)

    ground = Solid((0,270), (640,360))
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

    """player = init_player(game)
    scene.add(player, "#player")"""

def update(game: Game):
    Debug.register_debug_entity(game, player)


