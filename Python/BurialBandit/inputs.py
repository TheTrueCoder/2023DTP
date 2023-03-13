import arcade
from dataclasses import dataclass

@dataclass
class Inputs():
    left_pressed: bool = False
    right_pressed: bool = False
    up_pressed: bool = False
    down_pressed: bool = False
    jump_needs_reset: bool = False