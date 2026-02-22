import network
from machine import Pin
import time

led = Pin("LED", Pin.OUT)

def start_ap():
    SSID = "PicoSens"
    PASSWORD = "pico1234"

    # Initialize Access Point
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=SSID, password=PASSWORD)
    ap.active(True)

    # Optionally set static IP/subnet (DHCP server still works)
    ap.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '8.8.8.8'))

    print("Starting AP...")
    # Blink LED while AP is activating
    while not ap.active():
        led.on()
        time.sleep(0.3)
        led.off()

    led.off()
    print("AP Active:", ap.ifconfig())
    print("DHCP server running for connected clients")
    return ap

# Example usage
if __name__ == "__main__":
    ap = start_ap()
    # AP is now running and clients can connect via DHCP

