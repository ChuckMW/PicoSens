import time
from machine import Pin

# LED for status
led = Pin("LED", Pin.OUT)

# Blink LED 3 times to indicate boot
for _ in range(3):
    led.on()
    time.sleep(0.2)
    led.off()
    time.sleep(0.2)

# Delay before starting main app
time.sleep(2)

# Import main app (app.py should be in the same folder)
import app
