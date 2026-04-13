#=============================================================================
#Scripts du Niveau 2 : "La Forêt"
#=============================================================================

from api.environment.Solid import Solid
from api.Game import Game
from api.engine.Scene import Scene
from api.utils import Fonts
from api.utils.Console import print_info, print_success, print_warning
from api.assets.Texture import Texture
from api.UI.Dialog import Dialog
from api.environment.Trigger import Trigger, TriggerInteract
import random as rd


#%%###########################################################################
# GAMEPLAY — MÉCANIQUE EAU / CHECKPOINT
##############################################################################

def refill_water(player, game: Game):
    """
    Recharge l'arme eau du joueur à son maximum.
    Déclenché par TriggerInteract sur un collecteur de pluie.
    """
    try:
        player.ammo = getattr(player, "max_ammo", 30)
        game.audio_manager.play_sfx("water_refill")
        print_success("Réservoir d'eau rechargé !")
    except Exception as e:
        print_warning(f"[refill_water] {e}")


def save_checkpoint(player, pos: list, game: Game):
    """
    Enregistre la position de réapparition du joueur.
    `pos` est capturée par closure depuis Level2Scene.py (position fixe du checkpoint).
    """
    try:
        player.start_pos = list(pos)
        game.audio_manager.play_sfx("checkpoint")
        print_success(f"Checkpoint activé — réapparition en {pos}")
    except Exception as e:
        print_warning(f"[save_checkpoint] {e}")


#%%############################################################################
# DIALOG FACTORIES
#############################################################################

def make_ecology_dialog(font: str, sign_texture, title: str, message: str) -> Dialog:
    """
    Crée un dialogue simple pour un panneau écologique.
    `title` sert à la fois de nom de personnage et de titre du message.
    """
    dialog = Dialog(font)
    dialog.add_character(title, sign_texture)
    dialog.add_message(title, message)
    return dialog


def make_story_dialog(font: str, sign_texture, character_name: str,
                      messages: list) -> Dialog:
    """
    Crée un dialogue à plusieurs répliques pour les journaux de bord / PNJ narratifs.
    `messages` : liste de strings, chaque string = une réplique.
    """
    dialog = Dialog(font)
    dialog.add_character(character_name, sign_texture)
    for msg in messages:
        dialog.add_message(character_name, msg)
    return dialog


def make_melanie_dialog(font: str, melanie_texture, player_texture) -> Dialog:
    """
    Crée le dialogue radio de Mélanie Cavill — contact narratif principal du niveau 2.
    Déclenché une seule fois quand le joueur atteint le checkpoint #1.
    """
    dialog = Dialog(font)
    dialog.add_character("Mélanie Cavill", melanie_texture)
    dialog.add_character("Vous", player_texture)

    dialog.add_message("Mélanie Cavill",
        "Ici Mélanie Cavill depuis la station orbitale. Tu m'entends ? "
        "Signal capté — parfait.")
    dialog.add_message("Vous",
        "Reçu, Mélanie. Cette forêt est dans un état catastrophique...")
    dialog.add_message("Mélanie Cavill",
        "Nos capteurs confirment. 87 % de la végétation primaire détruite. "
        "Mais il reste des zones viables. La nature résiste, même ici.")
    dialog.add_message("Mélanie Cavill",
        "Priorité : neutraliser le CF-7. C'est lui qui coordonne toutes les unités. "
        "Sans lui, elles s'arrêteront d'elles-mêmes.")
    dialog.add_message("Vous",
        "Et les collecteurs d'eau de pluie ?")
    dialog.add_message("Mélanie Cavill",
        "Interagis avec eux pour recharger ton pistolet. "
        "C'est ta seule arme efficace contre le refroidisseur du CF-7. "
        "Je reste en ligne. Bonne chance.")

    return dialog


#%%###########################################################################
# INTERRUPTEURS / TRIGGERS DYNAMIQUES
##############################################################################

def activate_switch(scene: Scene, game: Game, switch_id: str):
    """
    Active un interrupteur nommé et fait apparaître les éléments associés.

    switch_id = "bridge1"
        -> Déploie deux rangées de planches de bois sur le GAP #2 (x: 1562→1640).
          Rangée basse (y=288) et rangée haute (y=238) pour offrir deux hauteurs
          de traversée selon l'impulsion du saut.
    """
    try:
        game.audio_manager.play_sfx("switch")
    except Exception:
        pass

    print_success(f"Interrupteur '{switch_id}' activé !")

    if switch_id == "bridge1":
        bridge = []
        plank_w = 26
        bridge_x_start, bridge_x_end = getattr(scene.this, "bridge1_range", (1562, 1640))
        bridge_rows = getattr(scene.this, "bridge1_rows", (238, 288))
        top_row_y, bottom_row_y = bridge_rows

        # Rangée basse — traversée au sol
        for x in range(int(bridge_x_start), int(bridge_x_end), plank_w):
            plank = Solid((x, int(bottom_row_y)), (plank_w, 12))
            plank.set_texture(game.RESSOURCES["textures"]["bridge_plank"])
            bridge.append(plank)

        # Rangée haute — raccourci depuis les plateformes élevées
        for x in range(int(bridge_x_start), int(bridge_x_end), plank_w):
            plank_high = Solid((x, int(top_row_y)), (plank_w, 12))
            plank_high.set_texture(game.RESSOURCES["textures"]["bridge_plank"])
            bridge.append(plank_high)

        for obj in bridge:
            scene.add(obj, "#object")

        print_info(
            f"Pont d'urgence déployé (x={int(bridge_x_start)}-{int(bridge_x_end)}, "
            f"y={int(top_row_y)} et y={int(bottom_row_y)})"
        )


