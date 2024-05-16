import asyncio
import cv2
from enum import auto, Enum
from pid import PID, RotationalPID
import numpy as np
from sklearn.linear_model import LinearRegression
from time import time
import websockets
import math
from scipy.interpolate import splprep, splev
from timer import Timer


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
    is_listening = False

    @classmethod
    async def image_handler(cls, uri):
        while True:
            async with websockets.connect(uri) as websocket:
                while True:
                    if not cls.is_listening:
                        await asyncio.sleep(0.01)
                        continue
                    try:
                        message = await websocket.recv()
                    except websockets.ConnectionClosedError:
                        await asyncio.sleep(0.01)
                        break
                    if message is None:
                        await asyncio.sleep(0.01)
                        continue

                    try:
                        buffer = np.asarray(bytearray(message), dtype="uint8")
                        cls.image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
                    except Exception as e:
                        print(e)

                    await asyncio.sleep(0.01)
            await asyncio.sleep(0.01)

    @classmethod
    def pump_image(cls):
        return cls.image

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
    SETTING_DOWN = 8
    FINISHED = 9
    # other states
    FAILURE = auto()


class CoralReturn(Enum):
    FAILED = -1
    FINISHED = 0
    IN_PROGRESS = 1


class CoralTransplanter:
    def __init__(self, pool_floor_depth: float, yaw_angle: int):
        # the red square is at a height of about 32 cm above the pool floor
        self.SQUARE_HEIGHT = 0.32
        # the ROV should be 75 cm above the pool floor when searching for the square
        self.LOCATING_HEIGHT = 0.75
        # the ROV should be 8 cm above the height of the square when moving towards it
        self.MOVING_HEIGHT = self.SQUARE_HEIGHT + 0.06

        # after the red square is no longer in the ROV's vision, the ROV should continue
        # moving for another second
        self.BLIND_MOVING_TIME = 1
        # if the ROV takes longer than 3 seconds to reach the target depth, assume that
        # the depth is slightly off and stop attempting
        self.SETTING_DOWN_TIMEOUT = 3

        self.pool_floor_depth = pool_floor_depth
        self.square_depth = pool_floor_depth - self.SQUARE_HEIGHT
        self.locating_depth = pool_floor_depth - self.LOCATING_HEIGHT
        self.moving_depth = pool_floor_depth - self.MOVING_HEIGHT

        self.square_coords = None
        self.prev_square_coords = []

        self.NUM_VERIFICATIONS = 30
        self.verify_count = 0

        # the roll and pitch anchor should always be on
        self.roll_anchor = True
        self.pitch_anchor = True

        self.yaw_pid = RotationalPID(
            proportional_gain=0.025, integral_gain=0, derivative_gain=0
        )
        # the ROV should stay parallel to the pool floor
        self.roll_pid = RotationalPID(
            0, proportional_gain=-0.03, integral_gain=-0.001, derivative_gain=0.0e-4
        )
        self.pitch_pid = RotationalPID(
            0, proportional_gain=0.02, integral_gain=0.007, derivative_gain=0.005
        )
        self.depth_pid = PID(
            proportional_gain=2, integral_gain=0.05, derivative_gain=0.01
        )

        self.square_x_pid = PID(
            proportional_gain=-0.0001, integral_gain=0, derivative_gain=0
        )
        self.square_y_pid = PID(
            proportional_gain=0.1, integral_gain=0, derivative_gain=0
        )

        self.approaching_timer = Timer()
        self.estimation_timer = Timer()

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

        img = ImageHandler.pump_image()
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

        print(self.current_step)
        print(f"Yaw Set Point: {self.yaw_pid.set_point}")
        print(f"Yaw: {yaw}")

        if self.current_step == CoralState.STARTING:
            self.depth_pid.update_set_point(self.moving_depth)
            print(f"Moving Depth: {self.moving_depth}")
            # keep the ROV's yaw locked
            self.yaw_pid.update_set_point(yaw)
            self.current_step = CoralState.MOVING_UP
            print("Moving on Next Step: Moving Up")

        # step 1 is to move up to a few centimeters above the red square
        elif self.current_step == CoralState.MOVING_UP:
            z_velocity = self.depth_pid.compute(depth)
            yaw_velocity = self.yaw_pid.compute(yaw)

            # the ROV should be within 1 cm of the target depth
            EPSILON = 0.01

            # move on to the next step if the ROV's height is within 1 cm of the target
            if abs(self.moving_depth - depth) <= EPSILON:
                self.current_step = CoralState.APPROACHING_SQUARE
                self.approaching_timer.restart()
                print("Moving on Next Step: Approaching Square")

        # step 2 is to approach the square blindly until the square comes into view
        # Main Failure Condition: Square is not identified after moving for 15 seconds
        # Result: Abandon attempt
        # Non-Ideal but Non-Failure Condition: False positive
        # Result: Verify the square's existence
        elif self.current_step == CoralState.APPROACHING_SQUARE:
            z_velocity = self.depth_pid.compute(depth)
            yaw_velocity = self.yaw_pid.compute(yaw)
            y_velocity = 0.2

            if timer.read() > 15:
                self.curent_step = CoralState.FAILURE
                print("Couldn't Find Square!")
                return (0, 0, 0, 0, 0, 0, CoralReturn.FAILED)

            x_coord, y_coord = center_of_red(img, save_image=True)
            # may want to implement something to make sure the x and y coords are stable
            # to prevent the algorithm from latching onto some random red object

            if x_coord is not None and y_coord is not None:
                print("Found square!")
                self.prev_square_coords = []

                self.approaching_timer.stop()
                self.current_step = CoralState.VERIFYING_SQUARE
                print("Moving on Next Step: Verifying Square")
        # step 3 is to make sure the red square that the ROV detected is actually the
        # square
        elif self.current_step == CoralState.VERIFYING_SQUARE:
            z_velocity = self.depth_pid.compute(depth)
            yaw_velocity = self.yaw_pid.compute(yaw)
            y_velocity = -0.1


            x_coord, y_coord = center_of_red(img)
            if self.verify_count < self.NUM_VERIFICATIONS:
                if x_coord is not None and y_coord is not None:
                    self.prev_square_coords.append((x_coord, y_coord, time()))
                else:
                    self.prev_square_coords.append((None, None, time()))
                self.verify_count += 1
            else:
                coords_np_array = np.array(self.prev_square_coords)
                std_dev_x = np.std(coords_np_array, axis=0)
                std_dev_y = np.std(coords_np_array, axis=1)

                num_not_found = reduce(lambda c: int(c[0] is None and c[1] is None), self.prev_square_coords)
                # to verify the square's existence, the square should be visible for
                # over 90% of the time, and vary too much in its location (given that
                # the ROV is supposed to be stationary)
                if num_not_found > len(self.prev_square_coords) * 0.1 or std_dev_x > 50 or std_dev_y > 50:
                    self.verify_count = 0
                    self.current_step = CoralState.APPROACHING_SQUARE
                    self.approaching_timer.start()
                else:
                    print("Verified!")
                    self.prev_square_coords = []
                    self.current_step = CoralState.CENTERING_SQUARE

        # step 4 is to center the square in the ROV's vision
        elif self.current_step == CoralState.CENTERING_SQUARE:
            z_velocity = self.depth_pid.compute(depth)
            
            x_coord, y_coord = center_of_red(img)

            if x_coord is not None and y_coord is not None:
                self.prev_square_coords.append((x_coord, y_coord, time()))
                yaw_velocity = self.square_x_pid.compute(x_coord)
            # it's possible the square might be temporarily invisible,if there's enough
            # data points to work with, use a linear regression to estimate the position
            # of the square
            elif len(self.prev_square_coords) > 3 and self.estimating_timer.read() < 1:
                prev_x_coords = np.array(
                    [c[0] for c in self.prev_square_coords]
                ).reshape((-1, 1))
                prev_times = [c[2] for c in self.prev_square_coords]
                print(f"X Coords: {prev_x_coords}")
                print(f"Times: {prev_times}")
                # performs a linear regression on the data to approximate a function
                # for the x coordinate given a time
                model = LinearRegression().fit(prev_x_coords, prev_times)
                # estimates the x coord given the current time
                approx_x_coord = model.coef_ * time.time() + model.intercept_
                yaw_velocity = self.square_x_pid.compute(approx_x_coord)

            # if there's not enough data points to work with, go back and verify the
            # square's existence
            else:
                self.prev_square_coords = []
                self.current_step = CoralState.VERIFYING_SQUARE

        
        # step 6 is to continue approaching the square, keeping the square centered
        # horizontally in the ROV's vision, until the square falls off the bottom of the
        # screen
        elif self.current_step == CoralState.ARRIVING_AT_SQUARE:
            EPSILON = 50

            z_velocity = self.depth_pid.compute(depth)
            #  yaw_velocity = self.yaw_pid.compute(yaw)
            y_velocity = 0.2

            x_coord, y_coord = center_of_red(img)
            if x_coord is not None and y_coord is not None:
                print(f"Coords: ({x_coord}, {y_coord})")
                center_of_red(img, save_image=True)
                self.prev_square_coords.append((x_coord, y_coord, time()))
                #  self.square_x_pid.update_set_point(img_center_x)
                yaw_velocity = self.square_x_pid.compute(x_coord)

            # check if the square disappeared off the bottom of the screen
            elif len(self.prev_square_coords) > 10:
                prev_y_coords = np.array(
                    [c[1] for c in self.prev_square_coords]
                ).reshape((-1, 1))
                prev_times = [c[2] for c in self.prev_square_coords]
                print(f"Y Coords: {prev_y_coords}")
                print(f"Times: {prev_times}")
                # performs a linear regression on the data to approximate a function
                # for the y coordinate given a time
                model = LinearRegression().fit(prev_y_coords, prev_times)
                # estimates the x coord given the current time
                predicted_y_coord = model.coef_ * time() + model.intercept_
                #  predicted_y_coord = model.predict(time())
                if predicted_y_coord > img_height - EPSILON:
                    self.start_time = time()
                    self.current_step = CoralState.MOVING_BLINDLY

            # if there haven't already been 10 recorded coordinates, go back and verify that the square exists
            else:
                print("Where'd it go?")
                self.current_step = CoralState.VERIFYING_SQUARE

        # after the red square is no longer visible, the ROV should continue moving
        # so that the coral sample aligns with the square
        elif self.current_step == CoralState.MOVING_BLINDLY:
            z_velocity = self.depth_pid.compute(depth)
            y_velocity = 0.2

            if time() - self.start_time >= self.BLIND_MOVING_TIME:
                self.start_time = time()
                self.current_step = CoralState.SETTING_DOWN
                print("Moving on Next Step: Setting Down")

        # step 8 is to set the coral head down on the red square
        elif self.current_step == CoralState.SETTING_DOWN:
            # the ROV should be within 1 cm of the target depth
            EPSILON = 1
            z_velocity = -0.5
            # the ROV should move to the depth of the square, if for some reason, the
            # depth is incorrect, the ROV will stop trying to move down after a certain
            # period of time
            if (
                abs(self.square_depth - depth) <= EPSILON
                or time() - self.start_time >= self.SETTING_DOWN_TIMEOUT
            ):
                self.current_step = CoralState.FINISHED
                print("Done!")

        match self.current_step:
            case CoralState.FINISHED:
                return_code = CoralReturn.FINISHED
            case CoralState.FAILURE
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


