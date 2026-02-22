from machine import ADC, Pin
import time
from config import load_config
from debug import log

cfg = load_config()

log("Initializing sensors...")

adc0 = ADC(26)
adc1 = ADC(27)
adc2 = ADC(28)
sensors = [adc0, adc1, adc2]

calibration = cfg["sensors"]["calibration"]
threshold_high = cfg["sensors"]["threshold_high"]
threshold_low  = cfg["sensors"]["threshold_low"]

led = Pin("LED", Pin.OUT)

def blink_led(duration=0.1):
    log(f"Blink LED for {duration}s")
    led.on()
    time.sleep(duration)
    led.off()

def read_sensors():
    log("Reading sensors...")
    data = []
    for i, adc in enumerate(sensors):
        raw = adc.read_u16()
        voltage = (raw / 65535) * 3.3
        voltage = voltage * calibration[i]["scale"] + calibration[i]["offset"]
        log(f"Sensor {i}: raw={raw}, voltage={voltage}")
        data.append({"raw":raw,"voltage":voltage})
    return data

def check_thresholds(data):
    log("Checking thresholds...")
    for i, s in enumerate(data):
        if s["voltage"] > threshold_high[i]:
            log(f"Sensor {i} HIGH threshold exceeded")
            blink_led(0.1)
        elif s["voltage"] < threshold_low[i]:
            log(f"Sensor {i} LOW threshold exceeded")
            blink_led(0.05)

def init_sensors():
    log("Sensors initialized")

