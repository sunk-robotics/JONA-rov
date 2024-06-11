import adafruit_bno055
import asyncio
import autonomous
from autonomous import ImageHandler, CoralTransplanter, CoralReturn
import board
import cv2
import json
from motors import Motors
from ms5837 import MS5837_02BA
from orientation import quaternion_to_euler
from pid import PID, RotationalPID
from power_monitoring import PowerMonitor
from time import time
import websockets
from ws_server import WSServer

# how far the joystick needs to be moved before stabilization is temporarily
# disabled (0..1)
destable_thresh = 0.5


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

    try:
        power_monitor = PowerMonitor()
    except OSError:
        print("Unable to connect to power monitor!")
        power_monitor = None

    depth_anchor = False
    # adjust the y-velocity to have the ROV remain at a constant depth
    depth_pid = PID(proportional_gain=2, integral_gain=0.05, derivative_gain=0.01)

    yaw_anchor = False
    # adjust the yaw velocity to keep the ROV stable
    # TODO - Need to tune the PID parameters
    yaw_pid = RotationalPID(proportional_gain=0.03, integral_gain=0, derivative_gain=0)

    roll_anchor = False
    # adjust the roll velocity to keep the ROV stable
    roll_pid = RotationalPID(
        proportional_gain=-0.03, integral_gain=-0.001, derivative_gain=0.0e-4
    )

    pitch_anchor = False
    # adjust the pitch velocity to keep the ROV stable
    pitch_pid = RotationalPID(
        proportional_gain=0.02, integral_gain=0.007, derivative_gain=0.005
    )

    # multiplier for velocity to set speed limit
    speed_multiplier = 1

    # lock the controls in a certain state
    motor_lock = False

    # whether the ROV is attempting to autonomously transplant a sample of coral
    is_autonomous = False
    coral_transplanter = None

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
    prev_depth_anchor_toggle = None
    prev_roll_anchor_toggle = None
    prev_pitch_anchor_toggle = None
    prev_yaw_anchor_toggle = None
    prev_motor_lock_toggle = None
    prev_autonomous_toggle = None

    prev_z_velocity = 0
    prev_yaw_velocity = 0
    prev_roll_velocity = 0
    prev_pitch_velocity = 0

    #  ImageHandler.start_listening()
    print("Server started!")
    while True:
        joystick_data = WSServer.pump_joystick_data()
        if depth_sensor is not None:
            depth_sensor.read()

        # read sensor information
        internal_temp = imu.temperature if imu is not None else None
        internal_temp = 37
        external_temp = depth_sensor.temperature() if depth_sensor is not None else None
        cpu_temp = None
        depth = depth_sensor.depth() if depth_sensor is not None else None
        yaw = imu.euler[0] if imu is not None else None
        roll = imu.euler[1] if imu is not None else None
        pitch = imu.euler[2] - 90 if imu is not None else None
        x_accel = imu.linear_acceleration[0]
        y_accel = imu.linear_acceleration[1]
        z_accel = imu.linear_acceleration[2]
        voltage_5V = power_monitor.voltage_5V() if power_monitor is not None else None
        current_5V = power_monitor.current_5V() if power_monitor is not None else None
        voltage_12V = power_monitor.voltage_12V() if power_monitor is not None else None
        current_12V = power_monitor.current_12V() if power_monitor is not None else None

        # send data to web client
        if WSServer.web_client_main is not None:
            status_info = {
                "internal_temp": internal_temp,
                "external_temp": external_temp,
                "depth": depth,
                "yaw": yaw,
                "roll": roll,
                "pitch": pitch,
                "x_accel": x_accel,
                "y_accel": y_accel,
                "z_accel": z_accel,
                "voltage_5V": voltage_5V,
                "current_5V": current_5V,
                "voltage_12V": voltage_12V,
                "current_12V": current_12V,
                "speed_multiplier": speed_multiplier,
                "depth_anchor_enabled": depth_anchor,
                "yaw_anchor_enabled": yaw_anchor,
                "roll_anchor_enabled": roll_anchor,
                "pitch_anchor_enabled": pitch_anchor,
                "motor_lock_enabled": motor_lock,
            }
            await WSServer.web_client_main.send(json.dumps(status_info))

        # set all the velocities to 0 if there's no joystick connected
        if joystick_data:
            x_velocity = joystick_data["left_stick"][0] * speed_multiplier
            y_velocity = joystick_data["left_stick"][1] * speed_multiplier
            z_velocity = -joystick_data["right_stick"][1] * speed_multiplier
            yaw_velocity = joystick_data["right_stick"][0] * speed_multiplier
            pitch_velocity = joystick_data["dpad"][1] * speed_multiplier
            roll_velocity = joystick_data["dpad"][0] * speed_multiplier
            speed_toggle = (
                joystick_data["buttons"]["right_bumper"]
                - joystick_data["buttons"]["left_bumper"]
            )
            depth_anchor_toggle = joystick_data["buttons"]["north"]
            roll_anchor_toggle = joystick_data["buttons"]["east"]
            pitch_anchor_toggle = joystick_data["buttons"]["south"]
            yaw_anchor_toggle = joystick_data["buttons"]["west"]
            motor_lock_toggle = joystick_data["buttons"]["start"]
            autonomous_toggle = joystick_data["buttons"]["select"]
            photo_trigger = joystick_data["buttons"]["left_trigger"]
        else:
            x_velocity = 0
            y_velocity = 0
            z_velocity = 0
            yaw_velocity = 0
            pitch_velocity = 0
            roll_velocity = 0
            speed_toggle = 0
            yaw_anchor_toggle = 0
            roll_anchor_toggle = 0
            depth_anchor_toggle = 0
            pitch_anchor_toggle = 0
            motor_lock_toggle = 0
            autonomous_toggle = 0
            photo_trigger = 0

        # when the controller speed increases beyond 50% of the speed multiplier,
        # temporarily turn off any stabilization
        destable_thresh = speed_multiplier / 2

        # re-enable the depth anchor at a new depth when the z velocity falls below the
        # threshold
        if (
            depth_anchor
            and abs(z_velocity) < destable_thresh
            and abs(prev_z_velocity) > destable_thresh
        ):
            depth_pid.update_set_point(depth)

        # re-enable the yaw anchor at a new angle when the yaw velocity falls below the
        # threshold
        if (
            yaw_anchor
            and abs(yaw_velocity) < destable_thresh
            and abs(prev_yaw_velocity) > destable_thresh
        ):
            yaw_pid.update_set_point(yaw)

        # re-enable the roll anchor at a new angle when the roll velocity falls below the
        # threshold
        if (
            roll_anchor
            and abs(roll_velocity) < destable_thresh
            and abs(prev_roll_velocity) > destable_thresh
        ):
            roll_pid.update_set_point(roll)

        # re-enable the pitch anchor at a new angle when the pitch velocity falls below the
        # threshold
        if (
            pitch_anchor
            and abs(pitch_velocity) < destable_thresh
            and abs(prev_pitch_velocity) > destable_thresh
        ):
            pitch_pid.update_set_point(pitch)

        prev_z_velocity = z_velocity
        prev_yaw_velocity = yaw_velocity
        prev_roll_velocity = roll_velocity
        prev_pitch_velocity = pitch_velocity

        # set the z velocity according to the depth PID controller based on
        # current depth, the depth anchor should be temporarily disabled
        # when the z velocity is greater than a certain threshold in order to
        # give the pilot control over the depth when the depth anchor is on
        if depth_anchor and depth is not None and abs(z_velocity) < destable_thresh:
            z_velocity = depth_pid.compute(depth)

        # set the yaw velocity according to the yaw PID controller based on
        # current yaw angle
        if yaw_anchor and yaw is not None and abs(yaw_velocity) < destable_thresh:
            yaw_velocity = yaw_pid.compute(yaw)

        # set the roll velocity according to the roll PID controller based on
        # current roll angle
        if roll_anchor and roll is not None and abs(roll_velocity) < destable_thresh:
            roll_velocity = roll_pid.compute(roll)

        # set the pitch velocity according to the pitch PID controller based on
        # current pitch angle
        if pitch_anchor and pitch is not None and abs(pitch_velocity) < destable_thresh:
            #  print(f"Pitch Angle: {pitch}°")
            #  print(f"Error: {pitch_pid.set_point - pitch}")
            pitch_velocity = pitch_pid.compute(pitch)

        if motor_lock:
            x_velocity = locked_velocities["x_velocity"]
            y_velocity = locked_velocities["y_velocity"]
            z_velocity = locked_velocities["z_velocity"]
            yaw_velocity = locked_velocities["yaw_velocity"]
            pitch_velocity = locked_velocities["pitch_velocity"]
            roll_velocity = locked_velocities["roll_velocity"]

        # autonomous code should take precedence
        if is_autonomous:
            (
                x_velocity,
                y_velocity,
                z_velocity,
                yaw_velocity,
                roll_velocity,
                pitch_velocity,
                return_code,
            ) = coral_transplanter.next_step(depth, yaw, roll, pitch)
            if return_code == CoralReturn.FINISHED:
                is_autonomous = False
                ImageHandler.stop_listening()
                print("Autonomous task completed!")
            elif return_code == CoralReturn.FAILED:
                is_autonomous = False
                ImageHandler.stop_listening()
                print("Autonomous task failed! ;-;")

        if photo_trigger:
            img = ImageHandler.pump_image()
            cv2.imwrite(f"test_images/{time()}.jpg", img)

        #  if current_12V > 25:
        #      motors.speed_limit = 0.8
        #  else:
        #      motors.speed_limit = 1.0

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
            if speed_toggle > 0 and speed_multiplier < 1:
                speed_multiplier += 0.2
            # make sure the speed doesn't fall below 0
            if speed_toggle < 0 and speed_multiplier >= 0.2:
                speed_multiplier -= 0.2

            # just in case the speed multiplier ends up out of range
            if speed_multiplier > 1:
                speed_multiplier = 1
            elif speed_multiplier < 0:
                speed_multiplier = 0
            print(f"Speed Multiplier: {speed_multiplier}")
            prev_speed_toggle = speed_toggle

        # toggle the depth anchor
        if (
            depth_sensor is not None
            and depth_anchor_toggle
            and not prev_depth_anchor_toggle
        ):
            if depth_anchor:
                print("Vertical anchor disabled!")
                depth_anchor = False
            elif depth_sensor is not None:
                depth_anchor = True
                depth_pid.update_set_point(depth_sensor.depth())
                print(f"Vertical anchor enabled at: {depth_pid.set_point} m")

        # toggle the yaw anchor
        if imu is not None and yaw_anchor_toggle and not prev_yaw_anchor_toggle:
            if yaw_anchor:
                print("Yaw anchor disabled!")
                yaw_anchor = False
            elif depth_sensor is not None:
                yaw_anchor = True
                yaw_pid.update_set_point(yaw)
                print(f"Yaw anchor enabled at: {yaw_pid.set_point}°")

        # toggle the roll anchor
        if imu is not None and roll_anchor_toggle and not prev_roll_anchor_toggle:
            if roll_anchor:
                print("Roll anchor disabled!")
                roll_anchor = False
            elif depth_sensor is not None:
                roll_anchor = True
                roll_pid.update_set_point(roll)
                print(f"Roll anchor enabled at: {roll_pid.set_point}°")

        # toggle the pitch anchor
        if imu is not None and pitch_anchor_toggle and not prev_pitch_anchor_toggle:
            if pitch_anchor:
                print("Pitch anchor disabled!")
                pitch_anchor = False
            elif depth_sensor is not None:
                pitch_anchor = True
                pitch_pid.update_set_point(pitch)
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

        # toggle the autonomous control
        if autonomous_toggle and not prev_autonomous_toggle:
            if is_autonomous:
                is_autonomous = False
                ImageHandler.stop_listening()
                print("Autonomous mode disabled!")
            else:
                is_autonomous = True
                ImageHandler.start_listening()
                coral_transplanter = CoralTransplanter(depth, yaw)
                print("Autonomous mode enabled!")

        prev_depth_anchor_toggle = depth_anchor_toggle
        prev_yaw_anchor_toggle = yaw_anchor_toggle
        prev_roll_anchor_toggle = roll_anchor_toggle
        prev_pitch_anchor_toggle = pitch_anchor_toggle
        prev_motor_lock_toggle = motor_lock_toggle
        prev_autonomous_toggle = autonomous_toggle

        await asyncio.sleep(0.01)


def main():
    loop = asyncio.get_event_loop()
    auto_ws_server = websockets.serve(
        autonomous.WSServer.handler, "0.0.0.0", 3009, ping_interval=None
    )
    ws_server = websockets.serve(WSServer.handler, "0.0.0.0", 8765, ping_interval=None)
    asyncio.ensure_future(ws_server)
    asyncio.ensure_future(auto_ws_server)
    asyncio.ensure_future(ImageHandler.image_handler("ws://192.168.1.9:3000"))
    asyncio.ensure_future(main_server())
    loop.run_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("")
