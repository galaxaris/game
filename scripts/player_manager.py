"""
This module allows to manage the player's settings initialization, such as controls configuration, stats, inventory, etc...
"""
from api.assets.Animation import Animation
from api.assets.Texture import Texture
from api.entity.Player import Player
from game.Variables import player_settings


def load_player_settings() -> dict:
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
        player.equip_weapon(weapon_name, cooldown=weapon_settings.get("cooldown", None),
                            damage=weapon_settings.get("projectile_damage", None))


def init_player(game) -> Player:
    """
    Initializes the player with the specified settings.

    :param game: Game object to initialize the player within
    :return: The initialized Player object
    """

    settings = load_player_settings()

    player = Player(tuple(settings["position"]), tuple(settings["size"]), settings["direction"],
                    max_velocity=settings["max_velocity"],
                    acceleration=settings["acceleration"], resistance=settings["resistance"], force=settings["force"],
                    health=settings["health"], damage_resistance=settings["damage_resistance"],
                    damage_force=settings["damage_force"])

    set_sfx_list(player, settings["sfx_list"])
    set_animations(player, {name: game.RESSOURCES["animations"][anim_name] if anim_name in game.RESSOURCES["animations"]
    else game.RESSOURCES["textures"][anim_name] for name, anim_name in settings["animations"].items()})
    equip_weapons(player, settings["weapons"])

    player.set_gravity(settings["gravity"])

    return player
