import asyncio
import cv2
import numpy as np
import websockets


class FrameHandler:
    frame = None
    is_listening = False

    @classmethod
    async def frame_handler(cls, uri):
        #  uri = "ws://192.168.1.2:3000"
        #  uri = "ws://localhost:3000"
        async with websockets.connect(uri) as websocket:
            while True:
                if not cls.is_listening:
                    await asyncio.sleep(0.01)
                    continue
                message = await websocket.recv()
                if message is None:
                    await asyncio.sleep(0.01)
                    continue

                try:
                    buffer = np.asarray(bytearray(message), dtype="uint8")
                    cls.frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
                except Exception as e:
                    print(e)

                await asyncio.sleep(0.01)

    @classmethod
    def pump_frame(cls):
        return cls.frame

    @classmethod
    def start_listening(cls):
        cls.is_listening = True

    @classmethod
    def stop_listening(cls):
        cls.is_listening = False


# find the x and y coordinates of the center of a red object in the image
def center_of_red(img: np.ndarray) -> (int, int):
    if img is None:
        return None, None

    # blurring helps reduce noise that might confuse the algorithm
    img_blur = cv2.GaussianBlur(img, (9, 9), 0)

    # converting to HSV (Hue, Saturation, Value) makes it easier to identify a range
    # of possible red values
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

    # turn the image into a binary (black and white) image, where the white parts
    # represent anything red, and the black parts represent anything not red
    gray_img = cv2.cvtColor(red_img, cv2.COLOR_BGR2GRAY)
    ok, thresh = cv2.threshold(gray_img, 1, 255, cv2.THRESH_BINARY)

    # find the center of the red object
    moment = cv2.moments(thresh)

    if moment["m00"] == 0:
        return None, None
    # find the coordinates of the center of the red object
    x_coord = int(moment["m10"] / moment["m00"])
    y_coord = int(moment["m01"] / moment["m00"])

    return x_coord, y_coord


async def main_loop():
    while True:
        img = FrameHandler.pump_frame()
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
    #  print(f"Connected to: {websocket}")
    asyncio.ensure_future(FrameHandler.frame_handler("ws://localhost:3000"))
    asyncio.ensure_future(main_loop())
    loop.run_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
