import arcade

PLAYER_IMAGE = "assets/Archeologist-Character/StaticSprite.png"

class PlayerCharacter(arcade.Sprite):
    """The player's character."""

    def __init__(self, character_scaling: int = 1):
        # Initialise the parent
        super().__init__(PLAYER_IMAGE, character_scaling)

