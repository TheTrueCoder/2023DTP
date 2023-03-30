from dataclasses import dataclass


@dataclass
class Inputs():
    """
    Stores the input actions derived from the user's keyboard inputs.
    """

    left_pressed: bool = False
    right_pressed: bool = False
    up_pressed: bool = False
    down_pressed: bool = False
    jump_needs_reset: bool = False
