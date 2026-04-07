import game.setup.game_settings
from api.engine.Scene import Scene
import pygame as pg

size = pg.Vector2(game.setup.game_settings.settings["RENDER_WIDTH"], game.setup.game_settings.settings["RENDER_HEIGHT"])

MapScene = Scene(size)