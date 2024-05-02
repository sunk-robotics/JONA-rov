#!/usr/bin/python
from picamera2 import Picamera2
from picamera2.outputs import FileOutput
from picamera2.encoders import MJPEGEncoder
import io
import asyncio
from libcamera import controls, Rectangle
from websockets import serve, ConnectionClosed


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None

    def write(self, buf):
        self.frame = buf


class WSServer:
    output = StreamingOutput()

    @classmethod
    async def handler(cls, websocket, path):
        print("Client connected!")
        try:
            while True:
                if cls.output.frame is None:
                    await asyncio.sleep(0.001)
                    continue

                await websocket.send(bytearray(cls.output.frame))
                await asyncio.sleep(0.001)

        except ConnectionClosed:
            print("Client disconnected!")


def main():
    picam2 = Picamera2()
    print(picam2.sensor_modes)
    config = picam2.create_video_configuration(main={"size": (854, 480)}, raw={"size": (1920, 1080)})
    # config = picam2.create_video_configuration(main={"size": (1280, 720)})
    picam2.configure(config)
    picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous, "AeEnable": True, "AwbEnable": True, "AwbMode": controls.AwbModeEnum.Indoor})
    picam2.start_recording(MJPEGEncoder(25_000_000),
                           FileOutput(WSServer.output))

    loop = asyncio.get_event_loop()
    ws_server = serve(
        WSServer.handler, "0.0.0.0", 3000, ping_interval=None
    )
    print("Server started!")
    asyncio.ensure_future(ws_server)
    loop.run_forever()


if __name__ == "__main__":
    main()
