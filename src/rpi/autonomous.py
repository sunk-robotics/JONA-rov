import asyncio
import cv2
from enum import auto, Enum
from functools import reduce
import math
import numpy as np
import os
from pid import PID, RotationalPID
import queue
from queue import Queue
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from scipy.interpolate import splprep, splev
import sys
import threading
from time import time, sleep
from timer import Timer
from ultralytics import YOLO
import websockets
import websockets.sync.client


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


#  SQUARE_DETECTION_MODEL = YOLO(
#      "square_detection_ncnn_model", task="detect", verbose=False
#  )

SQUARE_DETECTION_MODEL = YOLO("square_detection_ncnn_model", task="detect")


class WSServer:
    frame = None

    @classmethod
    async def handler(cls, websocket, path):
        print("Client connected!")
        try:
            while True:
                if cls.frame is None:
                    await asyncio.sleep(0.001)
                    continue

                await websocket.send(bytearray(cls.frame))
                await asyncio.sleep(0.001)

        except websockets.ConnectionClosed:
            print("Client disconnected!")


class ImageHandler:
    image = None
    square_x = None
    square_y = None
    square_width = None
    square_height = None

    # the image queue should only hold one image at a time
    image_queue = Queue(1)
    is_listening = False

    last_frame_time = 0

    # process each image in a separate thread to avoid blocking. uses a queue that holds
    # only the most recent image
    @classmethod
    def image_processer(cls):
        while True:
            message = cls.image_queue.get()
            if not cls.is_listening:
                cls.image_queue.task_done()
                continue
            try:
                buffer = np.asarray(bytearray(message), dtype="uint8")
                img = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
            except Exception as e:
                print(f"Fuck: {e}")
                continue
            gray = cv2.cvtColor(
                cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR
            )
            x, y, width, height = find_square(gray, save_image=True)
            cls.square_x = x
            cls.square_y = y
            cls.square_width = width
            cls.square_height = height
            cls.image = img
            cls.image_queue.task_done()

    @classmethod
    def image_receiver(cls, uri):
        while True:
            try:
                with websockets.sync.client.connect(uri) as websocket:
                    for message in websocket:
                        try:
                            cls.image_queue.put_nowait(message)
                        except queue.Full:
                            pass
            except OSError:
                sleep(0.5)

    @classmethod
    async def image_handler(cls, uri):
        # spawn a thread to process incoming images without blocking
        threading.Thread(target=ImageHandler.image_processer, daemon=True).start()
        threading.Thread(
            target=ImageHandler.image_receiver, args=(uri,), daemon=True
        ).start()

    @classmethod
    def pump_image(cls):
        img = cls.image
        square_x = cls.square_x
        square_y = cls.square_y
        square_width = cls.square_width
        square_height = cls.square_height
        cls.square_coords = None, None
        cls.square_width = None
        cls.square_height = None
        cls.image = None
        return img, square_x, square_y, square_width, square_height

    @classmethod
    def start_listening(cls):
        cls.is_listening = True

    @classmethod
    def stop_listening(cls):
        cls.is_listening = False


# the steps in the process of transplanting the brain coral, broken down into an enum
# for readability
class CoralState(Enum):
    # the steps in the algorithm
    STARTING = 0
    MOVING_UP = 1
    ROTATING = 2
    APPROACHING = 3
    VERIFYING_SQUARE = 4
    CENTERING_SQUARE = 5
    ARRIVING_AT_SQUARE = 6
    MOVING_BLINDLY = 7
    SLOW_DOWN = 8
    SETTING_DOWN = 9
    ROCKET_UP = 10
    ROCKET_DOWN = 11
    FINISHED = 12
    # other states
    FAILURE = auto()


class CoralReturn(Enum):
    FAILED = -1
    FINISHED = 0
    IN_PROGRESS = 1


# the red square is at a height of about 32 cm above the pool floor
SQUARE_HEIGHT = 0.32
# the ROV should be 30 cm above the height of the square when moving towards it
MOVING_HEIGHT = 0.30
BLIND_MOVING_TIME = 1
# after placing the bowl in the correct spot, the ROV has a lot forward momentum that
# needs to be countered
#  SLOW_DOWN_TIME = 0.3
SLOW_DOWN_TIME = 0.3
# the ROV should spend 1 second setting the square down
SETTING_DOWN_TIMEOUT = 1
# when a square is first detected, verify its existence by seeing if it exists in 10
# different frames
NUM_VERIFICATIONS = 10


