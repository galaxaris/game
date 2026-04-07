"""
Personnalized functions for creating predefined UIs
Can be useful to predefine a certain AD for the game (colors, fonts, box styles, dialog styles, buttons, etc.)
"""

from game.setup.imports_collection import *


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

def menu_in_game(scene: Scene, menu_scene: Scene, menu_name: str, screen_w: int, screen_h: int, player: Player, game: Game):

    #Global variables:
    FONT_FR = Fonts.DEFAULT_FONT
    audio_manager = game.audio_manager

    ## Menu panel
    menu = Modal((50, 50), (screen_w-100, screen_h-100),  (0, 0, 0, 200))
    text = Text((0,0), 20, "Game Menu", FONT_FR, (3, 161, 45))
    menu.add_element(text, x=0)

    ## Buttons
    menu_button((0,50), (100, 40), "Resume", lambda e: (scene.UI.hide(menu_name), audio_manager.play_music("inGame")), menu, FONT_FR, color_set=COLOR_SET_COMMON)
    menu_button((0,100), (100, 40), "Restart", lambda e: (player.respawn(), scene.UI.hide(menu_name), audio_manager.play_music("inGame")), menu, FONT_FR, color_set=COLOR_SET_COMMON)
    menu_button((0,150), (100, 40), "Title Screen", lambda e: goto_title_scene(menu_scene, game), menu, FONT_FR, color_set=COLOR_SET_DANGER)
    menu_button((screen_w-220,50), (100, 40), "Debug", lambda e: game.enable_debug(), menu, FONT_FR, column_index=1, color_set=COLOR_SET_DEBUG)
    menu_button((screen_w-220,100), (100, 40), "Mute", lambda e: toggle_audio(audio_manager, menu), menu, FONT_FR, column_index=1, color_set=COLOR_SET_SETTINGS)
    menu_button((screen_w-220,150), (100, 40), "Quit", lambda e: game.stop(), menu, FONT_FR, color_set=COLOR_SET_DANGER,  column_index=1)

    return menu
    ## Add menu to scene UI
    #scene.UI.add(menu, menu_name)

def main_menu(menu_scene: Scene, game_scene: Scene, menu_name: str, screen_w: int, screen_h: int, game: Game):

    #Global variables:
    FONT_FR = Fonts.DEFAULT_FONT

    ## Menu panel
    menu = Modal(((screen_w-screen_w*0.33)/2, (screen_h-screen_h*0.28)/2), (screen_w*0.33, screen_h*0.28),  (0, 0, 0, 200))
    text = Text((0,0), 32, "Robot Recovery", FONT_FR, (160, 161, 10))
    menu.add_element(text, x=0)

    ## Buttons
    menu_button((45,45), (100, 40), "Play", lambda e: start_game_scene(game_scene, game), menu, FONT_FR, color_set=COLOR_SET_COMMON)

    return menu
    ## Add menu to scene UI
    #scene.UI.add(menu, menu_name)

#%%############### UI CALLBACKS ##########################
##########################################################
def start_game_scene(game_scene: Scene, game: Game):
    audio_manager = game.audio_manager
    audio_manager.play_music("inGame")
    game.scene = game_scene

def goto_title_scene(menu_scene: Scene, game: Game):
    audio_manager = game.audio_manager
    audio_manager.play_music("titleScreen")
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
                print_warning("Mute button not found in menu elements.")
    else:
        ...
        print_warning("Menu not found.")

    if audio_manager.is_muted:
        audio_manager.toggle_audio() #Unmute
        if mute_button:
            mute_button.set_text("Mute")
    else:
        audio_manager.toggle_audio() #Mute
        if mute_button:
            mute_button.set_text("Unmute")


def toggle_menu_inGame(scene: Scene, menu_name: str, menu_scene: Scene, game: Game):
    #TODO: To be implemented once in GameUI or EventManager
    if not "menu" in game.scene.UI.enabled_elements:
        if onKeyUp("pause"):
            game.scene.UI.show("menu")
            game.audio_manager.play_music("pause")

    elif "menu" in game.scene.UI.enabled_elements:
        if onKeyUp("pause"):
            game.scene.UI.hide("menu")
            game.audio_manager.play_music("inGame") #Resume the main theme when closing the menu

def update_player_health_UI(player_ui_health: ProgressBar, player_health: int):
    player_ui_health.set_progress(player_health)
    if player_health > 60:
        player_ui_health.set_color("green")
    elif player_health > 30:
        player_ui_health.set_color("yellow")
    else:
        player_ui_health.set_color("red")