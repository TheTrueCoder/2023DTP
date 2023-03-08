import arcade

PLAYER_IMAGE = "assets/Archeologist-Character/StaticSprite.png"
CHARACTER_SCALING = 1

class PlayerCharacter(arcade.Sprite):
    """The player's character."""

    def __init__(self):
        # Initialise the parent
        super().__init__(PLAYER_IMAGE, CHARACTER_SCALING)

