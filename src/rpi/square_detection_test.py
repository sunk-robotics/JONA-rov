import asyncio
from autonomous import center_of_square
import cv2
import numpy as np
import websockets
from ws_server import WSServer


class ImageHandler:
    image = None
    is_listening = False
    frame_number = 0
    square_coords = (None, None)

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
                        #  cls.image = cv2.resize(
                        #      img, (426, 240), interpolation=cv2.INTER_LINEAR
                        #  )
                        #  if cls.frame_number % 10 == 0:
                        #      cls.image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
                        #      cls.square_coords = center_of_square(cls.image)
                        #  cls.frame_number += 1
                    except Exception as e:
                        print(e)

                    await asyncio.sleep(0.01)
            await asyncio.sleep(0.01)

    @classmethod
    def pump_image(cls):
        img = cls.image
        cls.image = None
        return img

    @classmethod
    def start_listening(cls):
        cls.is_listening = True

    @classmethod
    def stop_listening(cls):
        cls.is_listening = False


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

        x_coord, y_coord = center_of_square(img)
        if x_coord is None or y_coord is None:
            await asyncio.sleep(0.01)
            continue

        print(f"Square Coords: ({x_coord}, {y_coord})")

        # find how far the center of the red object is from the center of the image
        x_error = img_center_x - x_coord
        y_error = img_center_y - y_coord

        #  print(f"X Error: {x_error} Y Error: {y_error}")

        await asyncio.sleep(0.01)


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
