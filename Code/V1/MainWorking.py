import network
import socket
import time
import json
from machine import Pin, ADC

# ====== Access Point Configuration ======
SSID = 'PicoSens'
PASSWORD = 'pico1234'

ap = network.WLAN(network.AP_IF)
ap.config(essid=SSID, password=PASSWORD)
ap.active(True)

# ====== LED ======
led = Pin("LED", Pin.OUT)

# ====== MULTIPLE ADC SENSORS ======
adc0 = ADC(26)  # Sensor 1
adc1 = ADC(27)  # Sensor 2
adc2 = ADC(28)  # Sensor 3

def blink_led(duration):
    led.on()
    time.sleep(duration)
    led.off()

def read_all_sensors():
    sensors = []

    for i, adc in enumerate([adc0, adc1, adc2]):
        raw = adc.read_u16()
        voltage = (raw / 65535) * 3.3

        print("SENSOR {} -> Raw: {} | Voltage: {:.3f} V".format(i+1, raw, voltage))

        sensors.append({
            "raw": raw,
            "voltage": voltage
        })

    print("----------------------------------")

    return sensors

# ====== Web Server ======
def serve():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print("Listening on", addr)

    while True:
        try:
            cl, addr = s.accept()
            request = cl.recv(1024).decode()

            blink_led(0.05)

            # ====== SENSOR DATA ======
            if "GET /data" in request:
                sensor_data = read_all_sensors()

                payload = json.dumps({
                    "sensor1": sensor_data[0],
                    "sensor2": sensor_data[1],
                    "sensor3": sensor_data[2]
                })

                cl.send('HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n')
                cl.send(payload)

            # ====== HTML PAGE ======
            elif "GET /" in request:
                cl.send('HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n')
                cl.send(html_content)

            else:
                cl.send('HTTP/1.0 404 Not Found\r\n\r\n')

            cl.close()

        except Exception as e:
            print("Error:", e)
            cl.close()

# ====== HTML Page ======
html_content = """
<!DOCTYPE html>
<html>
<head>
  <title>Pico Multi Sensor</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family:Arial; padding:20px;">

<h1>Pico Multi-Sensor Monitor</h1>

<div>
  Update Interval (ms):
  <input type="number" id="intervalInput" value="2000" min="200" step="200">
  <button onclick="applyInterval()">Apply</button>
</div>

<div style="margin-top:10px;">
  Graph Max Voltage (Y Scale):
  <input type="number" id="scaleInput" value="3.3" min="1" step="0.1">
  <button onclick="applyScale()">Apply</button>
</div>

<hr>

<div>Sensor 1: <span id="s1">--</span></div>
<div>Sensor 2: <span id="s2">--</span></div>
<div>Sensor 3: <span id="s3">--</span></div>

<hr>

<canvas id="graph" width="700" height="350"
        style="border:1px solid #ccc;"></canvas>

<script>
const canvas = document.getElementById("graph");
const ctx = canvas.getContext("2d");

let updateInterval = 2000;
let graphScale = 3.3;
let timer;

const maxPoints = 100;
let data1 = [];
let data2 = [];
let data3 = [];

function applyInterval() {
  updateInterval = parseInt(document.getElementById("intervalInput").value);
  clearInterval(timer);
  timer = setInterval(update, updateInterval);
}

function applyScale() {
  graphScale = parseFloat(document.getElementById("scaleInput").value);
}

function drawGrid() {
  ctx.strokeStyle = "#eee";
  ctx.beginPath();

  for (let i = 0; i <= 10; i++) {
    let y = (i / 10) * canvas.height;
    ctx.moveTo(0, y);
    ctx.lineTo(canvas.width, y);
  }

  ctx.stroke();
}

function drawLine(data, color) {
  ctx.beginPath();
  ctx.strokeStyle = color;

  for (let i = 0; i < data.length; i++) {
    const x = (i / maxPoints) * canvas.width;
    const y = canvas.height - (data[i] / graphScale) * canvas.height;

    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }

  ctx.stroke();
}

function drawGraph() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawGrid();
  drawLine(data1, "red");
  drawLine(data2, "green");
  drawLine(data3, "blue");
}

async function update() {
  try {
    const res = await fetch('/data');
    const data = await res.json();

    const v1 = data.sensor1.voltage;
    const v2 = data.sensor2.voltage;
    const v3 = data.sensor3.voltage;

    document.getElementById('s1').textContent = v1.toFixed(3) + " V";
    document.getElementById('s2').textContent = v2.toFixed(3) + " V";
    document.getElementById('s3').textContent = v3.toFixed(3) + " V";

    data1.push(v1);
    data2.push(v2);
    data3.push(v3);

    if (data1.length > maxPoints) {
      data1.shift();
      data2.shift();
      data3.shift();
    }

    drawGraph();

  } catch (e) {
    console.log("Fetch error:", e);
  }
}

timer = setInterval(update, updateInterval);
update();
</script>

</body>
</html>
"""


# ====== Startup ======
print("Starting Access Point...")
while not ap.active():
    blink_led(0.5)

print("AP Active!")
print("Network config:", ap.ifconfig())
blink_led(1)

serve()
