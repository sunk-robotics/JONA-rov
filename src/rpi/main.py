#!/bin/python
import adafruit_bno055
import asyncio
import board
import json
from motors import Motors
from ms5837 import MS5837_02BA
import time
import websockets


# websocket server
class WSServer:
    # registers the websocket objects of the clients to allow sending data to
    # the clients outside of the handler function
    joystick_client = None
    # web client websocket object used to transmit non-image data (sensor data)
    web_client_main = None
    # separate websocket used to transmit binary image data
    web_client_camera = None

    # incoming joystick data, can be accessed outside of the handler function
    joystick_data = None

    @classmethod
    def pump_joystick_data(cls):
        return cls.joystick_data

    @classmethod
    async def joystick_handler(cls, websocket, path):
        cls.joystick_client = websocket
        print("Joystick client connected")
        async for message in websocket:
            cls.joystick_data = json.loads(message)
        cls.joystick_client = None

    @classmethod
    async def web_client_main_handler(cls, websocket, path):
        cls.web_client_main = websocket
        print("Web client connected!")
        while True:
            try:
                await websocket.wait_closed()
                print("Web client disconnected!")
                cls.web_client_main = None
                break
            except websockets.ConnectionClosed:
                print("Web client disconnected!")

    @classmethod
    async def web_client_camera_handler(cls, websocket, path):
        cls.web_client_camera = websocket
        print("Web client connected!")
        while True:
            try:
                await websocket.wait_closed()
                print("Web client disconnected!")
                cls.web_client_camera = None
                break
            except websockets.ConnectionClosed:
                print("Web client disconnected!")

    @classmethod
    async def handler(cls, websocket, path):
        try:
            client_info_json = await asyncio.wait_for(websocket.recv(),
                                                      timeout=2.0)
            print("Client connected!")
        except asyncio.TimeoutError:
            print("Connection failed!")
            return
        client_info = json.loads(client_info_json)
        try:
            client_type = client_info["client_type"]
        except KeyError:
            print("Key error!")
            return
        if client_type == "joystick":
            await cls.joystick_handler(websocket, path)
        elif client_type == "web_client_main":
            await cls.web_client_main_handler(websocket, path)
        elif client_type == "web_client_camera":
            await cls.web_client_camera_handler(websocket, path)


# used to adjust the motor velocities to keep the ROV at a constant position
class PID:
    last_time = None
    last_error = None

    def __init__(self, set_point=0, proportional_gain=0, integral_gain=0,
                 derivative_gain=0):
        self.set_point = set_point
        self.proportional_gain = proportional_gain
        self.integral_gain = integral_gain
        self.derivative_gain = derivative_gain

        self.integral = 0
        self.last_time = time.time()
        self.last_error = set_point

    # takes in the acceleration as the process value
    def compute(self, process_value):
        current_time = time.time()
        d_time = time.time() - self.last_time
        self.last_time = current_time

        # difference between the target and measured acceleration
        error = self.set_point - process_value
        #  print(f"Set point: {self.set_point}")
        #  print(f"Process value: {process_value}")
        #  print(f"Error: {error}")
        # compute the integral ∫e(t) dt
        self.integral += error * d_time
        # compute the derivative
        d_error = (error - self.last_error) / d_time
        self.last_error = error

        # add the P, I, and the D together
        output = (self.proportional_gain * error + self.integral_gain
                  * self.integral + self.derivative_gain * d_error)
        return output


