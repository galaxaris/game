"""
File intended for debugging game & api features.
"""

from game.setup.imports_collection import *

ASSETS_DIR = resource_path("assets")
audio_manager = AudioManager()
resource_manager = Resource(ResourceType.GLOBAL, ASSETS_DIR)

RESSOURCES = init_ressource_manager(resource_manager, audio_manager, ASSETS_DIR)

loaded_ressources = ""

loaded_ressources += "Textures:\n"
for key, value in RESSOURCES["textures"].items():
    loaded_ressources += f"  {key}: {value.path}\n"
loaded_ressources += "Animations:\n"
for key, value in RESSOURCES["animations"].items():
    loaded_ressources += f"  {key}: {value.texture.path}\n"
loaded_ressources += "Fonts:\n"
for key, value in RESSOURCES["fonts"].items():
    loaded_ressources += f"  {key}: {value}\n"
loaded_ressources += "Music:\n"
for key, value in RESSOURCES["music"].items():
    loaded_ressources += f"  {key}: {value}\n"
loaded_ressources += "SFX:\n"
for key, value in RESSOURCES["sfx"].items():
    loaded_ressources += f"  {key}: {value}\n"

print_info(loaded_ressources, 400)