import arcade
import player.PlayerCharacter

# App parameters
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Burial Bandit"

# Scaling
TILE_SCALING = 2

# Physics
GRAVITY = 1

class TheGame(arcade.Window):
    """
    The main window class for the Burial Bandit game.
    
    Runs the game after running the `setup()` method
    and calling `arcade.run()`.
    """

    # Tiled map data
    tile_map = None
    # The arcade scene for all data from the tiled map.
    scene = None

    # Cameras
    camera = None

    def __init__(self) -> None:

        # Create the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.csscolor.SKY_BLUE)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        # CAMERAS
        # Make the camera that will follow the player.
        self.camera = arcade.Camera(self.width, self.height)

        # MAP LOAD
        # The path to the map file
        map_name = "maps/FantasyJungle_map1.tmx"

        # Configure map layers
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
        }

        # Load tiled map
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)
        
        # Convert Tiled map to a arcade scene with SpriteLists for each layer.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Set the background color from the map file.
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Create the physics engine to let the player move.
        # self.physics_engine = arcade.PhysicsEnginePlatformer(
        #     self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Platforms"]
        # )


    def on_draw(self):
        """Render the screen."""

        self.clear()

        self.camera.use()
        self.scene.draw()

    # Input Handling





# RUN GAME
# Run the game if the file is being run
if __name__ == "__main__":

    window = TheGame()
    window.setup()
    arcade.run()