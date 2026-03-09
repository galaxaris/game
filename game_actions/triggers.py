"""
All callbacks for triggers used & defined in the game
"""

import pygame as pg
import random as rd
from os.path import join

from api.engine.Scene import Scene
from api.assets.Texture import Texture
from api.environment.Solid import Solid
from api.environment.Trigger import Trigger, TriggerKillBox, TriggerInteract
from api.UI.Dialog import Dialog
from api.utils.ResourcePath import resource_path
from api.utils.Console import *
from api.utils.GlobalVariables import global_vars as GV

ASSETS_PATH = resource_path("assets")


def create_killBox(collections, lenght, game_heigth):
    """
    Adds a killbox of specified lenght, 400px behind the back of screen
    """
    collections += [TriggerKillBox((0, game_heigth+400), (lenght*1000, 100), ["player"], once=False, sfx=["death", "death2"])]

def summon_stairs1(scene: Scene, me: Texture, pnj: Texture, info_box_texture: Texture, collections, game_height, texture_common: Texture, texture_checkpoint: Texture, rdLength=20, blockDim = (50, 10),
                    dialog_font: str = ("**/" + join(ASSETS_PATH, "Fonts\\Gm6x11.ttf"))):

    print_info("Summoning stairs... - To be activated only once!")
    y=451
    for x in range(1100, 2000, 100):
        step = Solid((x, y), (30, 10))
        step.set_color((155, 255, 55))
        step.set_texture(texture_common)
        collections += [step]
        y-=10

    #Adds floating blocks
    count = 0
    for i in range(rdLength):
        count += 1
        randomNum = rd.randint(-6, 10)
        block = Solid((1350 + blockDim[0]*(i+13), game_height - 300 - blockDim[1]*(randomNum)), blockDim) #y=300 is where the stairs stop
        block.set_color((55, 55, 145))
        block.set_texture(texture_common)
        collections += [block]

    #Adds a mid-course platform
    platform = Solid((1350 + blockDim[0]*(rdLength+13) + blockDim[0], game_height - 300 - blockDim[1]*(randomNum)), (blockDim[0]*5, blockDim[1]))
    platform.set_color((55, 55, 145))
    platform.set_texture(texture_checkpoint)
    collections += [platform]

    #Adds a dialogue trigger
    dialog = Dialog(dialog_font)
    dialog.add_character("Sign", info_box_texture)
    dialog.add_character("You", me)
    dialog.add_message("Sign", "WHAT'S UP GUY??? Who are you??")
    dialog.add_message("You", "Uhhh, am I really speaking to a sign? * sighs *")
    dialog.add_message("Sign", "Uh, yes. Anyway. Do you want to continue? Then, continue, the way is after me.")
    dialog.add_message("You", "Okay, see you.")

    scene.UI.add("Checkpoint", dialog)

    #Adds a trigger to continue the stairs
    def summon_stairs2(rdLength=rdLength, collections=collections, texture=texture_checkpoint):
        print_info("Summoning stairs part 2... - To be activated only once!")
        y=game_height - 300 - blockDim[1]*(randomNum)
        for x in range(3300, 3600, 10):
            step = Solid((x, y), (30, 10))
            step.set_color((155, 255, 55))
            step.set_texture(texture)
            collections += [step]
            y-=30

    info_box = TriggerInteract((1350 +blockDim[0]*2 + blockDim[0]*(rdLength+13) + blockDim[0], game_height - 300 - blockDim[1]*(randomNum) -30), (32, 32), ["player"], [lambda obj: scene.UI.show("Checkpoint")])
    info_box.set_texture(info_box_texture)
    collections += [info_box]

    collections += [Trigger((1350 + 40 + blockDim[0]*2 + blockDim[0]*(rdLength+13) + blockDim[0], game_height - 300 - blockDim[1]*(randomNum) -30), (32, 32), ["player"], [summon_stairs2], once=True)]