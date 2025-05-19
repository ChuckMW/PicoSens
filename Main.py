import network
import socket
import time
from machine import Pin  # Import the Pin class to control the LED

# ====== Access Point Configuration ======
SSID = 'PicoSens'
PASSWORD = 'pico1234'

# Create and configure Access Point
ap = network.WLAN(network.AP_IF)
ap.config(essid=SSID, password=PASSWORD)
ap.active(True)

# Setup the LED pin (assuming GPIO pin 25 is used for the LED)
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

# ====== Simple Web Page HTML ======
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>PicoSens Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, sans-serif;
      background: #f0f2f5;
      padding: 20px;
      margin: 0;
    }

    .container {
      max-width: 850px;
      margin: auto;
    }

    .card {
      background: #fff;
      padding: 20px;
      margin-bottom: 20px;
      border-radius: 10px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }

    h1, h2 {
      font-size: 1.4rem;
      margin-bottom: 15px;
    }

    .reading {
      font-size: 2rem;
      color: #007acc;
      margin: 10px 0;
    }

    form {
      margin-top: 15px;
    }

    label {
      font-weight: 500;
      display: block;
      margin: 10px 0 5px;
    }

    input, select {
      padding: 8px;
      font-size: 1rem;
      width: 100%;
      box-sizing: border-box;
      border-radius: 6px;
      border: 1px solid #ccc;
    }

    input[type="submit"] {
      background-color: #007acc;
      color: white;
      width: auto;
      padding: 10px 20px;
      margin-top: 15px;
      cursor: pointer;
    }

    input[type="submit"]:hover {
      background-color: #005fa3;
    }

    .form-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 15px;
    }

    canvas {
      max-height: 300px;
    }

    table {
      width: 100%;
      margin-top: 15px;
      border-collapse: collapse;
    }

    th, td {
      padding: 8px 12px;
      text-align: left;
      border-bottom: 1px solid #eee;
    }

    th {
      background: #fafafa;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <h1>Sensor Readout</h1>
      <div id="liveReading" class="reading">--</div>

      <form id="scalingForm">
        <label for="scale">Display as:</label>
        <select id="scale">
          <option value="°C">Temperature (°C)</option>
          <option value="V">Voltage (V)</option>
          <option value="PSI">Pressure (PSI)</option>
          <option value="L/min">Flow (L/min)</option>
        </select>

        <div class="form-grid">
          <div>
            <label for="u_min">Unit Min</label>
            <input type="number" id="u_min" step="0.1" value="0">
          </div>
          <div>
            <label for="u_max">Unit Max</label>
            <input type="number" id="u_max" step="0.1" value="100">
          </div>
        </div>

        <input type="submit" value="Apply Scaling">
      </form>
    </div>

    <div class="card">
      <h2>Live Chart</h2>
      <canvas id="sensorChart"></canvas>
    </div>

    <div class="card">
      <h2>Time Log</h2>
      <table>
        <thead>
          <tr><th>Time</th><th>Value</th></tr>
        </thead>
        <tbody id="logTable">
          <!-- JS will fill rows -->
        </tbody>
      </table>
    </div>
  </div>

  <script>
    const chartCtx = document.getElementById('sensorChart').getContext('2d');
    const logTable = document.getElementById('logTable');
    const liveReading = document.getElementById('liveReading');

    let unit = "°C";
    let uMin = 0;
    let uMax = 100;

    const chartData = {
      labels: [],
      datasets: [{
        label: 'Sensor Reading',
        data: [],
        borderColor: '#007acc',
        backgroundColor: 'rgba(0,122,204,0.1)',
        fill: true,
        tension: 0.3,
        pointRadius: 2
      }]
    };

    const chart = new Chart(chartCtx, {
      type: 'line',
      data: chartData,
      options: {
        responsive: true,
        scales: {
          x: { title: { display: true, text: 'Time' }},
          y: { title: { display: true, text: unit }}
        }
      }
    });

    document.getElementById('scalingForm').addEventListener('submit', (e) => {
      e.preventDefault();
      uMin = parseFloat(document.getElementById('u_min').value);
      uMax = parseFloat(document.getElementById('u_max').value);
      unit = document.getElementById('scale').value;
      chart.options.scales.y.title.text = unit;
      chart.update();
    });

    async function fetchData() {
      try {
        const res = await fetch('/data');
        const data = await res.json();
        const raw = parseFloat(data.value); // value in mA or ADC equivalent
        const time = data.timestamp || new Date().toLocaleTimeString();

        // Scale (assuming 4–20 mA linear map)
        const scaled = ((raw - 4) / 16) * (uMax - uMin) + uMin;
        const scaledVal = scaled.toFixed(2);

        liveReading.textContent = `${scaledVal} ${unit}`;

        // Update chart
        chartData.labels.push(time);
        chartData.datasets[0].data.push(scaled);
        if (chartData.labels.length > 30) {
          chartData.labels.shift();
          chartData.datasets[0].data.shift();
        }
        chart.update();

        // Log table
        const row = document.createElement('tr');
        row.innerHTML = `<td>${time}</td><td>${scaledVal}</td>`;
        logTable.prepend(row);
        if (logTable.rows.length > 30) logTable.deleteRow(30);

      } catch (err) {
        console.error('Fetch error:', err);
      }
    }

    setInterval(fetchData, 5000); // fetch every 5 seconds
    fetchData(); // initial
  </script>
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

            # Serve the embedded HTML page if the request is for '/'
            if "GET /" in request:
                print("Serving embedded HTML page")

                # Send the embedded HTML content
                cl.send('HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n')
                cl.send(html_content)

            else:
                cl.send('HTTP/1.0 404 Not Found\r\n\r\n')

            cl.close()
        except Exception as e:
            print("Error:", e)
            cl.close()

# Start the web server
serve()

