"""
Handles the ending action sequence for Burial Bandit.
"""


from typing import Dict
import arcade
from pyglet.math import Vec2

SHAKE_FREQUENCY_SECS = 0.15
SHAKE_MAGNITUDE = 5
SHAKE_SPEED = 0.5
SHAKE_DAMPING = 0.9

LOOP_START_WAIT_SECS = 14

DESTRUCTION_AUDIO_VOLUME = 2

LAYER_NAME_END_TRIGGER = "EndTrigger"


class EndSequence():
    """Does the fancy stuff for the final game sequence."""
    lapsed_time = 0.0

    is_active = False

    sounds = None
    camera = None
    scene = None
    player = None

    # Players
    loop_player = None
    # Records the time since the corrosponding event was last performed.
    last_shake_time = 0

    def __init__(self, sound_library: Dict[str, arcade.Sound],
                 camera: arcade.Camera,
                 scene: arcade.Scene,
                 player: arcade.Sprite) -> None:
        self.sounds = sound_library
        self.camera = camera
        self.scene = scene
        self.player = player

    def start(self):
        """
        Start the action sequence.
        """
        self.is_active = True
        self.sounds['end_intro'].play(DESTRUCTION_AUDIO_VOLUME)

    def stop(self):
        """
        End the action sequence.
        """
        self.is_active = False
        if self.loop_player is not None:
            arcade.stop_sound(self.loop_player)

    def on_update(self, delta_time=1/60):
        """
        Called in the main on_update function to play the
        sequence of events for the final action sequence.
        """

        if self.is_active:
            self.lapsed_time += delta_time
            # print(self.lapsed_time)

            # Play the looping section after the intro.
            if (self.lapsed_time >= LOOP_START_WAIT_SECS and
                    self.loop_player is None):
                self.loop_player = self.sounds['end_loop'].play(
                    DESTRUCTION_AUDIO_VOLUME,
                    loop=True
                    )

            # Shake the camera every SHAKE_FREQUENCY_SECS seconds.
            if self.lapsed_time - self.last_shake_time >= SHAKE_FREQUENCY_SECS:
                start_velocity = arcade.rand_on_circle(
                    (0, 0),
                    SHAKE_MAGNITUDE
                )
                self.camera.shake(
                    Vec2(start_velocity[0], start_velocity[1]),
                    SHAKE_SPEED,
                    SHAKE_DAMPING
                )

                self.last_shake_time = self.lapsed_time

            if arcade.check_for_collision_with_list(
                self.player,
                self.scene[LAYER_NAME_END_TRIGGER]
            ):
                self.stop()
