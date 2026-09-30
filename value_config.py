from dataclasses import dataclass

@dataclass
class ValueConfig:
    """A dataclass to hold configuration values for the Picobot."""
    orbit_distance_threshold: float = 320
    chase_speed_factor: float = orbit_distance_threshold * 1.2

    orbit_full_speed_angle: int = 40
    rotation_full_speed_angle: int = 20

    goal_angle_tolerance: int = 15
    ball_angle_tolerance: int = 12