import arcade
import arcade.gl
import player
import camera
from inputs import Inputs

# App parameters
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Burial Bandit"

# Scaling
TILE_SCALING = 4

# Player size
PLAYER_SCALING = 4
# Starting location with co-ordiantes in the format (X, Y).
PLAYER_START_LOCATION = (64, 128)

# Physics
GRAVITY = 0.5

# PLAYER
# Movement speed
PLAYER_MOVEMENT_SPEED = 7
PLAYER_JUMP_SPEED = 15
# Player size
PLAYER_SCALING = 4
# Starting location with coordinates in the format (X, Y).
PLAYER_START_LOCATION = (64, 128)
LAYER_NAME_PLAYER = "Player"

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

    # Holds the current input values
    inputs = None
    # Axis go from 1 to -1 to define direction and speed.
    # inputs.axis.up: float = None
    # inputs.axis.right: float = None
    # Actions are on/off button presses
    # inputs.actions.jump: bool = None



    def __init__(self) -> None:

        # Create the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.csscolor.SKY_BLUE)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        # CAMERAS
        # Make the camera that will follow the player.
        self.camera = camera.CinematicCamera(self.width, self.height)

        # INPUT SYSTEM
        self.inputs = Inputs()

        # MAP LOAD
        # The path to the map file
        map_name = "maps/Level_1.tmx"

        # Configure map layers to optimise performance.
        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_PICKUPS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_DONT_TOUCH: {
                "use_spatial_hash": True,
            },
        }

        # Load tiled map
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        print(self.tile_map.properties)
        
        # Convert Tiled map to a arcade scene with SpriteLists for each layer.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Set the background color from the map file.
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)
        # END MAP LOAD


        # CREATE PLAYER CHARACTER
        # Create the list for the player sprites
        self.scene.add_sprite_list(LAYER_NAME_PLAYER)
        # Put in front of the BG so the
        # player is not hidden incorrectly.
        self.scene.add_sprite_list_after(LAYER_NAME_PLAYER, LAYER_NAME_FOREGROUND)
        
        # Make the player character object and
        # place them at the start of the level.
        self.player_sprite = player.PlayerCharacter(PLAYER_SCALING)
        self.player_sprite.center_x = PLAYER_START_LOCATION[0]
        self.player_sprite.center_y = PLAYER_START_LOCATION[1]
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_sprite)

        # Create the physics engine to let the player move.
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Platforms"]
        )

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Move the player with the physics engine
        self.physics_engine.update()

        # Check if the player hits something damaging
        if arcade.check_for_collision_with_list(
            self.player_sprite,
            self.scene[LAYER_NAME_DONT_TOUCH]
        ):
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
            self.player_sprite.center_x = PLAYER_START_LOCATION[0]
            self.player_sprite.center_y = PLAYER_START_LOCATION[1]

    def on_draw(self):
        """Render the screen."""
        self.clear()

        self.camera.camera_to_player(self.player_sprite)
        self.camera.use()
        # Draw with nearest pixel sampling to get that pixelated look.
        self.scene.draw(filter = arcade.gl.NEAREST)
        # self.scene.draw()


    def process_keychange(self):
        """
        Updates the input's impact on gameplay.
        """
        # Process up/down
        if self.inputs.up_pressed and not self.inputs.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif (
                self.physics_engine.can_jump(y_distance=10)
                and not self.inputs.jump_needs_reset
            ):
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.inputs.jump_needs_reset = True
                # arcade.play_sound(self.jump_sound) # NOTE: Add sounds later
        elif self.inputs.down_pressed and not self.inputs.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

        # Process up/down when on a ladder and no movement
        if self.physics_engine.is_on_ladder():
            if not self.inputs.up_pressed and not self.inputs.down_pressed:
                self.player_sprite.change_y = 0
            elif self.inputs.up_pressed and self.inputs.down_pressed:
                self.player_sprite.change_y = 0

        # Process left/right
        if self.inputs.right_pressed and not self.inputs.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.inputs.left_pressed and not self.inputs.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

    # CAPTURE INPUTS
    def on_key_press(self, key, modifiers):
        """Sets input value for the pressed key."""

        if key == arcade.key.UP or key == arcade.key.W:
            self.inputs.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.inputs.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.inputs.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.inputs.right_pressed = True

        self.process_keychange()

    def on_key_release(self, key, modifiers):
        """Resets input value corresponding to the key released."""

        if key == arcade.key.UP or key == arcade.key.W:
            self.inputs.up_pressed = False
            self.inputs.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.inputs.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.inputs.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.inputs.right_pressed = False

        self.process_keychange()





# RUN GAME
# Run the game if the file is being run
if __name__ == "__main__":

    window = TheGame()
    window.setup()
    arcade.run()