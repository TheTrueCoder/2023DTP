import arcade

class CinematicCamera(arcade.Camera):
    """
    Adds features to the default camera to make the movement nicer.
    """

    def camera_to_player(self, player_sprite: arcade.Sprite):
        """
        Moves the camera to follow the provided player character.
        """
        screen_center_x = player_sprite.center_x - (self.viewport_width / 2)
        screen_center_y = player_sprite.center_y - (
            self.viewport_height / 2
        )

        # Don't let camera travel past 0
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.move_to(player_centered)