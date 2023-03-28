import arcade
import arcade.gl

# Internal modules
import player
import camera
from inputs import Inputs

# App parameters
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Burial Bandit"

# Scaling
TILE_SCALING = 3

# Physics
GRAVITY = 0.5

# PLAYER
LAYER_NAME_PLAYER = "Player"

# Movement speed
PLAYER_MOVEMENT_SPEED = 7
PLAYER_JUMP_SPEED = 12

# Player size
PLAYER_SCALING = 4

# Starting location with coordinates in the format (X, Y).
PLAYER_START_LOCATION = (64, 128)

# The number of pixels distance from the absolute ends of the map that the player will be stopped at.
PLAYER_X_STOP_BUFFER = 64


# LEVELS
LEVELS = [
    'maps/1_TownLevel.tmx',
    'maps/2_JungleLevel.tmx',
    'maps/3_CaveLevel.tmx',
]

# Map scale values by level
MAP_SCALE = [
    3,
    4,
    4,
]

# Custom property keys
PROPERTY_GROUND_TYPE = "ground_type"

# Layer Names from the tiled project
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_PICKUPS = "Pickups"
LAYER_NAME_FOREGROUND = "Foreground"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_DONT_TOUCH = "Don't Touch"
LAYER_NAME_NEXT_LEVEL = "Next Level"
LAYER_NAME_LADDERS = "Ladders"
LAYER_NAME_SPAWN_LOCATION = "Spawn Location"

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

    # Holds all the sounds in the game in a dictionary.
    sounds = {}

    # Holds the player Sprite object
    player_sprite = None

    # Cameras
    camera = None

    # Holds the current input values
    inputs = None
    
    # Keys
    keys_picked_up = 0

    # Level index
    current_level_index = 0

    # Starting point
    player_start_location: arcade.Point = None

    def __init__(self) -> None:

        # Create the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.csscolor.SKY_BLUE)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        # INPUT SYSTEM
        self.inputs = Inputs()

        # MAP LOAD
        # The path to the map file
        map_name = LEVELS[self.current_level_index]

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
            LAYER_NAME_LADDERS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_NEXT_LEVEL: {
                "use_spatial_hash": True,
            },
        }

        # Load tiled map
        self.tile_map = arcade.load_tilemap(map_name, MAP_SCALE[self.current_level_index], layer_options)

        # Can be used to obtain custom properties on the map.
        # print(self.tile_map.properties)
        
        # Convert Tiled map to a arcade scene with SpriteLists for each layer.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Set the background color from the map file.
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Get the player start location from the tiled map file.
        # Uses a point object on the "Spawn Location" layer
        # to define the location.
        if LAYER_NAME_SPAWN_LOCATION in self.tile_map.object_lists.keys():
            self.player_start_location = self.tile_map.object_lists[LAYER_NAME_SPAWN_LOCATION][0].shape
        else:
            self.player_start_location = PLAYER_START_LOCATION

        self.map_width_px = self.tile_map.width * self.tile_map.tile_width * MAP_SCALE[self.current_level_index]
        # END MAP LOAD


        # CREATE PLAYER CHARACTER
        # Create the list for the player sprites
        self.scene.add_sprite_list(LAYER_NAME_PLAYER)
        # Put in front of the BG so the
        # player is not hidden incorrectly.
        self.scene.add_sprite_list_before(LAYER_NAME_PLAYER, LAYER_NAME_FOREGROUND)
        
        # Make the player character object and
        # place them at the start of the level.
        self.player_sprite = player.PlayerCharacter(PLAYER_SCALING)
        self.player_sprite.center_x = self.player_start_location[0]
        self.player_sprite.center_y = self.player_start_location[1]
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_sprite)

        # Create the physics engine to let the player move.
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            gravity_constant=GRAVITY,
            walls=self.scene[LAYER_NAME_PLATFORMS],
            ladders=self.scene[LAYER_NAME_LADDERS]
        )
        # END CREATE PLAYER CHARACTER

        # CAMERAS
        # Make the camera that will follow the player.
        self.camera = camera.GameCamera(self.width, self.height)
        # Set it's start location to where the player is
        # instantly, so that it doesn't drift to the start.
        self.camera.camera_to_player(self.player_sprite, 1)
        self.camera.update()

        # LOAD SOUNDS
        self.sounds = {
            'keys_on_surface': arcade.load_sound('assets/Audio/keys_on_surface_zapsplat.mp3'),
        }

        # Hack to prevent lag spikes when playing
        # the sounds for the first time.
        for sound in self.sounds.values():
            sound.stop(sound.play(0))
        # END LOAD SOUNDS

        # GAMEPLAY VALUES
        # Set Keys picked up to none.
        self.keys_picked_up = 0
        # Get the number of keys placed on the pickup layer.
        self.keys_to_pick_up = len(self.scene[LAYER_NAME_PICKUPS])
        # print("Initial keys picked up: "+str(self.keys_picked_up))


    def on_update(self, delta_time):
        """Movement and game logic"""

        self.stop_player_at_ends()

        # Move the player with the physics engine.
        self.physics_engine.update()

        # Update player animation
        self.player_sprite.update_animation(delta_time)

        # Check if the player hits something deadly.
        self.check_for_deadly_surfaces()

        # Check if the player picked up a key.
        self.check_for_pickup_collision()

        self.check_for_next_level()

        # self.play_walking_sfx()
        

    def on_draw(self):
        """Render the screen."""
        self.clear()

        self.camera.camera_to_player(self.player_sprite)
        self.camera.use()

        self.scene[LAYER_NAME_PICKUPS].update_animation()

        # Draw with nearest pixel sampling to get that pixelated look.
        self.scene.draw(filter = arcade.gl.NEAREST)
        # self.scene.draw()dd
        # self.scene[LAYER_NAME_PLATFORMS].draw_hit_boxes(arcade.color.GREEN, 3)

    def check_for_deadly_surfaces(self):
        """Check if the player hits something damaging"""
        if arcade.check_for_collision_with_list(
            self.player_sprite,
            self.scene[LAYER_NAME_DONT_TOUCH]
        ):
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
            self.player_sprite.center_x = self.player_start_location[0]
            self.player_sprite.center_y = self.player_start_location[1]

    def check_for_pickup_collision(self):
        """Collect keys when the player walks into them."""

        # See if we hit any keys
        pickup_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_PICKUPS]
        )

        if len(pickup_hit_list) > 0:
            self.sounds['keys_on_surface'].play()

        # Loop through each key we hit (if any) and remove it
        for pickup in pickup_hit_list:
            # Remove the coin
            pickup.remove_from_sprite_lists()
            # Add to the key counter
            self.keys_picked_up += 1
            # Play a sound
            # arcade.play_sound(self.collect_coin_sound)
            # print("Keys picked up: "+str(self.keys_picked_up))

    def check_for_next_level(self):
        """When the player reaches the end of the level,
        load the next one."""

        if arcade.check_for_collision_with_list(
            self.player_sprite,
            self.scene[LAYER_NAME_NEXT_LEVEL]
        ) and self.keys_picked_up >= self.keys_to_pick_up :
            self.keys_picked_up = 0
            if len(LEVELS)-1 > self.current_level_index:
                self.current_level_index += 1
            self.setup()

    def play_walking_sfx(self):
        """
        Play a sound effect corresponding
        to the surface the player is walking on.
        """
        # Find the tiles that the player is standing on.
        tiles_touching = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_PLATFORMS]
        )
        print(tiles_touching)
        ground_type: str = None
        for tile in tiles_touching:
            ground_type = tile.properties[PROPERTY_GROUND_TYPE]

        if self.player_sprite.change_x != 0 and ground_type != None:
            print(ground_type)

    def stop_player_at_ends(self):
        """
        Stop the player walking off the ends of the level.
        Call this before the physics update.
        """
        # Where the player will be on the next
        # physics update if the change goes ahead.
        anticipated_position = self.player_sprite.center_x + self.player_sprite.change_x
        print("anticipated_position", anticipated_position)
        # Stop the player at the left side of the map.
        if self.inputs.left_pressed and anticipated_position <= PLAYER_X_STOP_BUFFER:
            self.player_sprite.change_x = 0
        # Stop the player on the right side of the map.
        elif self.inputs.right_pressed and anticipated_position >= self.map_width_px - PLAYER_X_STOP_BUFFER:
            self.player_sprite.change_x = 0
        

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