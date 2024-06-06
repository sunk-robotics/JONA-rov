import asyncio
from autonomous import center_of_square
import cv2
import numpy as np
import threading
from time import time
import websockets
from ws_server import WSServer


def process_image(img):
    x_coord, y_coord = center_of_square(img)
    print(f"Coords: {x_coord}, {y_coord}")


class ImageHandler:
    image = None
    is_listening = False
    frame_number = 0
    square_coords = (None, None)
    last_frame_time = 0

    @classmethod
    def process_image(cls, img):
        cls.square_coords = center_of_square(img)
        cls.image = img

    @classmethod
    async def image_handler(cls, uri):
        while True:
            async with websockets.connect(uri) as websocket:
                while True:
                    if not cls.is_listening:
                        await asyncio.sleep(0.001)
                        continue
                    try:
                        message = await websocket.recv()
                    except websockets.ConnectionClosedError:
                        await asyncio.sleep(0.001)
                        break
                    if message is None:
                        await asyncio.sleep(0.001)
                        continue

                    try:
                        buffer = np.asarray(bytearray(message), dtype="uint8")
                        img = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
                        x = threading.Thread(target=cls.process_image, args=(img,))
                        x.start()
                        print(
                            f"Frametime: {(time() - cls.last_frame_time) * 1000:.2f} ms"
                        )
                        cls.last_frame_time = time()
                    except Exception as e:
                        print(e)

                    await asyncio.sleep(0.001)
            await asyncio.sleep(0.001)

    @classmethod
    def pump_image(cls):
        img = cls.image
        square_coords = cls.square_coords
        cls.square_coords = None, None
        cls.image = None
        return img, square_coords

    @classmethod
    def start_listening(cls):
        cls.is_listening = True

    @classmethod
    def stop_listening(cls):
        cls.is_listening = False


async def main_loop():
    while True:
        img, square_coords = ImageHandler.pump_image()
        if img is None:
            await asyncio.sleep(0.001)
            continue

        # find the center of the image
        img_height, img_width = img.shape[:2]
        img_center_x = img_width / 2
        img_center_y = img_height / 2

        #  x_coord, y_coord = center_of_square(img)
        x_coord, y_coord = square_coords[0], square_coords[1]
        #  if x_coord is None or y_coord is None:
        #      await asyncio.sleep(0.001)
        #      continue

        print(f"Square Coords: ({x_coord}, {y_coord})")

        # find how far the center of the red object is from the center of the image
        x_error = img_center_x - x_coord
        y_error = img_center_y - y_coord

        #  print(f"X Error: {x_error} Y Error: {y_error}")

        await asyncio.sleep(0.001)


def main():
    loop = asyncio.get_event_loop()
    #  ws_server = websockets.serve(WSServer.handler, "0.0.0.0", 3009, ping_interval=None)
    #  asyncio.ensure_future(ws_server)
    #  print(f"Connected to: {websocket}")
    asyncio.ensure_future(ImageHandler.image_handler("ws://192.168.1.9:3000"))
    ImageHandler.start_listening()
    asyncio.ensure_future(main_loop())
    loop.run_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
