"""
=== Omicronde Project Game - Galaxaris ===

This is the entry point of the Omicronde Game. Built using the Omicronde API.

Authors: Galaxaris & Associates

v.Beta (in development)
- 03/03/2026

Copyright (c) 2026 Galaxaris & Associates. All rights reserved.

"""
#### RUN THE GAME WITH "python -m game.main" FROM THE ROOT DIRECTORY OF THE PROJECT ####


### TODO: levels to be implemented and loaded in a JSON BDD (using the editor) => GameObjects, triggers, UI, background, music, dialogs, etc...

### TODO: create an 'InputManager' to centralize game input handling
### TODO: create an 'EventManager' to centralize game events handling
### TODO: create a 'SceneManager' to manage multiple game scenes (menus, levels...) and transitions between them

### TODO: create a 'ResourceManager' to centralize the loading and stock of game assets
    ## => try/except for loading function, "pink" texture as fallback
    ### TODO: create a 'TextureManager' to manage and stock game textures; texture atlases (=> sprites) and animations
        ## => TODO: define a standard for texture atlases & anims (associated .json files?)
    ### TODO: create an 'AudioManager' to manage and stock game SFX and music
    ### TODO: create a 'UIManager' to define specific game UI elements and keep an overall style (fonts, colors...)


#%%################ IMPORTS ####################
################################################
from game.setup.imports_collection import *
from game.setup.game import Omicronde

#%%############# ON START #############################
#######################################################
print_info("Welcome to the Omicronde Game - [bold]Galaxaris Demo[/bold] !\nIf you don't see the game window, it might be behind your current window, please check!\nAnd... [green]HAVE FUN![/green]")

#%%################ MAIN ##############################
#######################################################
if __name__ == "__main__":
    try:
        #%%############## CLOSE SPLASH SCREEN #################
        #######################################################
        in_an_exe = True
        try:
            import pyi_splash

            time.sleep(5)
            pyi_splash.close()
        except ImportError:
            # we are not in an exe file
            in_an_exe = False

        #%%############## LAUNCH THE GAME #####################
        #######################################################
        app = Omicronde()
        app.launch()

    except Exception:
        #%%############## CLOSE PG WINDOW #####################
        #######################################################
        try:
            import pygame as pg

            pg.quit()

        except ImportError:
            pass

        #%%############## CLOSE CMD ###########################
        #######################################################
        from api.utils.Console import *

        print_error("[bold red]=== FATAL ERROR ===[/bold red]\nAn unexpected error occurred while running the game. Please check the error message above and try to fix it. If you need help, don't hesitate to contact us with the error message and the steps to reproduce it. We will be happy to help you!")
        import traceback

        error = traceback.format_exc()
        print_error(f"[bold red]{error}[/bold red]", width=100)

        if in_an_exe:
            print_warning("CMD is self closing in 10 seconds...")
            print("")
            print_countdown(10)
            print("")

        print_info("Goodbye !")