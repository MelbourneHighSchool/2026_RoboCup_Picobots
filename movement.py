"""
Turns motor speeds into robot movement: driving toward an angle, spinning
in place, and stopping. Built on top of motors.py.
"""

import math
import motors
from value_config import ValueConfig

MAX_SPEED = 100000000
SLOW_SPEED = int(MAX_SPEED * 0.1)


def move_to_ball(ball_angle, ball_dist, goal_angle, speed=MAX_SPEED):
    """
    Drives the robot toward `ball_angle` (0 = the direction the camera faces),
    using trig to work out how fast each of the 4 wheels needs to spin.
    """
    speed_factor = ball_dist / ValueConfig.move_distance_factor
    speed = int(speed * speed_factor)

    rotation_speed_factor = min(1.0, abs(goal_angle) / ValueConfig.orbit_angle_tolerance)
    rotation_speed = int((speed * rotation_speed_factor if goal_angle < 0 else -speed * rotation_speed_factor) * 0.4)
    
    angle_rad = math.radians(ball_angle + 90)
    x = math.floor(math.cos(angle_rad) * speed)
    y = math.floor(math.sin(angle_rad) * speed)
    motors.drivers[0].set_speed(y + x + rotation_speed)       # FR
    motors.drivers[1].set_speed(y - x + rotation_speed)       # BR
    motors.drivers[2].set_speed(-(y + x) + rotation_speed)    # BL
    motors.drivers[3].set_speed(-(y - x) + rotation_speed)    # FL


def spin(speed):
    """Spins the robot in place (used when the ball isn't visible)."""
    for driver in motors.drivers:
        driver.set_speed(speed)


def stop():
    """Stops all 4 motors."""
    for driver in motors.drivers:
        driver.set_speed(0)


def orbit_around(ball_angle, ball_dist, goal_angle, speed=MAX_SPEED):
    offset = ball_angle - 90 if ball_angle < 0 else ball_angle + 90

    move_speed_factor = ball_dist / ValueConfig.move_distance_factor
    move_speed = int(speed * move_speed_factor)

    orbit_speed_factor = min(1.0, abs(ball_angle) / ValueConfig.orbit_full_speed_angle)
    orbit_speed = int(speed * orbit_speed_factor)

    is_possession = (ball_dist < ValueConfig.orbit_distance_threshold 
                     and abs(goal_angle) < ValueConfig.orbit_angle_tolerance
                     and abs(ball_angle) < ValueConfig.ball_angle_tolerance)

    if is_possession:
        stop()
    elif ball_dist < ValueConfig.orbit_distance_threshold:
        move_to_ball(offset, ball_dist, goal_angle, orbit_speed)
        print('orbiting around the ball')
    else:
        move_to_ball(ball_angle, ball_dist, goal_angle, move_speed)
        print('moving toward the ball')