class CoralTransplanter:
    def __init__(self, square_depth: float, yaw_angle: int):
        # the red square is at a height of about 32 cm above the pool floor
        #  self.SQUARE_HEIGHT = 0.32
        # the ROV should be 30 cm above the height of the square when moving towards it
        #  self.MOVING_HEIGHT = self.SQUARE_HEIGHT + 0.30
        #  self.MOVING_HEIGHT = 0.30

        # after the red square is no longer in the ROV's vision, the ROV should continue
        # moving for another second
        #  self.BLIND_MOVING_TIME = 1
        # after placing the bowl in the correct spot, the ROV has a lot of forward
        # momentum that needs to be countered
        #  self.SLOW_DOWN_TIME = 0.3
        # if the ROV takes longer than 3 seconds to reach the target depth, assume that
        # the depth is slightly off and stop attempting
        #  self.SETTING_DOWN_TIMEOUT = 1

        self.square_depth = square_depth
        self.moving_depth = self.square_depth - MOVING_HEIGHT

        self.prev_square_coords = []

        #  self.NUM_VERIFICATIONS = 10
        self.verify_count = 0

        # the roll and pitch anchor should always be on
        self.roll_anchor = True
        self.pitch_anchor = True

        self.yaw_pid = RotationalPID(
            proportional_gain=0.025, integral_gain=0, derivative_gain=0
        )
        # the ROV should stay parallel to the pool floor
        self.roll_pid = RotationalPID(
            0, proportional_gain=-0.022, integral_gain=-0.001, derivative_gain=0.0e-4
        )
        self.pitch_pid = RotationalPID(
            15, proportional_gain=0.035, integral_gain=0.009, derivative_gain=0.005
        )
        self.depth_pid = PID(
            proportional_gain=3, integral_gain=0.1, derivative_gain=0.01
        )

        self.square_x_pid = PID(
            proportional_gain=-0.002, integral_gain=0, derivative_gain=0
        )
        self.square_y_pid = PID(
            proportional_gain=0.1, integral_gain=0, derivative_gain=0
        )

        self.approaching_timer = Timer()
        self.estimating_timer = Timer()

        self.current_step = CoralState.STARTING

    def next_step(
        self, depth: float, yaw: float, roll: float, pitch: float
    ) -> (float, float, float, float, float, float, CoralReturn):
        x_velocity = 0
        y_velocity = 0
        z_velocity = 0
        yaw_velocity = 0
        roll_velocity = self.roll_pid.compute(roll) if self.roll_anchor else 0
        pitch_velocity = self.pitch_pid.compute(pitch) if self.pitch_anchor else 0

        (
            img,
            square_x,
            square_y,
            square_width,
            square_height,
        ) = ImageHandler.pump_image()
        if img is None:
            print("No image")
            return (
                x_velocity,
                y_velocity,
                z_velocity,
                yaw_velocity,
                roll_velocity,
                pitch_velocity,
                CoralReturn.IN_PROGRESS,
            )

        img_height, img_width = img.shape[:2]
        img_center_x = img_width / 2
        self.square_x_pid.update_set_point(img_center_x)

        print(self.current_step)
        print(f"Current Time: {time()}")

        if self.current_step == CoralState.STARTING:
            self.depth_pid.update_set_point(self.moving_depth)
            print(f"Moving Depth: {self.moving_depth}")
            # keep the ROV's yaw locked
            self.yaw_pid.update_set_point(yaw)
            self.current_step = CoralState.MOVING_UP
            print("Moving on Next Step: Moving Up")

        # step 1 is to move up to a few centimeters above the red square
        elif self.current_step == CoralState.MOVING_UP:
            z_velocity = -self.depth_pid.compute(depth)
            yaw_velocity = self.yaw_pid.compute(yaw)
            print(
                f"Set Point: {self.yaw_pid.set_point} Yaw: {yaw} Yaw Velocity: {yaw_velocity}"
            )

            # the ROV should be within 1 cm of the target depth
            EPSILON = 0.01

            # move on to the next step if the ROV's height is within 1 cm of the target
            if abs(self.moving_depth - depth) <= EPSILON:
                self.current_step = CoralState.APPROACHING
                self.approaching_timer.start()
                print("Moving on Next Step: Approaching Square")

        # step 2 is to approach the square blindly until the square comes into view
        # Main Failure Condition: Square is not identified after moving for 15 seconds
        # Result: Abandon attempt
        # Non-Ideal but Non-Failure Condition: False positive
        # Result: Verify the square's existence
        elif self.current_step == CoralState.APPROACHING:
            print(f"Roll Velocity: {roll_velocity} Pitch Velocity: {pitch_velocity}")
            z_velocity = -self.depth_pid.compute(depth)
            yaw_velocity = self.yaw_pid.compute(yaw)
            y_velocity = 0.0

            # if the square can't be found after moving for 15 seconds, just give up
            print(self.approaching_timer.read())
            if self.approaching_timer.read() > 15:
                self.curent_step = CoralState.FAILURE
                print("Time's up! Couldn't find square!")
                return (0, 0, 0, 0, 0, 0, CoralReturn.FAILED)

            # may want to implement something to make sure the x and y coords are stable
            # to prevent the algorithm from latching onto some random red object
            if square_x is not None and square_y is not None:
                print(f"Found square at ({square_x}, {square_y})!")
                self.prev_square_coords = []

                self.approaching_timer.stop()
                #  self.current_step = CoralState.VERIFYING_SQUARE
                self.current_step = CoralState.CENTERING_SQUARE
                print("Moving on Next Step: Verifying Square")
        # step 3 is to make sure the red square that the ROV detected is actually the
        # square
        elif self.current_step == CoralState.VERIFYING_SQUARE:
            z_velocity = -self.depth_pid.compute(depth)
            yaw_velocity = self.yaw_pid.compute(yaw)
            y_velocity = -0.1

            if self.verify_count < NUM_VERIFICATIONS:
                if square_x is not None and square_y is not None:
                    self.prev_square_coords.append((square_x, square_y, time()))
                else:
                    self.prev_square_coords.append((None, None, time()))
                self.verify_count += 1
            else:
                #  coords_without_none = filter(
                #      lambda c: c[0] is not None and c[1] is not None,
                #      self.prev_square_coords,
                #  )
                #  coords_np_array = np.array(self.prev_square_coords)
                #  std_dev_x = np.std(coords_np_array, axis=0)
                #  std_dev_y = np.std(coords_np_array, axis=1)

                num_not_found = 0
                for coords in self.prev_square_coords:
                    if coords[0] is None and coords[1] is None:
                        num_not_found += 1

                # to verify the square's existence, the square should be visible for
                # over 90% of the time, and vary too much in its location (given that
                # the ROV is supposed to be stationary)
                if (
                    num_not_found
                    > len(self.prev_square_coords) * 0.2
                    #  or std_dev_x > 50
                    #  or std_dev_y > 50
                ):
                    self.verify_count = 0
                    self.current_step = CoralState.APPROACHING
                    self.approaching_timer.start()
                else:
                    print("Verified!")
                    self.prev_square_coords = []
                    self.current_step = CoralState.CENTERING_SQUARE

        # step 4 is to center the square in the ROV's vision
        elif self.current_step == CoralState.CENTERING_SQUARE:
            #  print(f"X Coord: {square_x} Y Coord: {square_y}")
            EPSILON = 25
            z_velocity = -self.depth_pid.compute(depth)
            y_velocity = -0.1

            if square_x is not None and square_y is not None:
                self.estimating_timer.stop()
                self.estimating_timer.reset()
                self.prev_square_coords.append((square_x, square_y, time()))
                print(f"X: {square_x} Set Point: {self.square_x_pid.set_point}")
                yaw_velocity = self.square_x_pid.compute(square_x)
                print(f"Yaw Velocity: {yaw_velocity}")

                if abs(img_center_x - square_x) <= EPSILON:
                    self.prev_square_coords = []
                    print("Success!")
                    self.current_step = CoralState.ARRIVING_AT_SQUARE
                    #  self.current_step = CoralState.FINISHED

            # it's possible the square might be temporarily invisible,if there's enough
            # data points to work with, use a linear regression to estimate the position
            # of the square
            #  elif len(self.prev_square_coords) > 3 and self.estimating_timer.read() < 1:
            #      if self.estimating_timer.stopped:
            #          self.estimating_timer.start()
            #      prev_x_coords = np.array(
            #          [c[0] for c in self.prev_square_coords]
            #      ).reshape((-1, 1))
            #      prev_times = [c[2] for c in self.prev_square_coords]
            #      print(f"X Coords: {prev_x_coords}")
            #      print(f"Times: {prev_times}")
            #      # performs a linear regression on the data to approximate a function
            #      # for the x coordinate given a time
            #      model = LinearRegression().fit(prev_x_coords, prev_times)
            #      # estimates the x coord given the current time
            #      approx_x_coord = model.coef_ * time() + model.intercept_
            #      yaw_velocity = self.square_x_pid.compute(approx_x_coord)

            # if there's not enough data points to work with, go back and verify the
            # square's existence
            #  else:
            #      self.prev_square_coords = []
            #      self.current_step = CoralState.VERIFYING_SQUARE

        # step 6 is to continue approaching the square, keeping the square centered
        # horizontally in the ROV's vision, until the square falls off the bottom of the
        # screen
        elif self.current_step == CoralState.ARRIVING_AT_SQUARE:
            EPSILON_Y = 30
            EPSILON_X = 200

            z_velocity = -self.depth_pid.compute(depth)
            print(
                f"Depth: {depth} Target Depth: {self.depth_pid.set_point} Z-Velocity: {z_velocity}"
            )
            y_velocity = 0.25

            if square_x is not None and square_y is not None:
                print(f"Coords: ({square_x}, {square_y})")
                yaw_velocity = self.square_x_pid.compute(square_x)

                # to protect against a random false positive, the previous sighting of the square must be in the general area
                if len(self.prev_square_coords) > 1:
                    #  prev_x = self.prev_square_coords[-1][0]
                    #  prev_y = self.prev_square_coords[-1][1]
                    if (
                        abs(square_x - img_center_x) <= EPSILON_X
                        and abs(square_y - img_height) <= EPSILON_Y
                        #  and abs(prev_x - img_center_x) <= EPSILON * 1.5
                        #  and abs(prev_y - img_height) <= EPSILON * 1.5
                    ):
                        self.start_time = time()
                        self.current_step = CoralState.SLOW_DOWN

                self.prev_square_coords.append((square_x, square_y, time()))
                #  self.square_x_pid.update_set_point(img_center_x)

            # check if the square disappeared off the bottom of the screen
            #  elif len(self.prev_square_coords) > 10:
            #      prev_y_coords = np.array([c[1] for c in self.prev_square_coords])
            #      prev_times = np.array(
            #          [c[2] for c in self.prev_square_coords], dtype="double"
            #      ).reshape((-1, 1))
            #      prev_times_transformed = PolynomialFeatures(
            #          degree=2, include_bias=False
            #      ).fit_transform(prev_times)
            #      print(f"Y Coords: {prev_y_coords}")
            #      print(f"Times: {prev_times}")
            #      # performs a linear regression on the data to approximate a function
            #      # for the y coordinate given a time
            #      model = LinearRegression().fit(prev_times_transformed, prev_y_coords)
            #      # estimates the x coord given the current time
            #      print(f"Coefficient: {model.coef_} Intercept: {model.intercept_}")
            #      time_transformed = time() ** 2
            #      predicted_y_coord = model.coef_ * time_transformed + model.intercept_
            #      print(f"Predicted Y Coord: {predicted_y_coord}")
            #      #  predicted_y_coord = model.predict(time())
            #      if predicted_y_coord > img_height - EPSILON:
            #          print("I think it's gone")
            #          self.start_time = time()
            #          self.current_step = CoralState.MOVING_BLINDLY

            # if there haven't already been 10 recorded coordinates, go back and verify that the square exists
            else:
                print("Where'd it go?")
                #  self.current_step = CoralState.VERIFYING_SQUARE

        # after the red square is no longer visible, the ROV should continue moving
        # so that the coral sample aligns with the square
        elif self.current_step == CoralState.MOVING_BLINDLY:
            z_velocity = -self.depth_pid.compute(depth)
            y_velocity = 0.2

            if time() - self.start_time >= BLIND_MOVING_TIME:
                self.start_time = time()
                self.current_step = CoralState.SETTING_DOWN
                print("Moving on Next Step: Setting Down")

        # need to counter the ROV's forward momentum
        elif self.current_step == CoralState.SLOW_DOWN:
            y_velocity = 0.25
            if time() - self.start_time >= SLOW_DOWN_TIME:
                self.start_time = time()
                self.current_step = CoralState.SETTING_DOWN
        # step 8 is to set the coral head down on the red square
        elif self.current_step == CoralState.SETTING_DOWN:
            # the ROV should be within 1 cm of the target depth
            EPSILON = 1
            z_velocity = -0.3
            yaw_velocity = 0.2
            y_velocity = -0.0
            # the ROV should move to the depth of the square, if for some reason, the
            # depth is incorrect, the ROV will stop trying to move down after a certain
            # period of time
            if (
                #  abs(self.square_depth - depth) <= EPSILON
                time() - self.start_time
                >= SETTING_DOWN_TIMEOUT
            ):
                self.current_step = CoralState.FINISHED
                #  self.depth_pid.update_set_point(depth - 0.1)
                print("Done!")
        #  elif self.current_step == CoralState.ROCKET_UP:
        #      z_velocity = 0.7

        #      # the ROV should be within 1 cm of the target depth
        #      EPSILON = 0.01

        #      # move on to the next step if the ROV's height is within 1 cm of the target
        #      if abs(self.depth_pid.set_point - depth) <= EPSILON:
        #          self.current_step = CoralState.ROCKET_DOWN
        #          self.depth_pid.update_set_point(depth + 0.1)
        #  elif self.current_step == CoralState.ROCKET_DOWN:
        #      z_velocity = -self.depth_pid.compute(depth)

        #      # the ROV should be within 1 cm of the target depth
        #      EPSILON = 0.01

        #      # move on to the next step if the ROV's height is within 1 cm of the target
        #      if abs(self.depth_pid.set_point - depth) <= EPSILON:
        #          self.current_step = CoralState.FINISHED
        #          print("Moving on Next Step: Approaching Square")

        match self.current_step:
            case CoralState.FINISHED:
                return_code = CoralReturn.FINISHED
            case CoralState.FAILURE:
                return_code = CoralReturn.FAILED
            case _:
                return_code = CoralReturn.IN_PROGRESS

        return (
            x_velocity,
            y_velocity,
            z_velocity,
            yaw_velocity,
            roll_velocity,
            pitch_velocity,
            return_code,
        )


