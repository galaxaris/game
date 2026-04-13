"""
Personnalized functions for creating predefined UIs
Can be useful to predefine a certain AD for the game (colors, fonts, box styles, dialog styles, buttons, etc.)
"""
from api.Game import Game
from api.UI.Button import Button
from api.UI.Modal import Modal
from api.UI.ProgressBar import ProgressBar
from api.UI.Text import Text
from api.assets.AudioManager import AudioManager
from api.engine.Scene import Scene
from api.utils import Fonts
from api.utils.InputManager import *

#Global variables
COLOR_SET_CLASSIC = ((0, 0, 0), (255, 255, 255), (188, 188, 188), (163, 163, 163))
COLOR_SET_COMMON = ((0, 0, 0), (3, 161, 45), (90, 204, 121), (9, 117, 42))
COLOR_SET_SETTINGS = ((0, 0, 0), (0, 104, 204), (105, 162, 214), (0, 62, 117))
COLOR_SET_DANGER = ((0, 0, 0), (181, 0, 0), (237, 100, 100), (94, 4, 4))
COLOR_SET_DEBUG = ((0, 0, 0), (161, 2, 131), (214, 107, 193), (94, 6, 78))

#%%### UI CREATION FUNCTIONS ####
#################################

### TODO: implement later in the JSON BDD
def menu_button(pos: int, size: int, text: str, callback: callable, menu: Modal, FONT_FR: str, column_index: int = 0, color_set: tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]] = COLOR_SET_CLASSIC):
    """
    Game utility function to create a button with predefined style and add it to a menu.

    :param pos: Button position relative to the menu.
    :param size: Button size.
    :param text: Button text.
    :param callback: Button callback function.
    :param menu: Menu to which the button will be added.
    :param column_index: Menu column index for button placement (default: 0).
    :param color_set: Tuple of four colors for the button (text, background, hover, focus) (default: black, white, gray, darker gray).
    """
    button = Button(pos, size, text, color_set, FONT_FR)
    button.set_callback(callback)
    menu.add_element(button, column_index)


def getCurrentLevelMusic(game: Game):
    current_level_music = None
    if game.scene.name == "BaseScene":
        current_level_music = "titleScreen"
    elif game.scene.name == "Level1Scene":
        current_level_music = "level1"
    elif game.scene.name == "Level2Scene":
        current_level_music = "level2"
    elif game.scene.name == "Level3Scene":
        current_level_music = "level3"
    elif game.scene.name == "BossLevelScene":
        current_level_music = "bossLevel"

    return current_level_music

def menu_in_game(game: Game, menu_name: str):

    if(game.scene.name == "MainMenuScene"):
        return None

    #Global variables:
    FONT_FR = Fonts.DEFAULT_FONT
    audio_manager = game.audio_manager

    scene = game.scene
    screen_w = scene.size.x
    screen_h = scene.size.y

    ## Menu panel
    menu = Modal((50, 50), (screen_w-100, screen_h-100),  (0, 0, 0, 200))
    text = Text((0,0), 20, "Game Menu", FONT_FR, (3, 161, 45))
    menu.add_element(text, x=0)


    ## Get current level name to play it's corresponding music when resuming the game
    current_level_music = getCurrentLevelMusic(game)

    ## Buttons
    menu_button((0,50), (100, 40), "Resume", lambda e: (scene.UI.hide(menu_name), audio_manager.play_music(current_level_music)), menu, FONT_FR, color_set=COLOR_SET_COMMON)
    menu_button((0,100), (100, 40), "Restart", lambda e: (game.event_manager.triggerEvent("restart_level"), scene.UI.hide(menu_name), audio_manager.play_music(current_level_music)), menu, FONT_FR, color_set=COLOR_SET_COMMON)
    menu_button((0,150), (100, 40), "Title Screen", lambda e: game.event_manager.triggerEvent("goto_title_screen"), menu, FONT_FR, color_set=COLOR_SET_DANGER)
    menu_button((screen_w-220,50), (100, 40), "Debug", lambda e: game.event_manager.triggerEvent("enable_debug"), menu, FONT_FR, column_index=1, color_set=COLOR_SET_DEBUG)
    menu_button((screen_w-220,100), (100, 40), "Mute", lambda e: toggle_audio(audio_manager, menu), menu, FONT_FR, column_index=1, color_set=COLOR_SET_SETTINGS)
    #menu_button((screen_w-220,150), (100, 40), "Quit", lambda e: game.event_manager.triggerEvent("QUIT"), menu, FONT_FR, color_set=COLOR_SET_DANGER,  column_index=1)

    return menu
    ## Add menu to scene UI
    #scene.UI.add(menu, menu_name)

def main_menu( game: Game, scene):

    #Global variables:
    FONT_FR = Fonts.DEFAULT_FONT

    screen_w = scene.size.x
    screen_h = scene.size.y

    ## Menu panel
    menu = Modal(((screen_w-screen_w*0.33)/2, (screen_h-screen_h*0.28)/2), (screen_w*0.33, screen_h*0.28),  (0, 0, 0, 200))
    text = Text((0,0), 32, "Robot Recovery", FONT_FR, (160, 161, 10))
    menu.add_element(text, x=0)

    ## Buttons
    menu_button((45,45), (100, 40), "Play", lambda e: game.event_manager.triggerEvent("start_game"), menu, FONT_FR, color_set=COLOR_SET_COMMON)

    return menu
    ## Add menu to scene UI
    #scene.UI.add(menu, menu_name)

#%%############### UI CALLBACKS ##########################
##########################################################
def start_game_scene(game_scene: Scene, game: Game):
    game.scene = game_scene

def goto_title_scene(menu_scene: Scene, game: Game):
    game.scene = menu_scene

def toggle_audio(audio_manager: AudioManager = None, menu = None):
    if not audio_manager:
        return
    #Gets the button in menu.elements to change its text accordingly
    mute_button = None
    if menu:
        for element in menu.elements:
            if isinstance(element, Button) and (element.text == "Mute" or element.text == "Unmute"):
                mute_button = element
                break
            else:
                ...
                #print_warning("Mute button not found in menu elements.")
    else:
        ...
        #print_warning("Menu not found.")

    if audio_manager.is_muted:
        audio_manager.toggle_audio() #Unmute
        if mute_button:
            mute_button.set_text("Mute")
    else:
        audio_manager.toggle_audio() #Mute
        if mute_button:
            mute_button.set_text("Unmute")


def toggle_menu_inGame(game: Game):
    if game.scene and game.scene.name == "MainMenuScene":
        return None
    
    current_level_music = getCurrentLevelMusic(game)

    if not "menu" in game.scene.UI.enabled_elements:
        if onKeyUp("pause"):
            game.scene.UI.show("menu")
            game.audio_manager.play_music("pause")

    elif "menu" in game.scene.UI.enabled_elements:
        if onKeyUp("pause"):
            game.scene.UI.hide("menu")
            game.audio_manager.play_music(current_level_music) #Resume the main theme when closing the menu

def update_player_health_UI(player_ui_health: ProgressBar, player_health: int):
    player_ui_health.set_progress(player_health)
    if player_health > 60:
        player_ui_health.set_color("green")
    elif player_health > 30:
        player_ui_health.set_color("yellow")
    else:
        player_ui_health.set_color("red")