"""
This module allows you to overide default input settings (see `api.utils.InputManager`) and create custom inputs
"""

from api.utils.InputManager import INPUT_ACTIONS
import api.utils.InputManager as InputManager
from game.setup.imports_collection import *

DEFAULT_INPUT_ACTIONS = INPUT_ACTIONS.copy()

## PLEASE NOTE: let empty if you don't want to override default settings
## Do not add actions not present in `DEFAULT_INPUT_ACTIONS`.
PERSON_INPUT_ACTIONS = {

}


"""
##Custom input settings using WASD instead of ZQSD
PERSON_INPUT_ACTIONS = {
    "up": [pg.K_w, pg.K_UP], #If we want to switch from ZQSD to WASD
    "down": [pg.K_s, pg.K_DOWN],
    "left": [pg.K_a, pg.K_LEFT],
    "right": [pg.K_d, pg.K_RIGHT],

    "interact": [pg.K_h], #Overriding: from E to H
}
"""


def load_input_settings(person_input_actions: dict[str, list[int | str]] = None):
    """
    Loads the input settings. The input settings defined in `person_input_actions` override the default input settings, allowing to create custom keymaps.
    """

    if not person_input_actions: #If it is None or empty
        person_input_actions = {}

    input_actions = DEFAULT_INPUT_ACTIONS.copy()

    for action, keys in person_input_actions.items():
        if action in input_actions:
            input_actions[action] = keys
            print_success(f"Input action '{action}' set to keys: {keys}")
        else:
            print_warning(f"Input action '{action}' not found in default input actions.")

    return input_actions

def init_input_manager(resetToDefault: bool = False):
    """
    Initializes the input manager with the defined input settings

    Can be used to reset InputManager to default, using saved var `DEFAULT_INPUT_ACTIONS`

    :param resetToDefault: Reset input settings to default?
    """
    if resetToDefault:
        InputManager.set_input_actions(DEFAULT_INPUT_ACTIONS)
    else:
        InputManager.set_input_actions(load_input_settings(PERSON_INPUT_ACTIONS))