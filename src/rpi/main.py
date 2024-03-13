#!/bin/python
import adafruit_bno055
import asyncio
import board
from motors import Motors
from ms5837 import MS5837_02BA
import websockets
from ws_server import WSServer
from pid import PID

# how far the joystick needs to be moved before stabilization is temporarily
# disabled (0..1)
DESTABLE_THRESH = 0.5


async def main_server():
    motors = Motors()

    try:
        depth_sensor = MS5837_02BA(1)
        depth_sensor.init()
    except OSError:
        print("Unable to connect to depth sensor!")
        depth_sensor = None
    try:
        imu = adafruit_bno055.BNO055_I2C(board.I2C())
    except OSError:
        print("Unable to connect IMU!")
        imu = None

    vertical_anchor = False
    # adjust the y-velocity to have the ROV remain at a constant depth
    # TODO - Likely need to re-tune the PID parameters
    vertical_pid = PID(
        proportional_gain=2, integral_gain=0.05, derivative_gain=0.01
    )

    yaw_anchor = False
    # adjust the yaw velocity to keep the ROV stable
    # TODO - Need to tune the PID parameters
    yaw_pid = PID(proportional_gain=0, integral_gain=0, derivative_gain=0)

    roll_anchor = False
    # adjust the roll velocity to keep the ROV stable
    roll_pid = PID(
        proportional_gain=0.025, integral_gain=0.001, derivative_gain=0.0e-4
    )

    pitch_anchor = False
    # adjust the pitch velocity to keep the ROV stable
    # TODO - Need to tune the PID parameters
    pitch_pid = PID(proportional_gain=0, integral_gain=0, derivative_gain=0)

    # multiplier for velocity to set speed limit
    speed_factor = 1

    # lock the controls in a certain state to allow for "autonomous" docking
    motor_lock = False

    locked_velocities = {
        "x_velocity": 0,
        "y_velocity": 0,
        "z_velocity": 0,
        "yaw_velocity": 0,
        "pitch_velocity": 0,
        "roll_velocity": 0,
    }

    # stores the last button press of the velocity toggle button
    prev_speed_toggle = None
    prev_vertical_anchor_toggle = None
    prev_roll_anchor_toggle = None
    prev_pitch_anchor_toggle = None
    prev_yaw_anchor_toggle = None
    prev_motor_lock_toggle = None

    prev_z_velocity = 0

    print("Server started!")
    while True:
        joystick_data = WSServer.pump_joystick_data()
        if depth_sensor is not None:
            depth_sensor.read()

        # if a joystick client hasn't connected yet
        if not joystick_data:
            await asyncio.sleep(0.01)
            continue

        #  print(f"Depth: {depth_sensor.depth() * 100:2f}cm")
        #  print(imu.euler[0])
        #  print(imu.euler[1])
        #  print(imu.euler[2])
        x_velocity = joystick_data["right_stick"][0] * speed_factor
        y_velocity = joystick_data["left_stick"][1] * speed_factor
        z_velocity = joystick_data["right_stick"][1] * speed_factor
        yaw_velocity = joystick_data["left_stick"][0] * speed_factor
        pitch_velocity = joystick_data["dpad"][1] * speed_factor
        roll_velocity = joystick_data["dpad"][0] * speed_factor
        speed_toggle = (
            joystick_data["buttons"]["right_bumper"]
            - joystick_data["buttons"]["left_bumper"]
        )
        vertical_anchor_toggle = joystick_data["buttons"]["north"]
        roll_anchor_toggle = joystick_data["buttons"]["east"]
        pitch_anchor_toggle = joystick_data["buttons"]["south"]
        yaw_anchor_toggle = joystick_data["buttons"]["west"]
        motor_lock_toggle = joystick_data["buttons"]["start"]

        # re-enable the vertical anchor when the z velocity falls below the
        # threshold
        if (
            vertical_anchor
            and z_velocity < DESTABLE_THRESH
            and prev_z_velocity > DESTABLE_THRESH
        ):
            vertical_pid.update_set_point(depth_sensor.depth())

        # set the z velocity according to the vertical PID controller based on
        # current depth, the vertical anchor should be temporarily disabled
        # when the z velocity is greater than a certain threshold in order to
        # give the pilot control over the depth when the vertical anchor is on
        if (
            vertical_anchor
            and depth_sensor is not None
            and z_velocity < DESTABLE_THRESH
        ):
            z_velocity = vertical_pid.compute(depth_sensor.depth())

        # set the yaw velocity according to the yaw PID controller based on
        # current yaw angle
        if yaw_anchor and imu is not None:
            yaw_angle = imu.euler[1]
            if yaw_angle is not None:
                yaw_velocity = yaw_pid.compute(yaw_angle)

        # set the roll velocity according to the roll PID controller based on
        # current roll angle
        if roll_anchor and imu is not None:
            roll_angle = imu.euler[1]
            if roll_angle is not None:
                roll_velocity = roll_pid.compute(roll_angle)

        # set the pitch velocity according to the pitch PID controller based on
        # current pitch angle
        if pitch_anchor and imu is not None:
            pitch_angle = imu.euler[2]
            if pitch_angle is not None:
                pitch_velocity = pitch_pid.compute(pitch_angle)

        if motor_lock:
            x_velocity = locked_velocities["x_velocity"]
            y_velocity = locked_velocities["y_velocity"]
            z_velocity = locked_velocities["z_velocity"]
            yaw_velocity = locked_velocities["yaw_velocity"]
            pitch_velocity = locked_velocities["pitch_velocity"]
            roll_velocity = locked_velocities["roll_velocity"]

        # run the motors!
        motors.drive_motors(
            x_velocity,
            y_velocity,
            z_velocity,
            yaw_velocity,
            pitch_velocity,
            roll_velocity,
        )

        # increase or decrease speed when the dpad buttons are pressed
        if speed_toggle != prev_speed_toggle:
            # make sure the speed doesn't exceed 1
            if speed_toggle > 0 and speed_factor < 1:
                speed_factor += 0.25
            # make sure the speed doesn't fall below 0.25
            if speed_toggle < 0 and speed_factor >= 0.25:
                speed_factor -= 0.25

            # just in case the speed factor ends up out of range
            if speed_factor > 1:
                speed_factor = 1
            elif speed_factor < 0:
                speed_factor = 0
            print(f"Speed Factor: {speed_factor}")
            prev_speed_toggle = speed_toggle

        # toggle the vertical anchor
        if (
            depth_sensor is not None
            and vertical_anchor_toggle
            and not prev_vertical_anchor_toggle
        ):
            if vertical_anchor:
                print("Vertical anchor disabled!")
                vertical_anchor = False
            elif depth_sensor is not None:
                vertical_anchor = True
                vertical_pid.update_set_point(depth_sensor.depth())
                print(
                    f"Vertical anchor enabled at: {vertical_pid.set_point} m"
                )

        # toggle the yaw anchor
        if (
            imu is not None
            and yaw_anchor_toggle
            and not prev_yaw_anchor_toggle
        ):
            if yaw_anchor:
                print("Pitch anchor disabled!")
            elif depth_sensor is not None:
                yaw_anchor = True
                yaw_pid.update_set_point(imu.euler[2])
                print(f"Pitch anchor enabled at: {yaw_pid.set_point}°")

        # toggle the roll anchor
        if (
            imu is not None
            and roll_anchor_toggle
            and not prev_roll_anchor_toggle
        ):
            if roll_anchor:
                print("Roll anchor disabled!")
                roll_anchor = False
            elif depth_sensor is not None:
                roll_anchor = True
                roll_pid.update_set_point(imu.euler[1])
                print(f"Roll anchor enabled at: {roll_pid.set_point}°")

        # toggle the pitch anchor
        if (
            imu is not None
            and pitch_anchor_toggle
            and not prev_pitch_anchor_toggle
        ):
            if pitch_anchor:
                print("Pitch anchor disabled!")
                pitch_anchor = False
            elif depth_sensor is not None:
                pitch_anchor = True
                pitch_pid.update_set_point(imu.euler[0])
                print(f"Pitch anchor enabled at: {pitch_pid.set_point}°")

        # toggle the motor lock
        if motor_lock_toggle and not prev_motor_lock_toggle:
            if motor_lock:
                motor_lock = False
                print("Motor lock disabled!")
            else:
                motor_lock = True
                locked_velocities["x_velocity"] = x_velocity
                locked_velocities["y_velocity"] = y_velocity
                locked_velocities["z_velocity"] = z_velocity
                locked_velocities["yaw_velocity"] = yaw_velocity
                locked_velocities["pitch_velocity"] = pitch_velocity
                locked_velocities["roll_velocity"] = roll_velocity
                print("Motor lock enabled!")

        prev_vertical_anchor_toggle = vertical_anchor_toggle
        prev_roll_anchor_toggle = roll_anchor_toggle
        prev_motor_lock_toggle = motor_lock_toggle

        await asyncio.sleep(0.01)


def main():
    loop = asyncio.get_event_loop()
    ws_server = websockets.serve(
        WSServer.handler, "0.0.0.0", 8765, ping_interval=None
    )
    asyncio.ensure_future(ws_server)
    asyncio.ensure_future(main_server())
    loop.run_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("")
