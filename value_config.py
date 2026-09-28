from dataclasses import dataclass

@dataclass
class ValueConfig:
    """A dataclass to hold configuration values for the Picobot."""
    orbit_distance_threshold: float = 170