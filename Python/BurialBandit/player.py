"""
The player character for Burial Bandit
including animations and sound effects.
"""

from typing import List, Dict
from os.path import join
from math import floor
import arcade
from pyglet.media import Player

# ANIMATION_FRAMERATE = 8

# Animation metadata
ANIMATIONS_METADATA = {
    'idle': {
        'folder': "assets/Archeologist-Character/Animations/Idle",
        'length': 8,
        'wait': 8,
        'framerate': 4,
    },
    'running': {
        'folder': "assets/Archeologist-Character/Animations/Running",
        'length': 8,
        'wait': 0,
        'framerate': 10,
    }
}

# Names to refer to the different animations.
ANIM_IDLE = "idle"
ANIM_RUNNING = "running"

# Custom property keys
PROPERTY_GROUND_TYPE = "ground_type"

# Name the values that represent left and right facing.
RIGHT_FACING = 0
LEFT_FACING = 1


def load_image_sequence(folder: str, number_of_frames: int,
                        start_frame: int = 1,
                        file_extension=".png") -> List[List[arcade.Sprite]]:
    """
    Loads a sequence of images as texture pairs into a list
    to be used for animation.
    The images must be consecutively named e.g. 1.png, 2.png, 3.png, ...
    """
    image_sequence: List[List[arcade.Sprite]] = []
    for frame_no in range(start_frame, number_of_frames + 1):
        # Generate filepath for the next image to import.
        filepath = join(folder, str(frame_no) + file_extension)

        # Import the next image in the sequence
        # and append it to the list.
        image_sequence.append(
            arcade.load_texture_pair(filepath)
        )

    return image_sequence


class PlayerCharacter(arcade.Sprite):
    """The player's character."""

    # Track player state
    jumping = False
    climbing = False
    is_on_ladder = False
    facing_direction = RIGHT_FACING

    # Increases every frame proportional to delta time.
    current_frame = 0.0
    # Current frame index
    sequence_frame = 0
    # The animation that is played
    current_animation = ANIM_IDLE
    # The animation played the previous frame.
    # Used to determine if the animation has changed,
    # and to reset the frame if so.
    previous_animation = ANIM_IDLE
    animations = {}

    # Audio
    sounds = None
    surface_sfx_player: Player = None
    previous_ground_type: str = None

    def __init__(self,
                 character_scaling: int = 1,
                 sound_library: Dict[str, arcade.Sound] = {}):
        # Initialise the parent
        super().__init__(scale=character_scaling)

        # Save sounds
        self.sounds = sound_library

        # LOAD ANIMATIONS
        for anim_name, anim_data in ANIMATIONS_METADATA.items():
            self.animations[anim_name] = load_image_sequence(
                anim_data['folder'], anim_data['length'])

        # Set initial sprite
        self.texture = self.animations[ANIM_IDLE][0][self.facing_direction]

    def animation_selection(self):
        """
        Rules to select which animation to play.
        """

        # Idle
        if self.change_x == 0:
            self.current_animation = ANIM_IDLE
        # Running
        else:
            self.current_animation = ANIM_RUNNING

        # If the animation has changed, reset the frame to zero
        if self.current_animation != self.previous_animation:
            self.current_frame = 0.0
            self.sequence_frame = 0

        self.previous_animation = self.current_animation

    def update_animation(self, delta_time: float = 1 / 60):
        """
        Updates the animation state of the player,
        accounting for the passed time.

        delta_time: Time passed since last frame.
        """

        # Flip the character to face the direction they're walking.
        if self.change_x < 0:
            self.facing_direction = LEFT_FACING
        elif self.change_x > 0:
            self.facing_direction = RIGHT_FACING

        # Select the animation
        self.animation_selection()

        # Get animation attributes
        animation_frames = (ANIMATIONS_METADATA
                            [self.current_animation]['length'] - 1)
        wait_frames = ANIMATIONS_METADATA[self.current_animation]['wait']
        framerate = ANIMATIONS_METADATA[self.current_animation]['framerate']

        # Progress the animation frame unless
        # it's the last one in the animation.
        seq_frame = floor(self.current_frame)
        if seq_frame < animation_frames:
            self.sequence_frame = seq_frame

        # When the time for the full animation and
        # the wait time has passed, restart the animation.
        if self.current_frame >= animation_frames + wait_frames:
            self.current_frame = 0.0
            self.sequence_frame = 0

        # Play current animation frame.
        self.texture = (self.animations
                        [self.current_animation]
                        [self.sequence_frame]
                        [self.facing_direction])
        # Progress to the next frame
        self.current_frame += delta_time * framerate

    def update_sfx(self, sound_layer: arcade.SpriteList):
        """
        Play a sound effect corresponding
        to the surface the player is walking on.
        """
        # Find the tiles that the player is standing on.
        tiles_touching = arcade.check_for_collision_with_list(
            self, sound_layer
        )

        if len(tiles_touching) == 0 or self.change_x == 0:
            if self.surface_sfx_player is not None:
                arcade.stop_sound(self.surface_sfx_player)
            self.previous_ground_type = None
        else:
            ground_type: str = (tiles_touching[0]
                                .properties[PROPERTY_GROUND_TYPE])
            if ground_type != self.previous_ground_type:
                if self.surface_sfx_player is not None:
                    arcade.stop_sound(self.surface_sfx_player)
                self.surface_sfx_player = (
                    self.sounds[f"{ground_type}_surface"].play(volume=0.7,
                                                               loop=True)
                )
            self.previous_ground_type = ground_type

    def stop_sfx(self):
        """Stop playing player sound effects."""
        arcade.stop_sound(self.surface_sfx_player)