# Smooth a contour and make it solid
def smooth_contour(contour: np.ndarray) -> np.ndarray:
    x, y = contour.T
    x = x.tolist()[0]
    y = y.tolist()[0]
    tck, u = splprep([x, y], u=None, s=1.0, per=1)
    u_new = np.linspace(u.min(), u.max(), 100)
    x_new, y_new = splev(u_new, tck, der=0)
    res_array = [[[int(i[0]), int(i[1])]] for i in zip(x_new, y_new)]
    return np.asarray(res_array, dtype=np.int32)


# Remove the horkfook from the image, which often interferes with the image
# segmentation algorithm. Image must be HSV (Hue, Saturation, Value).
def filter_out_hork(img: np.ndarray) -> np.ndarray:
    lower_orange = np.array([13, 10, 10])
    upper_orange = np.array([35, 255, 255])
    orange_mask = cv2.inRange(img, lower_orange, upper_orange)
    # turn all parts of the image that aren't orange into black
    orange_img = cv2.bitwise_and(img, img, mask=orange_mask)
    gray_img = cv2.split(orange_img)[2]
    ok, thresh = cv2.threshold(gray_img, 1, 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)

    # find the contours of the two hooks
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    hook_contours = sorted(contours, key=cv2.contourArea, reverse=True)[0:2]
    if len(hook_contours) < 2:
        print("Unable to filter out hork!")
        return img
    smoothened_contours = [
        smooth_contour(hook_contours[0]),
        smooth_contour(hook_contours[1]),
    ]

    mask = np.zeros_like(thresh)
    cv2.drawContours(mask, smoothened_contours, -1, 255, -1)
    # dilate the mask to remove the pixels around the edges of the hooks that
    # like to cause problems
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=2)
    cv2.bitwise_not(mask, mask)

    return cv2.bitwise_and(img, img, mask=mask)


