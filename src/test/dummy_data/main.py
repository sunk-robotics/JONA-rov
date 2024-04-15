#!/bin/python
import asyncio
import json
import websockets
from ws_server import WSServer
import math


async def main_server():
   
    delta_time = 0
    depth_anchor = False
    yaw_anchor = False
    roll_anchor = False
    pitch_anchor = False
    speed_multiplier = 1
    motor_lock = False
    locked_velocities = {
        "x_velocity": 0,
        "y_velocity": 0,
        "z_velocity": 0,
        "yaw_velocity": 0,
        "pitch_velocity": 0,
        "roll_velocity": 0,
    }
    
    prev_speed_toggle = None
    prev_depth_anchor_toggle = None
    prev_roll_anchor_toggle = None
    prev_pitch_anchor_toggle = None
    prev_yaw_anchor_toggle = None
    prev_motor_lock_toggle = None

    print("Server started!")
    while True:
        delta_time += 0.01

        # read fake sensor information
        internal_temp = (math.sin(delta_time / 1000) / 2 + 0.5) * 100
        external_temp = (math.sin(delta_time / 1000) / 2 + 0.5) * 100
        depth = (math.sin(delta_time / 100) / 2 + 0.5) * 10
        yaw = (math.sin(delta_time / 100) / 2 + 0.5) * 360
        roll = (math.sin(delta_time / 100) / 2 + 0.5) * 360
        pitch = (math.sin(delta_time / 100) / 2 + 0.5) * 360
        x_accel = (math.sin(delta_time / 100) / 2 + 0.5)
        y_accel = (math.sin(delta_time / 100) / 2 + 0.5)
        z_accel = (math.sin(delta_time / 100) / 2 + 0.5)
        voltage_5V = (math.sin(delta_time / 100) / 2 + 0.5) 
        current_5V = (math.sin(delta_time / 100) / 2 + 0.5)
        voltage_12V = (math.sin(delta_time / 100) / 2 + 0.5)
        current_12V = (math.sin(delta_time / 100) / 2 + 0.5)

        # send fake data to web client
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
                "voltage_12V": voltage_12V,
                "current_12V": current_12V,
                "speed_multiplier": speed_multiplier,
                "depth_anchor_enabled": depth_anchor,
                "yaw_anchor_enabled": yaw_anchor,
                "roll_anchor_enabled": roll_anchor,
                "pitch_anchor_enabled": pitch_anchor,
                "motor_lock_enabled": motor_lock,
            }
            await WSServer.web_client_main.send(json.dumps(status_info))

        await asyncio.sleep(0.01)


def main():
    loop = asyncio.get_event_loop()
    ws_server = websockets.serve(WSServer.handler, "0.0.0.0", 8765, ping_interval=None)
    asyncio.ensure_future(ws_server)
    asyncio.ensure_future(main_server())
    loop.run_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("")
