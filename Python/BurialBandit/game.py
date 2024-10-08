from typing import Dict
import arcade
import arcade.gl

# Internal modules
import player
import camera
from inputs import Inputs
from end_sequence import EndSequence

# App parameters
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Burial Bandit"

# Performance logging
PERF_LOG_FPS = False

# Physics
GRAVITY = 0.5

# PLAYER
LAYER_NAME_PLAYER = "Player"

# Movement speed
PLAYER_MOVEMENT_SPEED = 7
PLAYER_JUMP_SPEED = 13

# The number of lives the player
# has at the start of the game.
PLAYER_INITIAL_LIVES = 3

# Player size
PLAYER_SCALING = 5

# How close you need to be to a checkpoint to activate it.
CHECKPOINT_TRIGGER_DISTANCE = 64

# The number of pixels distance from the absolute ends
# of the map that the player will be stopped at.
PLAYER_X_STOP_BUFFER = 64

# GUI
GUI_MAIN_FONT_SIZE = 20

# LEVELS
LEVELS = [
    'maps/1_TownLevel.tmx',
    'maps/2_JungleLevel.tmx',
    'maps/3_CaveLevel.tmx',
]

# Map scale values by level
MAP_SCALE = [
    3,
    5,
    4,
]

# The first map that is opened (usually the start).
MAP_START_INDEX = 0

# Used to enable the End scene logic.
FINAL_MAP_INDEX = 2

# Layer Names from the tiled project
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_PICKUPS = "Pickups"
LAYER_NAME_FOREGROUND = "Foreground"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_DONT_TOUCH = "Don't Touch"
LAYER_NAME_NEXT_LEVEL = "Next Level"
LAYER_NAME_LADDERS = "Ladders"
LAYER_NAME_CHECKPOINTS = "Checkpoints"
LAYER_NAME_SOUND = "Sound"


