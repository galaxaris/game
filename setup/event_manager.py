"""
This module allows you manage and add events to the EventManager. 

Based on `api.events.EventManager` and `api.events.DefaultEventCollection`
"""
from game.setup.imports_collection import *
from game.scripts.CustomEventsCollection import get_custom_events

def init_event_manager(game_instance):
    """
    Initializes the EventManager by registering the custom events.

    :param game_instance: The EventManager instance to be initialized.
    """

    game_instance.game_event_manager.Instances.bindInstancesDict({
            "game": game_instance.game,
            "scene": game_instance.scene,
            "player": game_instance.player,
            "entity": game_instance.entity,
            "menu_scene": game_instance.menu_scene,
            "audio_manager": game_instance.audio_manager,
            #... add as many other instances as needed
    })

    game_instance.game_event_manager.registerEventDict(get_custom_events(game_instance.game_event_manager)) 