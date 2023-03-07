import arcade
import core

# App parameters
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Burial Bandit"


class TheGame(core.WindowCore):
    def __init__(self) -> None:

        # Create the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.csscolor.SKY_BLUE)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        pass

    def on_draw(self):
        """Render the screen."""

        self.clear()




# RUN GAME
# Run the game if the file is being run
if __name__ == "__main__":

    window = TheGame()
    window.setup()
    arcade.run()