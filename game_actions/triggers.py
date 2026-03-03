"""
All callbacks for triggers used & defined in the game
"""

import pygame as pg
import random as rd
from api.environment.Solid import Solid
from api.environment.Trigger import Trigger, Trigger_KillBox

def create_killBox(collections, lenght, game, game_heigth):
    """
    Adds a killbox of specified lenght, 400px behind the back of screen
    """
    for x in range(0, lenght*1000, 1000):
        collections += [Trigger_KillBox((x, game_heigth+400), (1000, 100), ["player"], once=False)]


def print_alert_msg(msg):
    print(msg)

def summon_stairs1(collections, game_height, gameLength=200, blockDim = (50, 10)):

    print("Summoning stairs... - To be activated only once!")
    y=451
    for x in range(1100, 2000, 100):
        step = Solid((x, y), (30, 10))
        step.set_color((155, 255, 55))
        collections += [step]
        y-=10

    #Adds floating blocks
    count = 0
    for i in range(gameLength):
        count += 1
        randomNum = rd.randint(-6, 10)
        block = Solid((1000 + blockDim[0]*(i+13), game_height - 300 - blockDim[1]*(randomNum)), blockDim) #y=300 is where the stairs stop
        block.set_color((55, 55, 145))
        collections += [block]