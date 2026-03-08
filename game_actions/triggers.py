"""
All callbacks for triggers used & defined in the game
"""

import pygame as pg
import random as rd
from api.assets.Texture import Texture
from api.environment.Solid import Solid
from api.environment.Trigger import Trigger, TriggerKillBox
from api.utils.Console import *
from api.utils.GlobalVariables import global_vars as GV

def create_killBox(collections, lenght, game_heigth):
    """
    Adds a killbox of specified lenght, 400px behind the back of screen
    """
    collections += [TriggerKillBox((0, game_heigth+400), (lenght*1000, 100), ["player"], once=False, sfx="death")]

def summon_stairs1(collections, game_height, texture_common: Texture, texture_checkpoint: Texture, rdLength=20, blockDim = (50, 10)):

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