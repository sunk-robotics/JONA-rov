import asyncio
import cv2 as cv
import numpy as np
import websockets
from websockets.sync.client import connect


class FrameHandler:
    frame = None

    @classmethod
    async def frame_handler(cls, websocket):
        async for message in websocket:
            try:
                cls.frame = cv.imdecode(message, cv.IMREAD_COLOR)
            except Exception as e:
                print(e)

    @classmethod
    def pump_frame(cls):
        return cls.frame


async def main_loop():
    while True:
        img = FrameHandler.pump_frame()

        img_height, img_width = img.shape[:2]
        img_center_x = img_width / 2
        img_center_y = img_height / 2

        img_blur = cv.GaussianBlur(img, (9, 9), 0)
        img_blur = cv.bilateralFilter(img_blur, 9, 75, 75)
        img_hsv = cv.cvtColor(img_blur, cv.COLOR_BGR2HSV)

        lower_red1 = np.array([0, 80, 80])
        upper_red1 = np.array([10, 255, 255])

        lower_red2 = np.array([170, 80, 80])
        upper_red2 = np.array([180, 255, 255])

        red_mask1 = cv.inRange(img_hsv, lower_red1, upper_red1)
        red_mask2 = cv.inRange(img_hsv, lower_red2, upper_red2)

        red_mask = red_mask1 + red_mask2

        red_img = cv.cvtColor(
            cv.bitwise_and(img_hsv, img_hsv, mask=red_mask), cv.COLOR_HSV2BGR
        )

        gray_img = cv.cvtColor(red_img, cv.COLOR_BGR2GRAY)
        ok, thresh = cv.threshold(gray_img, 1, 255, cv.THRESH_BINARY)

        contours, hierarchy = cv.findContours(
            thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE
        )

        moment = cv.moments(thresh)

        if moment["m00"] != 0:
            x_coord = int(moment["m10"] / moment["m00"])
            y_coord = int(moment["m01"] / moment["m00"])

            cv.circle(img, (x_coord, y_coord), 5, (255, 255, 255), -1)
            cv.putText(
                img,
                "Centroid",
                (x_coord - 25, y_coord - 25),
                cv.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2,
            )

            x_error = img_center_x - x_coord
            y_error = img_center_y - y_coord

            print(f"X Error: {x_error}")
            print(f"Y Error: {y_error}")


def main():
    uri = "ws://localhost:3000"
    loop = asyncio.get_event_loop()
    websocket = websockets.connect(uri)
    asyncio.ensure_future(FrameHandler.frame_handler(websocket))
    asyncio.ensure_future(main_loop())
    loop.run_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
