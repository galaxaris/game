"""
=== Omicronde Project Game - Galaxaris ===

This is the entry point of the Omicronde Game. Built using the Omicronde API.

Authors: Galaxaris & Associates

v.0.1 (in development)
- 07/04/2026

Copyright (c) 2026 Galaxaris & Associates. All rights reserved.

"""
#### RUN THE GAME WITH "python -m game.main" FROM THE ROOT DIRECTORY OF THE PROJECT ####


### TODO: levels to be implemented and loaded in a JSON BDD (using the editor) => GameObjects, triggers, UI, background, music, dialogs, etc...
### TODO: create a 'SceneManager' to manage multiple game scenes (menus, levels...) and transitions between them


#%%################ IMPORTS ####################
################################################
from game.setup.imports_collection import *
from game.setup.game import Omicronde


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