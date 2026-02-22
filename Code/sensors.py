from machine import ADC, Pin
import time

adc0 = ADC(26)
adc1 = ADC(27)
adc2 = ADC(28)
sensors = [adc0, adc1, adc2]

calibration = [{"scale":1.0,"offset":0.0} for _ in sensors]
threshold_high = [2.5,2.5,2.5]
threshold_low  = [0.5,0.5,0.5]

led = Pin("LED", Pin.OUT)

def blink_led(duration=0.1):
    led.on()
    time.sleep(duration)
    led.off()

def read_sensors():
    data = []
    for i, adc in enumerate(sensors):
        raw = adc.read_u16()
        voltage = (raw / 65535) * 3.3
        voltage = voltage * calibration[i]["scale"] + calibration[i]["offset"]
        data.append({"raw":raw,"voltage":voltage})
    return data

def check_thresholds(data):
    for i, s in enumerate(data):
        if s["voltage"] > threshold_high[i]:
            blink_led(0.1)
        elif s["voltage"] < threshold_low[i]:
            blink_led(0.05)

def init_sensors():
    print("Sensors initialized")

