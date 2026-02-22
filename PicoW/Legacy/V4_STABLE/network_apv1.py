import network
from machine import Pin
import time

led = Pin("LED", Pin.OUT)

def start_ap():
    SSID = "PicoSens"
    PASSWORD = "pico1234"
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=SSID, password=PASSWORD)
    ap.active(True)

    # Wait until AP is active
    while not ap.active():
        led.on()
        time.sleep(0.5)
        led.off()

    print("AP Active:", ap.ifconfig())
    return ap
