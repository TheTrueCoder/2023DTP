import arcade
import player

# App parameters
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Burial Bandit"

# Scaling
TILE_SCALING = 2

# Physics
GRAVITY = 1

# Layer Names from the tiled project
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_PICKUPS = "Pickups"
LAYER_NAME_FOREGROUND = "Foreground"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_DONT_TOUCH = "Don't Touch"

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
    physics_engine = None

    # Holds the player Sprite object
    player_sprite = None

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
        # END MAP LOAD


        # CREATE PLAYER CHARACTER
        # Create the list for the player sprites
        self.scene.add_sprite_list("Player")
        
        
        # Make the player character object and
        # place them at the start of the level.
        self.player_sprite = arcade.Sprite("assets/Archeologist-Character/StaticSprite.png", 2)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 400
        self.scene.add_sprite("Player", self.player_sprite)

        # Create the physics engine to let the player move.
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Platforms"]
        )

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Move the player with the physics engine
        # self.physics_engine.update()


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