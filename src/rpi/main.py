import adafruit_bno055
import asyncio
from autonomous import ImageHandler, CoralTransplanter, CoralReturn, SQUARE_HEIGHT
import board
import json
from motors import Motors
from ms5837 import MS5837_02BA
from pid import PID, RotationalPID
from power_monitoring import PowerMonitor
import threading
import websockets
from ws_server import WSServer
import logging



#########################################################
#               JONA-ROV - main.py - v2                 #
#########################################################


# how far the joystick needs to be moved before stabilization is temporarily
destable_thresh = 0.5

# set the current draw limit in amps. 
MAX_CURRENT = 25 

# ASCII color codes
COLORS = {
    "DEBUG": "\033[94m",    # Blue
    "INFO": "\033[92m",     # Green
    "WARNING": "\033[93m",  # Yellow
    "ERROR": "\033[91m",    # Red
    "CRITICAL": "\033[95m", # Magenta
    "RESET": "\033[0m"      # Reset color
}

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_color = COLORS.get(record.levelname, COLORS["RESET"])
        log_msg = f"{log_color}{record.levelname}: {record.msg}{COLORS['RESET']}"
        return log_msg


async def main_server():
    # Create a logger
    logger = logging.getLogger("ColoredLogger")
    logger.setLevel(logging.DEBUG)  # Log everything

    # File Handler (Plain Text)
    file_handler = logging.FileHandler("jona.log", mode="a")  # Append to log file
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)

    # Console Handler (With Colors)
    console_handler = logging.StreamHandler()
    console_formatter = ColoredFormatter()
    console_handler.setFormatter(console_formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Motor setup:
    motors = Motors()

    await asyncio.sleep(2) # wait 2 seconds for the escs to rx neutral sig.

    depth_sensor = MS5837_02BA(1)
    depth_sensor.init()
    imu = adafruit_bno055.BNO055_I2C(board.I2C())
    power_monitor = PowerMonitor()
    
    depth_anchor = False
    yaw_anchor = False
    roll_anchor = False
    pitch_anchor = False

    # whether the ROV is attempting to autonomously transplant a sample of coral
    is_autonomous = False

    # multiplier for velocity to set speed limit
    speed_multiplier = 1

    # adjust the y-velocity to have the ROV remain at a constant depth
    depth_pid = PID(proportional_gain=2, integral_gain=0.05, derivative_gain=0.01)

    # adjust the yaw velocity to keep the ROV stable
    # TODO - Need to tune the PID parameters
    yaw_pid = RotationalPID(proportional_gain=0.03, integral_gain=0, derivative_gain=0)

    # adjust the roll velocity to keep the ROV stable
    roll_pid = RotationalPID(proportional_gain=-0.03, integral_gain=-0.001, derivative_gain=0.0e-4)

    # adjust the pitch velocity to keep the ROV stable
    pitch_pid = RotationalPID(proportional_gain=0.02, integral_gain=0.007, derivative_gain=0.005)

    # lock the controls in a certain state, each velocity can have its own lock
    motor_locks = {
        "x": False,
        "y": False,
        "z": False,
        "yaw": False,
        "pitch": False,
        "roll": False,
    }

    locked_velocities = {
        "x": 0,
        "y": 0,
        "z": 0,
        "yaw": 0,
        "pitch": 0,
        "roll": 0,
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

    # the recorded depth of the red square for the autonomous brain coral transportation task
    square_depth = None

    throttle_limit_factor = 0
    set_throttle = speed_multiplier

    logging.info("JONA ROV - COPYRIGHT SUNK ROBOTICS 2025")
    while True:
        joystick_data = WSServer.pump_joystick_data()
        can_read_depth = True
        if depth_sensor is not None:
            try:
                depth_sensor.read()
            except OSError:
                can_read_depth = False
                logging.error("Unable to read from depth sensor!")

        # read sensor information
        internal_temp = imu.temperature if imu is not None else None
        external_temp = depth_sensor.temperature() if depth_sensor is not None else None

        depth = (
            depth_sensor.depth()
            if depth_sensor is not None and can_read_depth
            else None
        )
        yaw = imu.euler[0] if imu is not None else None
        roll = imu.euler[1] if imu is not None else None
        pitch = imu.euler[2] if imu is not None else None

        if pitch is not None:
            pitch -= 90

        x_accel = imu.linear_acceleration[0] if imu is not None else None
        y_accel = imu.linear_acceleration[1] if imu is not None else None
        z_accel = imu.linear_acceleration[2] if imu is not None else None
        voltage_5V = power_monitor.voltage_5V() if power_monitor is not None else None
        current_5V = power_monitor.current_5V() if power_monitor is not None else None
        # voltage_12V = power_monitor.voltage_12V() if power_monitor is not None else None
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
                "voltage_12V": 0,
                "current_12V": current_12V,
                "speed_multiplier": speed_multiplier,
                "depth_anchor_enabled": depth_anchor,
                "yaw_anchor_enabled": yaw_anchor,
                "roll_anchor_enabled": roll_anchor,
                "pitch_anchor_enabled": pitch_anchor,
                "motor_lock_enabled": motor_locks,
                "throttle_limit_factor": throttle_limit_factor,
            }

            status_info = json.dumps(status_info)

            #try:
            await WSServer.web_client_main.send(status_info)
            #except Exception as e:
                #print("Main Web Client Connection Error: ", e) # TODO Make this work and not have this problem

            if WSServer.debug_client is not None:
                try:
                    await WSServer.debug_client.send(status_info) # TODO same here as above todo.
                except Exception as e:
                    print("Debug Client Connection Error: ", e)

        # set all the velocities to 0 if there's no joystick connected
        if joystick_data:
            x_velocity = joystick_data["left_stick"][0] * speed_multiplier
            y_velocity = joystick_data["left_stick"][1] * speed_multiplier
            z_velocity = joystick_data["right_stick"][1] * speed_multiplier
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
            record_depth_trigger = joystick_data["buttons"]["right_trigger"]
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
            record_depth_trigger = 0

        # when the controller speed increases beyond 50% of the speed multiplier,
        # temporarily turn off any stabilization
        destable_thresh = speed_multiplier / 2

        # adjust speed mutliplier based on current draw
        if (current_12V > MAX_CURRENT):
            previous_speed_multiplier = speed_multiplier
            throttle_limit_factor += 0.1
        else:
            throttle_limit_factor = 0
            speed_multiplier = set_throttle
	     
        # apply factor
        speed_multiplier -= throttle_limit_factor

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
            z_velocity = -depth_pid.compute(depth)

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
            pitch_velocity = pitch_pid.compute(pitch)

        if motor_locks["x"]:
            logging.debug("X-axis motor lock")
            x_velocity = locked_velocities["x"]
        if motor_locks["y"]:
            logging.debug("Y-axis motor lock")
            y_velocity = locked_velocities["y"]
        if motor_locks["z"]:
            logging.debug("Z-axis motor lock")
            z_velocity = locked_velocities["z"]
        if motor_locks["yaw"]:
            yaw_velocity = locked_velocities["yaw"]
        if motor_locks["pitch"]:
            pitch_velocity = locked_velocities["pitch"]
        if motor_locks["roll"]:
            roll_velocity = locked_velocities["roll"]

        # autonomous code should take precedence
        if is_autonomous:
            pass

        if photo_trigger:
            pass

        # before beginning the autonomous coral transplantation task, the ROV should
        # move over to the square and record the depth of the square
        if record_depth_trigger:
            square_depth = depth

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
                #speed_multiplier += 0.2
                set_throttle += 0.1
            # make sure the speed doesn't fall below 0
            if speed_toggle < 0 and speed_multiplier >= 0.2:
                #speed_multiplier -= 0.2
                set_throttle -= 0.1
            # just in case the speed multiplier ends up out of range
            if speed_multiplier > 1:
                speed_multiplier = 1
            elif speed_multiplier < 0:
                speed_multiplier = 0
            logging.info(f"Speed Multiplier Setting: {speed_multiplier}x")
            prev_speed_toggle = speed_toggle

        # toggle the depth anchor
        if (
            depth_sensor is not None
            and depth_anchor_toggle
            and not prev_depth_anchor_toggle
        ):
            if depth_anchor:
                logging.info("Vertical anchor disabled.")
                depth_anchor = False
            elif depth_sensor is not None:
                depth_anchor = True
                depth_pid.update_set_point(depth_sensor.depth())
                logging.info(f"Vertical anchor enabled at: {depth_pid.set_point} m")

        # toggle the yaw anchor
        if imu is not None and yaw_anchor_toggle and not prev_yaw_anchor_toggle:
            if yaw_anchor:
                logging.info("Yaw anchor disabled!")
                yaw_anchor = False
            elif depth_sensor is not None:
                yaw_anchor = True
                yaw_pid.update_set_point(yaw)
                logging.info(f"Yaw anchor enabled at: {yaw_pid.set_point}°")

        # toggle the roll anchor
        if imu is not None and roll_anchor_toggle and not prev_roll_anchor_toggle:
            if roll_anchor:
                logging.info("Roll anchor disabled!")
                roll_anchor = False
            elif depth_sensor is not None:
                roll_anchor = True
                roll_pid.update_set_point(roll)
                logging.info(f"Roll anchor enabled at: {roll_pid.set_point}°")

        # toggle the pitch anchor
        if imu is not None and pitch_anchor_toggle and not prev_pitch_anchor_toggle:
            if pitch_anchor:
                logging.info("Pitch anchor disabled!")
                pitch_anchor = False
            elif depth_sensor is not None:
                pitch_anchor = True
                pitch_pid.update_set_point(pitch)
                logging.info(f"Pitch anchor enabled at: {pitch_pid.set_point}°")

        # toggle the motor lock
        if motor_lock_toggle and not prev_motor_lock_toggle:
            if any(motor_locks.values()):
                motor_locks = {
                    "x": False,
                    "y": False,
                    "z": False,
                    "yaw": False,
                    "pitch": False,
                    "roll": False,
                }
                logging.info("Motor lock disabled!")
            else:
                motor_locks = {
                    "x": True,
                    "y": True,
                    "z": True,
                    "yaw": True,
                    "pitch": True,
                    "roll": True,
                }
                locked_velocities["x"] = x_velocity
                locked_velocities["y"] = y_velocity
                locked_velocities["z"] = z_velocity
                locked_velocities["yaw"] = yaw_velocity
                locked_velocities["pitch"] = pitch_velocity
                locked_velocities["roll"] = roll_velocity
                logging.info("Motor lock enabled!")

        # toggle the autonomous control
        if autonomous_toggle and not prev_autonomous_toggle:
            if is_autonomous:
                ImageHandler.stop_listening()
                is_autonomous = False
                logging.critical("Autonomous mode disabled!")
            else:
                ImageHandler.start_listening()
                is_autonomous = True
                if square_depth is not None:
                    coral_transplanter = CoralTransplanter(square_depth, yaw)
                else:
                    coral_transplanter = CoralTransplanter(depth - SQUARE_HEIGHT, yaw)
                logging.critical("Autonomous mode enabled!")

        prev_depth_anchor_toggle = depth_anchor_toggle
        prev_yaw_anchor_toggle = yaw_anchor_toggle
        prev_roll_anchor_toggle = roll_anchor_toggle
        prev_pitch_anchor_toggle = pitch_anchor_toggle
        prev_motor_lock_toggle = motor_lock_toggle
        prev_autonomous_toggle = autonomous_toggle

        await asyncio.sleep(0.01)


def main():
    loop = asyncio.get_event_loop()

    ws_server = websockets.serve(WSServer.handler, "0.0.0.0", 8765, ping_interval=None)
    asyncio.ensure_future(ws_server)
   
    threading.Thread(target=ImageHandler.image_processer, daemon=True).start()
    threading.Thread(
        target=ImageHandler.image_receiver, args=("ws://192.168.1.9:3000",), daemon=True
    ).start()

    asyncio.ensure_future(main_server())
    loop.run_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.critical("Keyboard Interrupt, Exiting")
