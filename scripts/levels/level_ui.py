def update_level_ui(player_ui_health, player_health):
    player_ui_health.set_progress(player_health)
    if player_health > 60:
        player_ui_health.set_color("green")
    elif player_health > 30:
        player_ui_health.set_color("yellow")
    else:
        player_ui_health.set_color("red")