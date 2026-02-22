import network
import time
from machine import Pin
from config import load_config
from debug import log

led = Pin("LED", Pin.OUT)

def start_ap():
    log("Starting AP initialization...")
    cfg = load_config()
    SSID = cfg["wifi"]["ssid"]
    PASSWORD = cfg["wifi"]["password"]

    log("AP SSID: " + SSID)
    log("AP Password: " + PASSWORD)

    ap = network.WLAN(network.AP_IF)
    ap.config(essid=SSID, password=PASSWORD)
    ap.active(True)

    ap.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '8.8.8.8'))
    log("AP ifconfig set")

    while not ap.active():
        log("Waiting for AP to activate...")
        led.on()
        time.sleep(0.2)
        led.off()
        time.sleep(0.2)

    log("AP Active: " + str(ap.ifconfig()))
    return ap