class TheGame(arcade.Window):
    """
    The main window class for the Burial Bandit game.

    Runs the game after running the `setup()` method
    and calling `arcade.run()`.
    """

    # Tiled map data
    tile_map: arcade.TileMap = None
    # The arcade scene for all data from the tiled map.
    scene: arcade.Scene = None
    physics_engine = None

    # Holds all the sounds in the game in a dictionary.
    sounds: Dict[str, arcade.Sound] = {}
    # Holds the player for the background soundtrack.
    looping_song = None

    # Holds the player Sprite object
    player_sprite: arcade.Sprite = None

    # Cameras
    camera: arcade.Camera = None
    gui_camera: arcade.Camera = None

    # Holds the current input values
    inputs: Inputs = None

    # This object handles the unique effects
    # done in the game finale action sequence.
    end_sequence: EndSequence = None

    # Level index
    current_level_index: int = MAP_START_INDEX

    # Current checkpoint
    player_checkpoint_pos: arcade.Point = None
    player_checkpoint_index: int = 0

    # Map width in game px
    map_width_px = 0

    # GAMEPLAY
    # Keys
    keys_picked_up: int = 0
    keys_to_pick_up: int = 0

    # Lives
    lives: int = 0

    def __init__(self) -> None:

        # Create the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT,
                         SCREEN_TITLE, fullscreen=False)

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
        self.tile_map = arcade.load_tilemap(
            map_name,
            MAP_SCALE[self.current_level_index],
            layer_options
            )

        # Convert Tiled map to a arcade scene with SpriteLists for each layer.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Set the background color from the map file.
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Get the player start location from the tiled map file.
        # This is done by just going to the first checkpoint.
        self.player_checkpoint_index = 0
        self.player_checkpoint_pos = (self.tile_map.object_lists
                                      [LAYER_NAME_CHECKPOINTS]
                                      [self.player_checkpoint_index].shape)

        self.map_width_px = (
            self.tile_map.width *
            self.tile_map.tile_width *
            MAP_SCALE[self.current_level_index])
        # END MAP LOAD

        # LOAD SOUNDS
        self.sounds = {
            # Key pickup sound
            'keys_on_surface': arcade.load_sound(
                'assets/Audio/keys_on_surface_zapsplat.mp3'),

            # Looping game soundtrack
            'through_the_forest': arcade.load_sound(
                'assets/Audio/madmakingmistery_ttf.wav', True),

            # These sound effects are played when walking on surfaces.
            'grass_surface': arcade.load_sound(
                'assets/Audio/footsteps-in-grass-moderate-A-fesliyanstudios.mp3'),
            'stone_surface': arcade.load_sound(
                'assets/Audio/dress-shoes-on-Concrete-Floor-fast-pace-FesliyanStudios.mp3'),

            # End sequence
            'end_intro': arcade.load_sound(
                'assets/Audio/EndSequence_Intro.mp3'),
            'end_loop': arcade.load_sound(
                'assets/Audio/EndSequence_Looping.mp3')
        }

        # Hack to prevent lag spikes when playing
        # the sounds for the first time.
        for sound in self.sounds.values():
            sound.stop(sound.play(0))
        # END LOAD SOUNDS

        # CREATE PLAYER CHARACTER
        # Create the list for the player sprites
        self.scene.add_sprite_list(LAYER_NAME_PLAYER)
        # Put in front of the BG so the
        # player is not hidden incorrectly.
        self.scene.add_sprite_list_before(LAYER_NAME_PLAYER,
                                          LAYER_NAME_FOREGROUND)

        # Make the player character object and
        # place them at the start of the level.
        self.player_sprite = player.PlayerCharacter(PLAYER_SCALING,
                                                    self.sounds)
        self.player_sprite.center_x = self.player_checkpoint_pos[0]
        self.player_sprite.center_y = self.player_checkpoint_pos[1]
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
        self.camera = camera.GameCamera()
        # Set it's start location to where the player is
        # instantly, so that it doesn't drift to the start.
        self.camera.camera_to_player(self.player_sprite, 1)
        self.camera.update()

        # Static camera for the User Interface and
        # Heads Up Display elements, so they stay
        # in the same place on the screen.
        self.gui_camera = arcade.Camera()

        # PERFORMANCE MEASUREMENT
        # Needed to get the game framerate.
        if PERF_LOG_FPS:
            arcade.enable_timings()
        # END PERFORMANCE MEASUREMENT

        # GAMEPLAY VALUES
        # Set Keys picked up to none.
        self.keys_picked_up = 0
        # Get the number of keys placed on the pickup layer.
        self.keys_to_pick_up = len(self.scene[LAYER_NAME_PICKUPS])

        # Set lives to the max value
        self.lives = PLAYER_INITIAL_LIVES
        # END GAMEPLAY VALUES

        # Setup end sequence for last (3rd) level.
        # The end sequence has a lot of fancy animation stuff,
        # so it is kept seperate, with the sounds and camera shared.
        if self.current_level_index == FINAL_MAP_INDEX:
            self.end_sequence = EndSequence(
                self.sounds,
                self.camera,
                self.scene,
                self.player_sprite
            )

        # MUSIC
        # It plays the background music at start
        # and stops it on the final level.
        if (self.current_level_index != FINAL_MAP_INDEX and
                self.looping_song is None):
            self.looping_song = (self.sounds['through_the_forest']
                                 .play(.4, loop=True))
        elif (self.looping_song is not None and
                self.current_level_index == FINAL_MAP_INDEX):
            arcade.stop_sound(self.looping_song)

    def on_update(self, delta_time):
        """Movement and game logic"""

        self.stop_player_at_ends()

        # Move the player with the physics engine.
        self.physics_engine.update()

        # Update player animation
        self.player_sprite.update_animation(delta_time)
        self.player_sprite.update_sfx(self.scene[LAYER_NAME_SOUND])

        # Check if the player hits something deadly.
        self.check_for_deadly_surfaces()

        # Check if the player picked up a key.
        self.check_for_pickup_collision()

        self.check_for_next_level()

        self.update_checkpoints()

        if self.end_sequence is not None:
            self.end_sequence.on_update(delta_time)

    def on_draw(self):
        """Render the screen."""
        self.clear()

        # DRAW GAME WORLD
        self.camera.camera_to_player(self.player_sprite)
        self.camera.use()

        # Animate the pickups like keys and gems.
        self.scene[LAYER_NAME_PICKUPS].update_animation()

        # Draw with nearest pixel sampling to get that pixelated look.
        self.scene.draw(filter=arcade.gl.NEAREST)

        # DRAW GUI
        self.gui_camera.use()

        # Draw health counter in the top left of the screen.
        arcade.draw_text(
            f"Lives {self.lives}/{PLAYER_INITIAL_LIVES}",
            32, self.height - 32,
            arcade.color.ROSE_RED,
            GUI_MAIN_FONT_SIZE,
            anchor_y="top"
        )

        # Log the framerate of the game
        # to help diagnose performance issues.
        if PERF_LOG_FPS:
            print(arcade.get_fps())

    def check_for_deadly_surfaces(self):
        """Check if the player hits something damaging"""
        if arcade.check_for_collision_with_list(
            self.player_sprite,
            self.scene[LAYER_NAME_DONT_TOUCH]
        ):
            # Take a life
            self.lives -= 1

            # If the player has lives remaining.
            if self.lives > 0:
                # Send player back to checkpoint
                self.player_sprite.change_x = 0
                self.player_sprite.change_y = 0
                self.player_sprite.center_x = self.player_checkpoint_pos[0]
                self.player_sprite.center_y = self.player_checkpoint_pos[1]
            # If the player is out of lives.
            else:
                # Restart the level.
                self.setup()

    def check_for_pickup_collision(self):
        """Collect keys when the player walks into them."""

        # See if we hit any keys
        pickup_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_PICKUPS]
        )

        if len(pickup_hit_list) > 0:
            self.sounds['keys_on_surface'].play()
            # Start end sequence
            if self.current_level_index == FINAL_MAP_INDEX:
                self.end_sequence.start()

        # Loop through each key we hit (if any) and remove it
        for pickup in pickup_hit_list:
            # Remove the coin
            pickup.remove_from_sprite_lists()
            # Add to the key counter
            self.keys_picked_up += 1

    def check_for_next_level(self):
        """When the player reaches the end of the level,
        load the next one."""

        if arcade.check_for_collision_with_list(
            self.player_sprite,
            self.scene[LAYER_NAME_NEXT_LEVEL]
        ) and self.keys_picked_up >= self.keys_to_pick_up:
            self.keys_picked_up = 0
            self.player_sprite.stop_sfx()
            if len(LEVELS)-1 > self.current_level_index:
                self.current_level_index += 1
            self.setup()

    def update_checkpoints(self):
        """
        When the player comes within proximity of one of the
        checkpoints and it is of a higher index then the previous
        one they activated, that will become their new checkpoint.
        """
        checkpoints = self.tile_map.object_lists[LAYER_NAME_CHECKPOINTS]
        for checkpoint_index, tiled_object in enumerate(checkpoints):
            checkpoint_location: arcade.Shape = tiled_object.shape
            # Checks the player is both close enough to the checkpoint
            # and has not already obtained a further progressed checkpoint.
            if arcade.get_distance(
                self.player_sprite.center_x, self.player_sprite.center_y,
                checkpoint_location[0], checkpoint_location[1]
            ) <= CHECKPOINT_TRIGGER_DISTANCE and (
                    checkpoint_index > self.player_checkpoint_index):
                # Set the checkpoint location to
                # the newly reached checkpoint.
                self.player_checkpoint_index = checkpoint_index
                self.player_checkpoint_pos = checkpoint_location

    def stop_player_at_ends(self):
        """
        Stop the player walking off the ends of the level.
        Call this before the physics update.
        """
        # Where the player will be on the next
        # physics update if the change goes ahead.
        anticipated_position = (self.player_sprite.center_x +
                                self.player_sprite.change_x)
        # Stop the player at the left side of the map.
        if (self.inputs.left_pressed and
                anticipated_position <= PLAYER_X_STOP_BUFFER):
            self.player_sprite.change_x = 0
        # Stop the player on the right side of the map.
        elif (self.inputs.right_pressed and anticipated_position >=
              self.map_width_px - PLAYER_X_STOP_BUFFER):
            self.player_sprite.change_x = 0

    def process_keychange(self):
        """
        Updates the input's impact on gameplay.
        """
        # Process jumping and moving up/down ladders.
        if self.inputs.up_pressed and not self.inputs.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif (
                self.physics_engine.can_jump(y_distance=10)
                and not self.inputs.jump_needs_reset
            ):
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.inputs.jump_needs_reset = True
                # arcade.play_sound(self.jump_sound)
        elif self.inputs.down_pressed and not self.inputs.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

        # Cancel out movement on ladders when
        # both up and down are pressed.
        if self.physics_engine.is_on_ladder():
            if not self.inputs.up_pressed and not self.inputs.down_pressed:
                self.player_sprite.change_y = 0
            elif self.inputs.up_pressed and self.inputs.down_pressed:
                self.player_sprite.change_y = 0

        # Walking laft and right.
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
