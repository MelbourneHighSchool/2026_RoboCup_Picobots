from dataclasses import dataclass

@dataclass
class ValueConfig:
    """A dataclass to hold configuration values for the Picobot."""
    orbit_distance_threshold: float = 320
    move_distance_factor: float = orbit_distance_threshold * 1.2
    orbit_full_speed_angle: int = 45