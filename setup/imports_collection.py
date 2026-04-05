"""
This module centralizes all the imports of the game.
"""

#%%################## SYSTEM & SETUP ################## 
#######################################################

import os
import time
import random as rd
from os.path import join
import pygame as pg

#Changes working directory to project root
#(Allows to launch the game from any folder without a path error)

#From main.py:
#os.chdir(os.path.dirname(os.path.abspath(__file__)))
#From game/setup/imports_collection.py:
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


#%%#################### API CORE ###################### 
#######################################################

from api.Game import Game
from api.GameObject import GameObject
from api.engine.Scene import Scene


#%%##################### API UI ####################### 
#######################################################

from api.UI.Button import Button
from api.UI.Dialog import Dialog
from api.UI.Modal import Modal
from api.UI.Text import Text
from api.UI.TextBox import TextBox
from api.UI.Choice import Choice
from api.UI.GameUI import UIElement
from api.UI.ProgressBar import ProgressBar


#%%################ API ASSETS ######################### 
########################################################

from api.assets.Animation import Animation
from api.assets.ResourceManager import Resource, ResourceType
from api.assets.Texture import Texture
from api.assets.AudioManager import AudioManager


#%%################### API ENTITIES #################### 
########################################################

from api.entity.Entity import Entity
from api.entity.Player import Player
from api.entity.Boss import Boss
from api.entity.Enemy import Enemy


#%%################# API ENVIRONMENT ################### 
########################################################

from api.environment.Background import Background
from api.environment.Parallax import ParallaxLayer, ParallaxBackground
from api.environment.Solid import Solid
from api.environment.Trap import Trap
from api.environment.Trigger import Trigger, TriggerInteract, TriggerKillBox


#%%#################### API UTILS ##################### 
#######################################################

from api.utils import Debug, Fonts
from api.utils.ResourcePath import resource_path
from api.utils.Console import *
from api.utils.InputManager import (
    get_inputs, 
    get_once_inputs, 
    prevent_input, 
    get_held_inputs, 
    onKeyDown, 
    onKeyUp, 
    onKeyPress
)

#%%################## GAME SETUP ####################
#####################################################
from game.setup.game_settings import init_game_settings
from game.setup.ressource_manager import init_ressource_manager

#Do not use Omicronde to avoid circular imports
#from game.setup.game import Omicronde


#%%################## GAME SCRIPTS ##################### 
########################################################

from game.scripts.triggers import *
from game.scripts.ui import menu_in_game, main_menu, toggle_audio


#%%################## GLOBAL VARIABLES ####################
###########################################################
ASSETS_PATH = resource_path("assets")