async def main_server():
    motors = Motors()

    depth_sensor = MS5837_02BA(1)
    try:
        imu = adafruit_bno055.BNO055_I2C(board.I2C())
    except OSError:
        print("Unable to connect IMU")

    vertical_anchor = False
    # adjust the y-velocity to have the ROV remain at a constant depth
    vertical_pid = PID()

    yaw_anchor = False
    # adjust the yaw velocity to keep the ROV stable
    yaw_pid = PID()

    roll_anchor = False
    # adjust the roll velocity to keep the ROV stable
    roll_pid = PID()

    pitch_anchor = False
    # adjust the pitch velocity to keep the ROV stable
    pitch_pid = PID()

    # multiplier for velocity to set speed limit
    speed_factor = 0.5

    # lock the controls in a certain state to allow for "autonomous" docking
    motor_lock = False

    locked_velocities = {
        "x_velocity": 0,
        "y_velocity": 0,
        "z_velocity": 0,
        "yaw_velocity": 0,
        "pitch_velocity": 0,
        "roll_velocity": 0
    }

    # stores the last button press of the velocity toggle button
    prev_speed_toggle = None
    prev_vertical_anchor_toggle = None
    prev_roll_anchor_toggle = None
    prev_pitch_anchor_toggle = None
    prev_yaw_anchor_toggle = None
    prev_motor_lock_toggle = None

    if not depth_sensor.init():
        print("Depth sensor not working!")
        depth_sensor = None

    print("Server started!")
    while True:
        joystick_data = WSServer.pump_joystick_data()
        depth_sensor.read()

        # if a joystick client hasn't connected yet
        if not joystick_data:
            await asyncio.sleep(0.01)
            continue

        x_velocity = joystick_data["right_stick"][0] * speed_factor
        y_velocity = joystick_data["left_stick"][1] * speed_factor
        z_velocity = joystick_data["right_stick"][1] * speed_factor
        yaw_velocity = joystick_data["left_stick"][0] * speed_factor
        pitch_velocity = joystick_data["dpad"][1] * speed_factor
        roll_velocity = joystick_data["dpad"][0] * speed_factor
        speed_toggle = (joystick_data["right_bumper"]
                        - joystick_data["left_bumper"])
        vertical_anchor_toggle = joystick_data["buttons"]["north"]
        roll_anchor_toggle = joystick_data["buttons"]["east"]
        pitch_anchor_toggle = joystick_data["buttons"]["south"]
        yaw_anchor_toggle = joystick_data["buttons"]["west"]
        motor_lock_toggle = joystick_data["buttons"]["start"]

        if motor_lock:
            x_velocity = locked_velocities["x_velocity"]
            y_velocity = locked_velocities["y_velocity"]
            z_velocity = locked_velocities["z_velocity"]
            yaw_velocity = locked_velocities["yaw_velocity"]
            pitch_velocity = locked_velocities["pitch_velocity"]
            roll_velocity = locked_velocities["roll_velocity"]

        # set the z velocity according to the vertical PID controller based on
        # current depth
        if vertical_anchor:
            z_velocity = vertical_pid.compute(depth_sensor.depth())

        # set the yaw velocity according to the yaw PID controller based on
        # current yaw angle
        if yaw_anchor:
            yaw_angle = imu.euler[1]
            if yaw_angle is not None:
                yaw_velocity = yaw_pid.compute(yaw_angle)

        # set the roll velocity according to the roll PID controller based on
        # current roll angle
        if roll_anchor:
            roll_angle = imu.euler[1]
            if roll_angle is not None:
                roll_velocity = roll_pid.compute(roll_angle)

        # set the pitch velocity according to the pitch PID controller based on
        # current pitch angle
        if pitch_anchor:
            pitch_angle = imu.euler[2]
            if pitch_angle is not None:
                pitch_velocity = pitch_pid.compute(pitch_angle)

        motors.drive_motors(x_velocity, y_velocity, z_velocity, yaw_velocity,
                            pitch_velocity, roll_velocity)

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
            prev_speed_toggle = speed_toggle

        # toggle the vertical anchor
        if vertical_anchor_toggle and not prev_vertical_anchor_toggle:
            if vertical_anchor:
                print("Vertical anchor disabled!")
                vertical_anchor = False
            elif depth_sensor is not None:
                vertical_anchor = True
                vertical_anchor_depth = depth_sensor.depth()
                vertical_pid = PID(vertical_anchor_depth, proportional_gain=2,
                                   integral_gain=0.05, derivative_gain=0.01)
                print(f"Vertical anchor enabled at: {vertical_anchor_depth} m")

        # toggle the yaw anchor
        if yaw_anchor_toggle and not prev_yaw_anchor_toggle:
            if yaw_anchor:
                print("Pitch anchor disabled!")
            elif depth_sensor is not None:
                yaw_anchor = True
                yaw_anchor_angle = imu.euler[2]
                # TODO - Need to tune PID parameters
                yaw_pid = PID(yaw_anchor_angle, proportional_gain=0,
                              integral_gain=0, derivative_gain=0)
                print(f"Pitch anchor enabled at: {yaw_anchor_angle}°")

        # toggle the roll anchor
        if roll_anchor_toggle and not prev_roll_anchor_toggle:
            if roll_anchor:
                print("Roll anchor disabled!")
                roll_anchor = False
            elif depth_sensor is not None:
                roll_anchor = True
                roll_anchor_angle = imu.euler[1]
                roll_pid = PID(roll_anchor_angle, proportional_gain=0.025,
                               integral_gain=0.001, derivative_gain=0.0e-4)
                print(f"Roll anchor enabled at: {roll_anchor_angle}°")

        # toggle the pitch anchor
        if pitch_anchor_toggle and not prev_pitch_anchor_toggle:
            if pitch_anchor:
                print("Pitch anchor disabled!")
            elif depth_sensor is not None:
                pitch_anchor = True
                pitch_anchor_angle = imu.euler[2]
                # TODO - Need to tune PID parameters
                pitch_pid = PID(pitch_anchor_angle, proportional_gain=0,
                                integral_gain=0, derivative_gain=0)
                print(f"Pitch anchor enabled at: {pitch_anchor_angle}°")

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
        WSServer.handler, "0.0.0.0", 8765, ping_interval=None)
    asyncio.ensure_future(ws_server)
    asyncio.ensure_future(main_server())
    loop.run_forever()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('')
