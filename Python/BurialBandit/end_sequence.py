from typing import Dict
import arcade

SHAKE_FREQUENCY_SECS = 3
SHAKE_MAGNITUDE = 16
SHAKE_SPEED = 1.5
SHAKE_DAMPING = 0.9

LOOP_START_WAIT_SECS = 14

DESTRUCTION_AUDIO_VOLUME = 2

class EndSequence():
    """Does the fancy stuff for the final game sequence."""
    lapsed_time = 0.0

    is_active = False

    sounds = None
    camera = None

    # Players
    loop_player = None
    # Records the time since the corrosponding event was last performed.
    last_shake_time = 0

    def __init__(self, sound_library: Dict[str, arcade.Sound],
        camera: arcade.Camera) -> None:
        self.sounds = sound_library
        self.camera = camera

    def start(self):
        self.is_active = True
        self.sounds['end_intro'].play(DESTRUCTION_AUDIO_VOLUME)

    def on_update(self, delta_time = 1/60):
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
            # if self.lapsed_time - self.last_shake_time >= SHAKE_FREQUENCY_SECS:
            #     self.camera.shake(
            #         arcade.rand_on_circle(
            #             arcade.Vector((0, 0)),
            #             SHAKE_MAGNITUDE
            #         ),
            #         SHAKE_SPEED,
            #         SHAKE_DAMPING
            #     )