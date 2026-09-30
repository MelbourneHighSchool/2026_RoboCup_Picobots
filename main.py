"""Main loop: streams the camera and chases the ball."""

import asyncio
import signal
import sys
import cv2
import websockets
import motors
import movement
import vision

# Smaller stream = less lag over WiFi
STREAM_WIDTH = 640
STREAM_JPEG_QUALITY = 70  # 0-100

# Ball can hide under the front plate when it's close.
# If it vanishes while this big, wiggle left/right to find it before spinning.
BLIND_SPOT_AREA_THRESHOLD = 6000  # tune with area= on camera.html
BLIND_SPOT_NUDGE_ANGLE = 35  # degrees
BLIND_SPOT_NUDGE_SPEED = int(movement.MAX_SPEED * 0.35)
BLIND_SPOT_SWITCH_TICKS = 15  # ~0.3s per side
BLIND_SPOT_MAX_TICKS = 100  # ~2s, then spin

# Open browser tabs
clients = set()


async def ws_handler(ws):
    """Track browser tabs."""
    clients.add(ws)
    print("Browser connected")
    try:
        await ws.wait_closed()
    finally:
        clients.remove(ws)


async def stream_cam(picam, lower_orange, upper_orange, lower_yellow, upper_yellow):
    """Find the ball and send each frame to the browser."""
    while True:
        frame = vision.read_frame(picam)
        frame = vision.detect_ball(frame, lower_orange, upper_orange)
        frame = vision.detect_goal(frame, lower_yellow, upper_yellow)

        # Only shrink the copy we send
        stream_height = int(frame.shape[0] * STREAM_WIDTH / frame.shape[1])
        preview = cv2.resize(frame, (STREAM_WIDTH, stream_height))

        encode_params = [cv2.IMWRITE_JPEG_QUALITY, STREAM_JPEG_QUALITY]
        success, image_data = cv2.imencode(".jpg", preview, encode_params)
        if success and clients:
            jpg = image_data.tobytes()
            await asyncio.gather(*[client.send(jpg) for client in clients])

        await asyncio.sleep(0.03)


async def motor_task():
    """Chase the ball, check the blind spot if it vanishes up close, otherwise spin."""
    blind_spot_ticks_left = 0
    ticks_in_recovery = 0
    nudge_toward_left = True
    was_visible = False

    while True:
        if vision.ball_visible:
            movement.orbit_around(vision.normalised_ball_angle, vision.ball_dist, vision.normalised_goal_angle, speed=movement.MAX_SPEED)
            print('ball is visible')
            print(f'ball angle: {vision.normalised_ball_angle}, ball distance: {vision.ball_dist}')
            # print(f'ballx: {vision.ballx_pos}, bally: {vision.bally_pos}')
            print(f'goal angle: {vision.normalised_goal_angle}, goal distance: {vision.goal_dist}')
            # print(f'goalx: {vision.goalx_pos}, goaly: {vision.goaly_pos}')
            blind_spot_ticks_left = 0

        else:
            movement.spin(movement.SLOW_SPEED)
            print('ball is not visible')

        was_visible = vision.ball_visible
        await asyncio.sleep(0.02)


async def main():
    motors.setup_motors()
    picam, lower_orange, upper_orange, lower_yellow, upper_yellow = vision.setup_camera()

    # Frames are already JPEGs, no point compressing again
    server = await websockets.serve(ws_handler, "0.0.0.0", 8765, compression=None)
    print("Streaming on port 8765, open camera.html")
    print("Ctrl+C to stop")

    await asyncio.gather(   
        stream_cam(picam, lower_orange, upper_orange, lower_yellow, upper_yellow),
        motor_task(),
    )
    await server.wait_closed()


def shutdown(sig, frame):
    print("\nShutting down...")
    movement.stop()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown)
    asyncio.run(main())