# Find the coordinates and dimensions of the square using YOLO
def find_square(img: np.ndarray, save_image=False) -> (int, int, int, int):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    results = SQUARE_DETECTION_MODEL.predict(
        source=gray, save=False, imgsz=320, verbose=False, max_det=1, half=True
    )
    if len(results) > 0 and len(results[0]) > 0:
        x1, y1, x2, y2 = [round(tensor.item()) for tensor in results[0].boxes.xyxy[0]]
        center_x = round((x2 + x1) / 2)
        center_y = round((y2 + y1) / 2)
        width = x2 - x1
        height = y2 - y1
        if save_image:
            cv2.imwrite(f"./images/{time()}.jpg", img)
            annotated_img = results[0].plot()
            #  cv2.circle(img, (center_x, center_y), 5, (255, 255, 255), -1)
            #  cv2.putText(
            #      img,
            #      "Centroid",
            #      (center_x - 25, center_y - 25),
            #      cv2.FONT_HERSHEY_SIMPLEX,
            #      0.5,
            #      (255, 255, 255),
            #      2,
            #  )
            cv2.imwrite(f"./images/{time()}_annotated.jpg", annotated_img)
        return center_x, center_y, width, height
    else:
        if save_image:
            cv2.imwrite(f"./images/{time()}.jpg", img)

    return None, None, None, None


async def main_loop():
    while True:
        img = ImageHandler.pump_image()
        if img is None:
            await asyncio.sleep(0.01)
            continue

        # find the center of the image
        img_height, img_width = img.shape[:2]
        img_center_x = img_width / 2
        img_center_y = img_height / 2

        x_coord, y_coord, _, _ = find_square(img)
        if x_coord is None or y_coord is None:
            await asyncio.sleep(0.01)
            continue

        # find how far the center of the red object is from the center of the image
        x_error = img_center_x - x_coord
        y_error = img_center_y - y_coord

        print(f"X Error: {x_error} Y Error: {y_error}")

        await asyncio.sleep(0.01)


def main():
    loop = asyncio.get_event_loop()
    ws_server = websockets.serve(WSServer.handler, "0.0.0.0", 3009, ping_interval=None)
    asyncio.ensure_future(ws_server)
    #  print(f"Connected to: {websocket}")
    #  asyncio.ensure_future(ImageHandler.image_handler("ws://localhost:3000"))
    #  asyncio.ensure_future(main_loop())
    loop.run_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
