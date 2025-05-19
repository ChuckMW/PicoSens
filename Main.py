import network
import socket
import time
import ujson
from random import uniform
from machine import Pin  # Import the Pin class to control the LED

# ====== Access Point Configuration ======
SSID = 'PicoSens'
PASSWORD = 'pico1234'

# Create and configure Access Point
ap = network.WLAN(network.AP_IF)
ap.config(essid=SSID, password=PASSWORD)
ap.active(True)

# Setup the LED pin (assuming GPIO pin 2 is used for the LED)
led = Pin(25, Pin.OUT)

# Function to blink the LED for a given duration
def blink_led(duration, status="ON"):
    if status == "ON":
        led.on()
    else:
        led.off()
    time.sleep(duration)
    led.off()  # Turn off the LED after the blink

print("Starting Access Point...")
while ap.active() == False:
    blink_led(0.5, status="ON")  # Blink LED while waiting for AP to become active
    print("Waiting for AP to be active...")

print("AP Active!")
print("Network config:", ap.ifconfig())

# Blink the LED once when the AP is active
blink_led(1, status="ON")
time.sleep(1)  # Wait for a second to give a clear blink indication

# ====== Simulated Sensor Function ======
def read_sensor():
    # Simulate a 4–20 mA reading
    return round(uniform(4.0, 20.0), 2)

# ====== Load HTML ======
html_page = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>PicoSens Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    /* [Styles same as your original HTML] */
    /* Paste your CSS here */
  </style>
</head>
<body>
  <!-- [Your HTML Body from earlier] -->
</body>
</html>
"""

# ====== Web Server Function ======
def serve():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('Listening on', addr)

    while True:
        try:
            cl, addr = s.accept()
            print('Client connected from', addr)
            request = cl.recv(1024).decode()

            # Blink LED to indicate activity
            blink_led(0.1, status="ON")

            if "GET /data" in request:
                value = read_sensor()
                timestamp = time.strftime("%H:%M:%S", time.localtime())
                response = ujson.dumps({"value": value, "timestamp": timestamp})
                cl.send('HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n')
                cl.send(response)
            else:
                cl.send('HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n')
                cl.send(html_page)

            cl.close()
        except Exception as e:
            print("Error:", e)
            cl.close()

# Start the web server
serve()
