"""
Resource manager for the game, responsible for loading and managing game assets such as textures, animations, and audio.
"""

from os.path import join

from api.utils.ResourcePath import resource_path
from api.utils.DataManager import load_json
from api.utils.Console import print_error, print_info, print_warning

from game.setup.imports_collection import *


def init_ressource_manager(ressource_manager: Resource, audio_manager: AudioManager, assets_dir: str, assets_store: str = "assets\\assets_store.json") -> dict:
    """
    Initializes the resource manager by loading all necessary game assets and storing them in a structured way.
    """
    assets_path = resource_path(assets_dir)

    # Init the resource manager
    glob = ressource_manager

    ressources = load_resources(glob, audio_manager, load_json(assets_store),  assets_path)

    return ressources


def load_resources(glob: Resource, audio_manager: AudioManager, ressources_dic: dict, assets_path: str) -> dict:
    """
    Loads all game resources and returns them as a dictionary, handling potential loading errors 
    Sounds are loaded using the AudioManager.

    :param assets_dic: A dictionary containing all game assets paths and types.

    :return: A dictionary containing all loaded game resources.
    """

    def _format_error(key, value):
        print_error(f"Invalid format for {key} in assets store. Expected a dictionary of key-path pairs, got {type(value)}. Skipping {key}.")

    def _not_string_error(key, key_type):
        print_error(f"Invalid format for {key} in {key_type} of assets store. Expected a string path, got {type(key)}.")

    def _not_list_error(key, key_type):
        print_error(f"Invalid format for {key} in {key_type} of assets store. Expected a list of 1 string and 2 integers, got {type(key)} of {len(key)} elements.")
        

    #Are stored in this dict: textures, animations & fonts. Sounds are loaded using the AudioManager
    loaded_ressources = {}

    #Process first the ressources_dic to replace the '/' by '\\'
    #So it is easier to write the paths in the json
    for key, value in ressources_dic.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                if isinstance(subvalue, str):
                    ressources_dic[key][subkey] = subvalue.replace('/', '\\')

    #print_info(f"Loading game assets...\nAssets store content:\n{ressources_dic}\n")

    for key, value in ressources_dic.items():
        loaded_ressources[key] = {}
        if key == "textures":
            try: 
                for r_key, r_val in value.items():
                    #Don't need to manage loading errors because it's done in Texture class, displaying a magenta texture in place.
                    if (not isinstance(r_val, str)):
                        _not_string_error(r_key, key)
                    else:
                        #print_info(f"Loading texture '{r_key}' from path '{assets_path}\\Images\\{r_val}'...")
                        loaded_ressources[key][r_key] = Texture(f"{assets_path}\\Images\\{r_val}", glob)
                        

            except AttributeError:
                _format_error(key, value)

        elif key == "animations" :
            try: 
                for r_key, r_val in value.items():
                    #Don't need to manage loading errors because it's done in Texture class, displaying a magenta texture in place.
                    if (not isinstance(r_val, list)):
                        _not_list_error(r_key, key)
                    elif (len(r_val) != 3 or not isinstance(r_val[0], str) or not isinstance(r_val[1], int) or not isinstance(r_val[2], int)):
                        _not_list_error(r_key, key)
                    else:
                        loaded_ressources[key][r_key] = Animation(Texture(f"{assets_path}\\Images\\{r_val[0]}", glob), r_val[1], r_val[2])

            except AttributeError:
                _format_error(key, value)

        elif key == "music":
            try: 
                for r_key, r_val in value.items():
                    #Don't need to manage loading errors because it's done in AudioManager, creating a blank sound
                    if (not isinstance(r_val, str)):
                        _not_string_error(r_key, key)
                    else:
                        audio_manager.load_music(r_key, f"{assets_path}\\Music\\{r_val}")
                        loaded_ressources[key][r_key] = "Loaded"

            except AttributeError:
                _format_error(key, value)

        elif key == "sfx":
            try: 
                for r_key, r_val in value.items():
                    #Don't need to manage loading errors because it's done in AudioManager, creating a blank sound
                    if (not isinstance(r_val, str)):
                        _not_string_error(r_key, key)
                    else:
                        audio_manager.load_sfx(r_key, f"{assets_path}\\SFX\\{r_val}")
                        loaded_ressources[key][r_key] = "Loaded"

            except AttributeError:
                _format_error(key, value)

        elif key == "fonts":
            try: 
                for r_key, r_val in value.items():
                    loaded_ressources[key][r_key] = "**/" + join(assets_path, f"Fonts\\{r_val}")
                    #print_info(f"Loading font '{r_key}' from path '{loaded_ressources[key][r_key]}'...", 400)
            except AttributeError:
                _format_error(key, value)

    print_success(f"Game assets loaded successfully from '{assets_path}'!")

    return loaded_ressources