def filter_contours(contours: np.ndarray, iter_num: int) -> bool:
    filtered_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        _, _, width, height = cv2.boundingRect(contour)
        aspect_ratio = width / height if height != 0 else math.inf

        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)

        solidity = area / hull_area if hull_area != 0 else math.inf

        if (
            area > 100 / (iter_num + 1)
            and area < 10_000 / (iter_num + 1)
            and aspect_ratio > 0.8
            and solidity > 0.5
        ):
            filtered_contours.append(contour)

    return filtered_contours


# find the x and y coordinates of the center of a red object in the image
def center_of_red(img: np.ndarray, save_image=False) -> (int, int):
    if img is None:
        return None, None

    # blurring helps reduce noise that might confuse the algorithm
    img_blur = cv2.GaussianBlur(img, (9, 9), 0)

    # crop out part of the top, left, and right sides of the image to remove
    # interference from reflections and other irrelevant parts of the image
    img_width = img.shape[1]
    img_height = img.shape[0]
    mask = np.zeros(img.shape[:2], dtype="uint8")

    cv2.rectangle(
        mask,
        (0, int(img_height / 4)),
        (int(img_width * (4 / 5)), img_height),
        255,
        -1,
    )
    cropped_img = cv2.bitwise_and(img_blur, img_blur, mask=mask)

    # converting to HSV (Hue, Saturation, Value) makes it easier to identify a range
    # of possible red values
    img_hsv = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2HSV)

    largest_contour = None
    # red light attenuates very quickly underwater, so the farther the ROV is
    # away from the square, the grayer/browner the square becomes, so gradually
    # increase the range of colors until the square can be found
    for i in range(0, 5):
        filter_img = filter_out_hork(img_hsv) if i > 3 else img_hsv
        lower_red = np.array([0, 10, 10])
        upper_red = np.array([i * 5 + 10, 255, 150])
        red_mask = cv2.inRange(filter_img, lower_red, upper_red)

        # turn all parts of the image that aren't red into black
        red_img = cv2.bitwise_and(filter_img, filter_img, mask=red_mask)

        # turn the image into a binary (black and white) image, where the white parts
        # represent anything red, and the black parts represent anything not red
        gray_img = cv2.split(red_img)[2]
        _, thresh = cv2.threshold(gray_img, 1, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        #  for contour in contours:
        #      area = cv2.contourArea(contour)
        #      print(f"Contour Area: {area}")

        #      x, y, w, h = cv2.boundingRect(contour)
        #      aspect_ratio = w / h if h != 0 else math.inf
        #      print(f"Aspect Ratio: {aspect_ratio}")

        #      hull = cv2.convexHull(contour)
        #      hull_area = cv2.contourArea(hull)

        #      solidity = area / hull_area if hull_area != 0 else math.inf

        #      print(f"Solidity: {solidity}")

        # filter out any contours that don't match the shape of the square
        filtered_contours = filter_contours(contours, i)

        if len(filtered_contours) > 0:
            largest_contour = max(filtered_contours, key=cv2.contourArea)
            break

    if largest_contour is None:
        return None, None

    moment = cv2.moments(largest_contour)
    if moment["m00"] == 0:
        print("shit")
        return None, None

    x_coord = int(moment["m10"] / moment["m00"])
    y_coord = int(moment["m01"] / moment["m00"])
    if save_image:
        cv2.circle(img, (x_coord, y_coord), 5, (255, 255, 255), -1)
        cv2.putText(
            img,
            "Centroid",
            (x_coord - 25, y_coord - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2,
        )
        cv2.imwrite(f"./images/{time()}.jpg", img)
    return x_coord, y_coord


def simplify_contour(contour, n_corners=4):
    """
    Binary searches best `epsilon` value to force contour
        approximation contain exactly `n_corners` points.

    :param contour: OpenCV2 contour.
    :param n_corners: Number of corners (points) the contour must contain.

    :returns: Simplified contour in successful case. Otherwise returns initial contour.
    """
    n_iter, max_iter = 0, 100
    lb, ub = 0.0, 1.0

    while True:
        n_iter += 1
        if n_iter > max_iter:
            return contour

        k = (lb + ub) / 2.0
        eps = k * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, eps, True)

        if len(approx) > n_corners:
            lb = (lb + ub) / 2.0
        elif len(approx) < n_corners:
            ub = (lb + ub) / 2.0
        else:
            return approx


# gets the coordinates of the four corners of the largest red square in an image
# returns None if corners can't be found
def find_corners(image):
    img_blur = cv2.GaussianBlur(image, (9, 9), 0)
    img_hsv = cv2.cvtColor(img_blur, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 80, 80])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 80, 80])
    upper_red2 = np.array([180, 255, 255])

    red_mask1 = cv2.inRange(img_hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(img_hsv, lower_red2, upper_red2)

    red_mask = red_mask1 + red_mask2

    # turn all parts of the image that aren't red into black
    red_img = cv2.cvtColor(
        cv2.bitwise_and(img_hsv, img_hsv, mask=red_mask), cv2.COLOR_HSV2BGR
    )

    gray = cv2.cvtColor(red_img, cv2.COLOR_BGR2GRAY)
    # filter to remove noise from the edges that can result in the contours becoming
    # jagged
    filtered_gray = cv2.bilateralFilter(gray, 9, 75, 75)
    # turn image into a binary (black and white) image
    thresh = cv2.threshold(filtered_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[
        1
    ]

    # apply morphology
    kernel = np.ones((7, 7), np.uint8)
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)

    # get largest contour
    contours = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    area_thresh = 0
    big_contour = None
    for c in contours:
        area = cv2.contourArea(c)
        if area > area_thresh:
            area_thresh = area
            big_contour = c

    if big_contour is None:
        return None
    # simplify the shape of the contour to a quadrilateral
    quad_contour = simplify_contour(big_contour)
    # get perimeter and approximate a polygon
    peri = cv2.arcLength(quad_contour, True)
    corners = cv2.approxPolyDP(quad_contour, 0.02 * peri, True)

    if len(corners) != 4:
        return None

    corners = np.resize(corners, (4, 2))
    keys = (corners[:, 0], corners[:, 1])

    # Indices for sorted array
    sorted_indices = np.lexsort(keys)

    # Apply array indexing to obtain sorted array
    corners = corners[sorted_indices]

    top_corners = corners[0:2]
    keys = (top_corners[:, 1], top_corners[:, 0])
    sorted_indices = np.lexsort(keys)
    top_corners = top_corners[sorted_indices]

    bottom_corners = corners[2:4]
    keys = (bottom_corners[:, 1], bottom_corners[:, 0])
    sorted_indices = np.lexsort(keys)
    bottom_corners = bottom_corners[sorted_indices]

    corners = np.append(top_corners, bottom_corners, axis=0)

    print(f"Sorted Corners: {corners}")

    return corners.astype(np.float32)


def distance_from_square(img):
    CAMERA_MATRIX = np.array(
        [
            (2.1484589086606215e03, 0, 8.8823443046428349e02),
            (0, 2.1553101552978601e03, 6.1716956646878486e02),
            (0, 0, 1),
        ]
    )
    DIST_COEFFS = np.array(
        [
            (
                -0.81642321343572366,
                1.5568737137734159,
                -0.0042440573440693579,
                -0.0022688996764112274,
                -2.1523633613219233,
            )
        ]
    )
    points_3d = np.array(
        [[-7.5, 7.5, 0], [7.5, 7.5, 0], [7.5, -7.5, 0], [-7.5, -7.5, 0]], dtype="single"
    )

    corners = find_corners(img)
    points_2d = np.array([corners[2], corners[3], corners[1], corners[0]])

    if points_2d is not None:
        ok, rotation_vec, translation_vec = cv2.solvePnP(
            points_3d,
            points_2d,
            CAMERA_MATRIX,
            DIST_COEFFS,
            flags=cv2.SOLVEPNP_IPPE_SQUARE,
        )

        return translation_vec[2]


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

        x_coord, y_coord = center_of_red(img)
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
