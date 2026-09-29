from dataclasses import dataclass

@dataclass
class ValueConfig:
    """A dataclass to hold configuration values for the Picobot."""
    move_distance_factor: int = 540
    orbit_distance_threshold: float = 360
    orbit_full_speed_angle: int = 45