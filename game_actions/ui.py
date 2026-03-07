"""
Personnalized functions for creating predefined UIs
Can be useful to predefine a certain AD for the game (colors, fonts, box styles, dialog styles, buttons, etc.)
"""

#Libs
import pygame as pg
from os.path import join

#API
from api.UI.Button import Button
from api.UI.Dialog import Dialog
from api.UI.Modal import Modal
from api.UI.Text import Text
from api.UI.TextBox import TextBox
from api.engine.Scene import Scene
from api.entity.Player import Player
from api.Game import Game

from api.utils import GlobalVariables

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

def menu_in_game(scene: Scene, menu_name: str, screen_w: int, screen_h: int, player: Player, game: Game):

    #Global variables:
    FONT_FR = GlobalVariables.get_variable("default_font")
    audio_manager = GlobalVariables.get_variable("audio_manager")

    ## Menu panel
    menu = Modal((50, 50), (screen_w-100, screen_h-100), (0, 0, 0))
    text = Text((0,0), 20, "Game Menu", FONT_FR, (3, 161, 45))
    menu.add_element(text, x=0)

    ## Buttons
    menu_button((0,50), (100, 40), "Resume", lambda e: (scene.UI.hide(menu_name), audio_manager.play_music("inGame")), menu, FONT_FR, color_set=COLOR_SET_COMMON)
    menu_button((0,100), (100, 40), "Restart", lambda e: (player.kill(), scene.UI.hide(menu_name), audio_manager.play_music("inGame")), menu, FONT_FR, color_set=COLOR_SET_COMMON)
    menu_button((0,150), (100, 40), "Quit", lambda e: game.stop(), menu, FONT_FR, color_set=COLOR_SET_DANGER)
    menu_button((screen_w-220,50), (100, 40), "Debug", lambda e: game.enable_debug(), menu, FONT_FR, column_index=1, color_set=COLOR_SET_DEBUG)
    menu_button((screen_w-220,100), (100, 40), "Mute", lambda e: toggle_mute_unmute(), menu, FONT_FR, column_index=1, color_set=COLOR_SET_SETTINGS)

    GlobalVariables.set_variable("current_menu", menu) #To be able to access the menu in the callback of the mute button
    return menu
    ## Add menu to scene UI
    #scene.UI.add(menu, menu_name)
    


#%%############### UI CALLBACKS ##########################
##########################################################
def toggle_mute_unmute():
    audio_manager = GlobalVariables.get_variable("audio_manager")
    #Gets the button in menu.elements to change its text accordingly
    menu = GlobalVariables.get_variable("current_menu")
    mute_button = None
    for element in menu.elements:
        if isinstance(element, Button) and (element.text == "Mute" or element.text == "Unmute"):
            mute_button = element
            break

    if audio_manager.music_volume > 0: #Condition suffisante car sfx et musique sont mis à 0 ou 1 en mm temps (pour le moment)
        audio_manager.set_music_volume(0)
        audio_manager.set_sfx_volume(0)
        if mute_button:
            mute_button.set_text("Mute")
    else:
        audio_manager.set_music_volume(1)
        audio_manager.set_sfx_volume(1)
        if mute_button:
            mute_button.set_text("Unmute")