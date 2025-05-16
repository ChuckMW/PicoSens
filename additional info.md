




> ⚠️ Note: 4 mA = 0.66 V, 20 mA = 3.3 V with 165 Ω resistor (safe for Pico ADC)

---

## 🧠 MicroPython Code Example

```python
from machine import ADC, Pin
import time

adc = ADC(26)  # GP26 = ADC0

V_REF = 3.3      # Pico ADC reference voltage
R = 165          # Resistor in ohms

def read_current():
    raw = adc.read_u16()
    voltage = (raw / 65535) * V_REF
    current_mA = (voltage / R) * 1000  # Convert A to mA
    return round(current_mA, 2)

def current_to_psi(current_mA):
    if current_mA < 4:
        return 0
    psi = ((current_mA - 4) / 16) * 100  # Scale to 0–100 PSI
    return round(psi, 1)

while True:
    current = read_current()
    psi = current_to_psi(current)
    print(f"Current: {current} mA, Pressure: {psi} PSI")
    time.sleep(1)






🌐 Web Dashboard (MicroPython + HTML)
You can use microdot or picoweb in MicroPython to serve a basic HTML dashboard. Here's a minimal example for microdot:

from microdot import Microdot
from machine import ADC
import time

app = Microdot()
adc = ADC(26)
R = 165
V_REF = 3.3

def read_current():
    voltage = adc.read_u16() * V_REF / 65535
    return round((voltage / R) * 1000, 2)

@app.route('/')
def index(request):
    current = read_current()
    html = f"""
    <html>
        <head><title>Industrial Sensor</title></head>
        <body>
            <h1>4–20 mA Sensor Dashboard</h1>
            <p>Current: {current} mA</p>
        </body>
    </html>
    """
    return html, 200, {'Content-Type': 'text/html'}

app.run(debug=True)






📈 Optional: Real-Time Graphing with Chart.js
Embed Chart.js in the HTML and fetch live data via an API route (/data). Here’s an outline:

Use AJAX or JavaScript fetch() to poll /data

Format response as JSON

Update chart every 5–10 seconds

🔒 Industrial Reliability Tips
Use shielded cables and twisted pair for sensor lines

Add TVS diode or buffer op-amp for surge protection

Use precision resistors (0.1% tolerance)

Consider ADS1115 (16-bit ADC) for better resolution

Enclose in DIN-rail case or IP-rated box for field use

📦 Expansion Ideas
Add SD card logging with time-stamped entries

Add configuration page for setting min/max thresholds

Support multiple 4–20 mA inputs with multiplexing

Push data to cloud via MQTT or HTTP POST

Add offline mode with syncing when reconnected


