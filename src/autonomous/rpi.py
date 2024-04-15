import asyncio
import cv2
import numpy as np
import websockets


class FrameHandler:
    frame = None

    @classmethod
    async def frame_handler(cls):
        uri = "ws://192.168.1.2:3000"
        async with websockets.connect(uri) as websocket:
            while True:
                message = websocket.recv()
                if message is None:
                    await asyncio.sleep(0.01)
                    continue

                try:
                    buffer = np.asarray(bytearray(message), dtype="uint8")
                    cls.frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
                except Exception as e:
                    print(e)

    @classmethod
    def pump_frame(cls):
        return cls.frame


async def main_loop():
    while True:
        img = FrameHandler.pump_frame()
        if img is None:
            await asyncio.sleep(0.01)
            continue

        img_height, img_width = img.shape[:2]
        img_center_x = img_width / 2
        img_center_y = img_height / 2

        img_blur = cv2.GaussianBlur(img, (9, 9), 0)
        img_hsv = cv2.cvtColor(img_blur, cv2.COLOR_BGR2HSV)

        lower_red1 = np.array([0, 80, 80])
        upper_red1 = np.array([10, 255, 255])

        lower_red2 = np.array([170, 80, 80])
        upper_red2 = np.array([180, 255, 255])

        red_mask1 = cv2.inRange(img_hsv, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(img_hsv, lower_red2, upper_red2)

        red_mask = red_mask1 + red_mask2

        red_img = cv2.cvtColor(
            cv2.bitwise_and(img_hsv, img_hsv, mask=red_mask), cv2.COLOR_HSV2BGR
        )

        gray_img = cv2.cvtColor(red_img, cv2.COLOR_BGR2GRAY)
        ok, thresh = cv2.threshold(gray_img, 1, 255, cv2.THRESH_BINARY)

        moment = cv2.moments(thresh)

        if moment["m00"] != 0:
            x_coord = int(moment["m10"] / moment["m00"])
            y_coord = int(moment["m01"] / moment["m00"])

            x_error = img_center_x - x_coord
            y_error = img_center_y - y_coord

            print(f"X Error: {x_error} Y Error: {y_error}")

        await asyncio.sleep(0.01)


def main():
    loop = asyncio.get_event_loop()
    #  print(f"Connected to: {websocket}")
    asyncio.ensure_future(FrameHandler.frame_handler())
    asyncio.ensure_future(main_loop())
    loop.run_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
