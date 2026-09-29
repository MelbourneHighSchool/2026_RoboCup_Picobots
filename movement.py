"""
Turns motor speeds into robot movement: driving toward an angle, spinning
in place, and stopping. Built on top of motors.py.
"""

import math
import motors
from value_config import ValueConfig

MAX_SPEED = 100000000
SLOW_SPEED = MAX_SPEED // 10


def move_to_ball(ball_angle, speed=MAX_SPEED):
    """
    Drives the robot toward `degree` (0 = the direction the camera faces),
    using trig to work out how fast each of the 4 wheels needs to spin.
    """    
    angle_rad = math.radians(ball_angle + 90)
    x = math.floor(math.cos(angle_rad) * speed)
    y = math.floor(math.sin(angle_rad) * speed)
    motors.drivers[0].set_speed(y + x)       # FR
    motors.drivers[1].set_speed(y - x)       # BR
    motors.drivers[2].set_speed(-(y + x))    # BL
    motors.drivers[3].set_speed(-(y - x))    # FL


def spin(speed=SLOW_SPEED):
    """Spins the robot in place (used when the ball isn't visible)."""
    for driver in motors.drivers:
        driver.set_speed(speed)


def stop():
    """Stops all 4 motors."""
    for driver in motors.drivers:
        driver.set_speed(0)


def orbit_around(degree, ball_distance, speed=MAX_SPEED):
    offset = degree - 90 if degree < 0 else degree + 90

    move_speed_factor = ball_distance / ValueConfig.move_distance_factor
    print(f'move_speed_factor: {move_speed_factor}')
    move_speed = int(speed * move_speed_factor)

    orbit_speed_factor = min(0.6, abs(degree) / ValueConfig.orbit_full_speed_angle)
    print (f'orbit_speed_factor: {orbit_speed_factor}')
    orbit_speed = int(speed * orbit_speed_factor)

    if ball_distance < ValueConfig.orbit_distance_threshold:
        move_to_ball(offset, orbit_speed)
        print('orbiting around the ball')
    else:
        move_to_ball(degree, move_speed)
        print('moving toward the ball')