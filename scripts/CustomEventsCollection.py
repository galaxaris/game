"""
Grab your new events from the scripts you have defined in `scripts/` (particularly `scripts/event.py`)
"""

from game.setup.imports_collection import *

def get_custom_events(manager):
    """

    Generates the custom event collection for the EventManager (same structure as `DefaultEventCollection`)
    associating event names with their corresponding callback functions.

    PLEASE place the main associated event first, then the additional ones, for clarity.

    ==> Exemple: "player_jump": 1. Jump action, 2. SFX, Particles, etc.

    Structure:

    {
        "event_name": ([lambda event: event.Instances.some_instance.some_method(), ...], [condition1, condition2, ...]) (set to None if no conds)
        ...
    }

    :param manager: The EventManager instance to which the events will be registered.

    :return: A dictionary containing the custom events and their associated callback functions, with optional conditions (set to None if no conds)
    """

    return {
        #manager = the EventManager instance
        #e = the event (ex: mouse click) passed by triggerEvent
        
        #Example of a custom event with multiple callbacks and no conditions (set to None if no conditions)
        "custom_event": ([lambda e=None: print_info("Custom event triggered!"), 
            lambda e=None: manager.Instances.audio_manager.play_music("pause"), lambda e=None: manager.Instances.scene.UI.show("sign")], None), 
        #... add other custom events as needed
        "toggle_audio": ([lambda e=None: toggle_audio(manager.Instances.audio_manager, manager.Instances.scene.UI.get("menu"))], None),
    }