"""
Turns motor speeds into robot movement: driving toward an angle, spinning
in place, and stopping. Built on top of motors.py.
"""

import math
import motors
import vision
from value_config import ValueConfig

MAX_SPEED = 100000000
SLOW_SPEED = int(MAX_SPEED * 0.1)


def move_to_ball(ball_angle, ball_dist, goal_angle, speed=MAX_SPEED):
    """
    Drives the robot toward `ball_angle` (0 = the direction the camera faces),
    using trig to work out how fast each of the 4 wheels needs to spin.
    """
    speed_factor = ball_dist / ValueConfig.chase_speed_factor
    speed = int(speed * speed_factor)

    rotation_speed_factor = min(1.0, abs(goal_angle) / ValueConfig.rotation_full_speed_angle)
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
    ball_to_goal_distance = math.hypot(vision.goalx_pos - vision.ballx_pos, vision.goaly_pos - vision.bally_pos)
    unit_x = (vision.goalx_pos - vision.ballx_pos) / ball_to_goal_distance if ball_to_goal_distance != 0 else 0
    unit_y = (vision.goaly_pos - vision.bally_pos) / ball_to_goal_distance if ball_to_goal_distance != 0 else 0

    target_x = vision.ballx_pos - unit_x * ValueConfig.orbit_distance_threshold
    target_y = vision.bally_pos - unit_y * ValueConfig.orbit_distance_threshold

    desired_bearing = math.degrees(math.atan2(target_x - vision.ballx_pos, target_y - vision.bally_pos)) % 360
    current_bearing = math.degrees(math.atan2(0 - vision.ballx_pos, 0 - vision.bally_pos)) % 360
    normalised_bearing_error = (desired_bearing - current_bearing + 180) % 360 - 180

    offset = ball_angle - 90 if normalised_bearing_error > 0 else ball_angle + 90

    move_speed_factor = ball_dist / ValueConfig.chase_speed_factor
    move_speed = int(speed * move_speed_factor * 0.4)

    orbit_speed_factor = min(1.0, abs(normalised_bearing_error) / ValueConfig.orbit_full_speed_angle)
    orbit_speed = int(speed * orbit_speed_factor * 0.4)

    is_possession = (ball_dist < ValueConfig.orbit_distance_threshold 
                     and abs(goal_angle) < ValueConfig.goal_angle_tolerance
                     and abs(ball_angle) < ValueConfig.ball_angle_tolerance)

    if is_possession:
        move_to_ball(ball_angle, ball_dist, goal_angle, speed)
    elif ball_dist < ValueConfig.orbit_distance_threshold:
        move_to_ball(offset, ball_dist, goal_angle, orbit_speed)
        print('orbiting around the ball')
    else:
        move_to_ball(ball_angle, ball_dist, goal_angle, move_speed)
        print('moving toward the ball')