def update_player_health_ui(player_ui_health, player_health):
    player_ui_health.set_progress(player_health)
    if player_health > 60:
        player_ui_health.set_color("green")
    elif player_health > 30:
        player_ui_health.set_color("yellow")
    else:
        player_ui_health.set_color("red")


def update_ammo_ui(player_ui_ammo, player_ammo):
    player_ui_ammo.set_progress(player_ammo)
    return None