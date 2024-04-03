import time
from gpiozero import PWMLED

led = PWMLED(4)

for i in range(1, 11):
    print(f"Duty Cycle: {i * 10}%")
    led.value = i / 10
    time.sleep(1)