def spawn_enemy_wave(scene: Scene, game: Game, positions: list):
    """
    Invoque une vague d'ennemis aux positions [(x, y), ...] données.
    Utile pour des rencontres de combat déclenchées par trigger.
    """
    from api.entity.Enemy import Enemy
    from api.assets.Animation import Animation
    from game.Variables import game_settings

    spawned = []
    for pos in positions:
        e = Enemy(pos, (48, 48), mode="patrol", range=150)
        e.set_gravity(game_settings["GRAVITY"])
        e.set_animation(Animation(game.RESSOURCES["textures"]["enemy"], 11, 50))
        spawned.append(e)

    for e in spawned:
        scene.add(e, "#object")

    print_info(f"Vague de {len(spawned)} ennemis invoquée !")


# #############################################################################
#  LEGACY : summon_stairs1 (conservé depuis la version originale)
# #############################################################################

def summon_stairs1(scene: Scene, me: Texture, pnj: Texture, info_box_texture: Texture,
                   game_height, texture_common: Texture, texture_checkpoint: Texture,
                   rdLength=20, blockDim=(50, 10), dialog_font: str = Fonts.DEFAULT_FONT):
    """
    Génère procéduralement un escalier de troncs + des blocs flottants aléatoires.
    Activé une seule fois par un Trigger.
    """
    collections = []
    print_info("Summoning stairs...")

    #Escalier descendant
    y = 451
    for x in range(1100, 2000, 100):
        step = Solid((x, y), (30, 10))
        step.set_color((155, 255, 55))
        step.set_texture(texture_common)
        collections.append(step)
        y -= 10

    #Blocs flottants aléatoires
    randomNum = 0
    for i in range(rdLength):
        randomNum = rd.randint(-6, 10)
        block = Solid(
            (1350 + blockDim[0] * (i + 13), game_height - 300 - blockDim[1] * randomNum),
            blockDim
        )
        block.set_color((55, 55, 145))
        block.set_texture(texture_common)
        collections.append(block)

    #Grande plateforme de mi-parcours
    platform = Solid(
        (1350 + blockDim[0] * (rdLength + 13) + blockDim[0],
         game_height - 300 - blockDim[1] * randomNum),
        (blockDim[0] * 5, blockDim[1])
    )
    platform.set_color((55, 55, 145))
    platform.set_texture(texture_checkpoint)
    collections.append(platform)

    #Dialogue du panneau
    dialog = Dialog(dialog_font)
    dialog.add_character("Sign", info_box_texture)
    dialog.add_character("You", me)
    dialog.add_message("Sign", "WHAT'S UP GUY??? Who are you??")
    dialog.add_message("You", "Uhhh, am I really speaking to a sign? * sighs *")
    dialog.add_message("Sign", "Uh, yes. Anyway. The way is after me.")
    dialog.add_message("You", "Okay, see you.")
    scene.UI.add("Checkpoint", dialog)

    #Fonction interne de continuation (escalier partie 2)
    _final_random = randomNum   # capture pour la closure

    def summon_stairs2():
        coll2 = []
        print_info("Summoning stairs part 2...")
        y2 = game_height - 300 - blockDim[1] * _final_random
        for x in range(3300, 3600, 10):
            step = Solid((x, y2), (30, 10))
            step.set_color((155, 255, 55))
            step.set_texture(texture_checkpoint)
            coll2.append(step)
            y2 -= 30
        for obj in coll2:
            scene.add(obj, "#object")

    #Panneau interactif de mi-parcours
    info_box_x = 1350 + blockDim[0] * 2 + blockDim[0] * (rdLength + 13) + blockDim[0]
    info_box_y = game_height - 300 - blockDim[1] * _final_random - 30

    info_box = TriggerInteract(
        (info_box_x, info_box_y), (32, 32), ["player"],
        [lambda obj: scene.UI.show("Checkpoint")]
    )
    info_box.set_texture(info_box_texture)
    collections.append(info_box)

    collections.append(Trigger(
        (info_box_x + 140, info_box_y), (32, 32), ["player"],
        [lambda obj: summon_stairs2()], once=True
    ))

    for obj in collections:
        scene.add(obj, "#object")
