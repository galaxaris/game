game_settings = {
        "RENDER_WIDTH": 640,
        "RENDER_HEIGHT": 360,
        "SCREEN_WIDTH": 1280,
        "SCREEN_HEIGHT": 720,
        "FPS": 60,
        "WINDOW_TITLE": "Robot Recovery",
        "GRAVITY": 0.5,
}

player_settings = {
    "position": [310, 110],
    "size": [48, 48],
    "direction": "right",

    "gravity": 0.5,
    "max_velocity": 2,
    "acceleration": 0.5,
    "resistance": 0.2,
    "force": 20,

    "health": 100,
    "damage_resistance": 0,
    "damage_force": 10,

    "weapons": {
        "WaterPistol": {
            "cooldown": 200,
            "projectile_damage": 30
        },
        "EarthPistol": {
            "cooldown": 0,
            "projectile_damage": 15
        },
        "GrapplingPistol": {
            "cooldown": 500,
            "projectile_damage": 15
        }
    },

    "sfx_list": {
        "jump": "jump",
        "death": "death",
        "fire": "fire"
    },

    "animations": {
        "run": "run",
        "run_fast": "run_fast",
        "idle": "idle",
        "jump": "jump_anim",
        "fall": "fall_anim",
        "hit": "hit"
    }
}

# TODO: Remove in Production, only for testing purposes
story = {
    "has_started": False,
    "current_chapter": 4,
}