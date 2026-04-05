"""
This module allows to manage the player's settings initialization, such as controls configuration, stats, inventory, etc...
"""

from api.utils.DataManager import load_json
from game.setup.imports_collection import *

def load_player_settings(path: str = "setup\\player_settings.json") -> dict:
    """
    Loads the player's settings from a json file. If the file is not found or if some settings are missing, it will return the default settings.

    :param path: Path to the json file containing the player's settings
    :return: A dictionary containing the player's settings
    """
    player_settings = load_json(path)

    if not player_settings:
        print_warning(f"Using default player settings instead.")
        return DEFAULT_SETTINGS.copy()

    # Check if all the settings are present, if not set them to the default value
    for key, value in DEFAULT_SETTINGS.items():
        if key not in player_settings:
            print_warning(f"'{key}' not found in player settings, setting it to the default value: {value}")
            player_settings[key] = value

    print_success(f"Player settings loaded successfully from '{path}'!")
    return player_settings


def set_sfx_list(player: Player, sfx_list: dict[str, str]):
    """
    Sets the player's sound effects list.

    :param player: Player object to set the sound effects list to
    :param sfx_list: Dictionary containing the sound effects (key: name)
    """
    player.set_sfx_list(sfx_list)

def set_animations(player: Player, animations: dict[str, Animation | Texture]):
    """
    Sets the player's animations.

    :param player: Player object to set the animations to
    :param animations: Dictionary containing the animations (key: name)
    """
    player.bind_animations(animations)

def equip_weapons(player: Player, weapons: dict[str, dict[str, int]]):
    """
    Equips the player with the specified weapons.

    :param player: Player object to equip the weapons to
    :param weapons: Dictionary containing the weapons to equip (key: weapon name, value: dictionary containing the weapon's settings)
    """
    for weapon_name, weapon_settings in weapons.items():
        player.equip_weapon(weapon_name, cooldown=weapon_settings.get("cooldown", None), damage=weapon_settings.get("projectile_damage", None))

def init_player(game) -> Player:
    """
    Initializes the player with the specified settings.

    :param game: Game object to initialize the player within
    :return: The initialized Player object
    """
    
    settings = load_player_settings()

    player = Player(list(settings["position"]), list(settings["size"]), settings["direction"], max_velocity=settings["max_velocity"], 
                    acceleration=settings["acceleration"], resistance=settings["resistance"], force=settings["force"],
                    health=settings["health"], damage_resistance=settings["damage_resistance"], damage_force=settings["damage_force"])
    
    set_sfx_list(player, settings["sfx_list"])
    set_animations(player, {name: game.RESSOURCES["animations"][anim_name] if anim_name in game.RESSOURCES["animations"] 
                            else game.RESSOURCES["textures"][anim_name] for name, anim_name in settings["animations"].items()})
    equip_weapons(player, settings["weapons"])

    player.set_gravity(settings["gravity"])

    return player


#%%################ Default settings ##############
#Used when the player settings file isn't found, or if some settings are missing
DEFAULT_SETTINGS = {
    "gravity": 0.5,
    "position": [310, 410],
    "size": [48, 48],
    "direction": "right",

    "max_velocity": 2,
    "acceleration": 0.5, 
    #Do not set under or equal to 0.01, otherwise the player will be sliding forever (no resistance)
    "resistance": 0.2, #< 0.2 more 'sliding' (e.g. ice, 0.01), > 0.2 more sticky (e.g. mud)
    "force": 20,

    "health": 100,
    "damage_resistance": 0,
    "damage_force": 10,

    "weapons": {
        "WaterPistol": {
            "cooldown": 200,
            "projectile_damage": 30
        },
        "EarthPistol": {
            "cooldown": 200,
            "projectile_damage": 15
        },
        "GrapplingPistol": {
            "cooldown": 500,
            "projectile_damage": 15
        }
    },

    "sfx_list": {
        "jump": "jump",
        "death": "death",
        "fire": "fire"
    },

    "animations": {
        "run": "run",
        "run_fast": "run_fast",
        "idle": "idle",
        "jump": "jump_anim",
        "fall": "fall_anim",
        "hit": "hit"
    }
}