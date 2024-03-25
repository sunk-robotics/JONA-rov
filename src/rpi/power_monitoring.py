import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import time


class PowerMonitor:
    def __init__(self):
        ads = ADS.ADS1015(busio.I2C(board.SCL, board.SDA))
        ads.gain = 2 / 3
        self.ads_range = 4.096 / ads.gain
        self.channel0 = AnalogIn(ads, ADS.P0)
        self.channel1 = AnalogIn(ads, ADS.P1)
        self.channel2 = AnalogIn(ads, ADS.P2)
        self.channel3 = AnalogIn(ads, ADS.P3)

    def voltage_5V(self) -> float:
        return self.channel1.value / 2**15 * self.ads_range

    def current_5V(self) -> float:
        return (
            73.3 * self.channel3.value / 2**15 * self.ads_range / self.voltage_5V()
            - 36.7
        )

    def voltage_12V(self) -> float:
        return self.channel0.value / 2**15 * self.ads_range * 4

    def current_12V(self) -> float:
        return (
            73.3 * self.channel2.value / 2**15 * self.ads_range / self.voltage_5V()
            - 36.7
        )


def main():
    while True:
        power_monitor = PowerMonitor()

        print(f"5V Rail Voltage: {power_monitor.voltage_5V():.2f}V")
        print(f"12V Rail Voltage: {power_monitor.voltage_12V():.2f}V")
        print(f"5V Rail Current: {power_monitor.current_5V():.2f}A")
        print(f"12V Rail Current: {power_monitor.current_12V():.2f}A")

        time.sleep(0.1)


if __name__ == "__main__":
    main()
