import arcade
from typing import Dict

class EndSequence():
    """Does the fancy stuff for the final game sequence."""
    lapsed_time = 0.0

    is_active = False

    sounds = None
    camera = None

    def __init__(self, sound_library: Dict[str, arcade.Sound],
        camera: arcade.Camera) -> None:
        self.sounds = sound_library
        self.camera = camera

    def start(self):
        self.is_active = True
        self.sounds['end_intro'].play()

    def update(self, delta_time = 1/60):
        self.lapsed_time += delta_time