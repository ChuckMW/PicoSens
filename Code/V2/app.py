import time
import network
import socket
import json
from machine import Pin, ADC

# ====== LED for status ======
led = Pin("LED", Pin.OUT)

# ====== ADC Sensors ======
adc0 = ADC(26)
adc1 = ADC(27)
adc2 = ADC(28)
sensors = [adc0, adc1, adc2]

# ====== Calibration / scaling ======
calibration = [
    {"scale": 1.0, "offset": 0.0},
    {"scale": 1.0, "offset": 0.0},
    {"scale": 1.0, "offset": 0.0}
]

# ====== Thresholds for alerts ======
threshold_high = [2.5, 2.5, 2.5]
threshold_low  = [0.5, 0.5, 0.5]

# ====== Digital I/O ======
din0 = Pin(15, Pin.IN, Pin.PULL_DOWN)
din1 = Pin(14, Pin.IN, Pin.PULL_DOWN)
digital_inputs = [din0, din1]

dout0 = Pin(13, Pin.OUT)
dout1 = Pin(12, Pin.OUT)
digital_outputs = [dout0, dout1]

# ====== Helper Functions ======
def blink_led(duration=0.1, status="ON"):
    if status == "ON":
        led.on()
    else:
        led.off()
    time.sleep(duration)
    led.off()

def read_sensors():
    data = []
    for i, adc in enumerate(sensors):
        raw = adc.read_u16()
        voltage = (raw / 65535) * 3.3
        voltage = voltage * calibration[i]["scale"] + calibration[i]["offset"]
        data.append({"raw": raw, "voltage": voltage})
    return data

def check_thresholds(data):
    for i, sensor in enumerate(data):
        if sensor["voltage"] > threshold_high[i]:
            blink_led(0.1, "ON")
        elif sensor["voltage"] < threshold_low[i]:
            blink_led(0.05, "ON")

def read_digital_inputs():
    return [pin.value() for pin in digital_inputs]

def set_digital_output(index, value):
    if 0 <= index < len(digital_outputs):
        digital_outputs[index].value(value)

# ====== Access Point ======
SSID = 'PicoSens'
PASSWORD = 'pico1234'

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=SSID, password=PASSWORD)

# Wait for AP to activate
while not ap.active():
    blink_led(0.5)

blink_led(1)

# ====== Web Server ======
def serve():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    while True:
        try:
            cl, addr = s.accept()
            request = cl.recv(1024).decode()
            blink_led(0.05)

            # ====== Sensor + Digital Data ======
            if "GET /data" in request:
                sensor_data = read_sensors()
                digital_data = read_digital_inputs()
                check_thresholds(sensor_data)

                payload = json.dumps({
                    "sensor1": sensor_data[0],
                    "sensor2": sensor_data[1],
                    "sensor3": sensor_data[2],
                    "din0": digital_data[0],
                    "din1": digital_data[1],
                    "dout0": digital_outputs[0].value(),
                    "dout1": digital_outputs[1].value()
                })

                cl.send('HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n')
                cl.send(payload)

            # ====== Digital Output Control ======
            elif "GET /digital" in request:
                import ure
                for i in range(len(digital_outputs)):
                    match = ure.search(f"out{i}=([01])", request)
                    if match:
                        set_digital_output(i, int(match.group(1)))

                payload = json.dumps({
                    "dout0": digital_outputs[0].value(),
                    "dout1": digital_outputs[1].value()
                })
                cl.send('HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n')
                cl.send(payload)

            # ====== HTML Page ======
            elif "GET /" in request:
                cl.send('HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n')
                cl.send(html_content)

            else:
                cl.send('HTTP/1.0 404 Not Found\r\n\r\n')

            cl.close()

        except Exception:
            cl.close()

# ====== HTML Page with Sensors, Digital I/O, Graph ======
html_content = """ 
<!DOCTYPE html>
<html>
<head>
<title>Pico Multi-Sensor + Digital I/O</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family:Arial; padding:20px;">
<h1>PicoSense</h1>

<div>Sensor 1: <span id="s1">--</span> V</div>
<div>Sensor 2: <span id="s2">--</span> V</div>
<div>Sensor 3: <span id="s3">--</span> V</div>

<hr>
<h2>Digital Inputs</h2>
<div>DIN0: <span id="din0">--</span></div>
<div>DIN1: <span id="din1">--</span></div>

<h2>Digital Outputs</h2>
<button onclick="setOut(0,1)">DOUT0 ON</button>
<button onclick="setOut(0,0)">DOUT0 OFF</button><br>
<button onclick="setOut(1,1)">DOUT1 ON</button>
<button onclick="setOut(1,0)">DOUT1 OFF</button>
<div>DOUT0: <span id="dout0">--</span></div>
<div>DOUT1: <span id="dout1">--</span></div>

<hr>
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
<canvas id="graph" width="700" height="400" style="border:1px solid #ccc;"></canvas>

<script>
const canvas = document.getElementById("graph");
const ctx = canvas.getContext("2d");

let updateInterval = 2000;
let graphScale = 3.3;
let timer;
const maxPoints = 100;
let data1=[], data2=[], data3=[], din0Data=[], din1Data=[], dout0Data=[], dout1Data=[];

function applyInterval() { updateInterval=parseInt(document.getElementById("intervalInput").value); clearInterval(timer); timer=setInterval(update, updateInterval);}
function applyScale() { graphScale=parseFloat(document.getElementById("scaleInput").value); }

function drawGrid() {
    ctx.strokeStyle="#eee"; ctx.font="12px Arial"; ctx.fillStyle="#000";
    for(let i=0;i<=10;i++){
        let y=(i/10)*canvas.height;
        ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(canvas.width,y); ctx.stroke();
        ctx.fillText((graphScale*(10-i)/10).toFixed(2),0,y-2);
    }
    const xStep=10;
    for(let i=0;i<=maxPoints;i+=xStep){
        let x=(i/maxPoints)*canvas.width;
        ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,canvas.height); ctx.stroke();
        ctx.fillText((i*updateInterval/1000).toFixed(1)+"s",x,canvas.height-2);
    }
}

function drawLine(data,color){
    ctx.beginPath(); ctx.strokeStyle=color;
    for(let i=0;i<data.length;i++){
        const x=(i/maxPoints)*canvas.width;
        const y=canvas.height-(data[i]/graphScale)*canvas.height;
        if(i==0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }
    ctx.stroke();
}

function drawDigital(data,color,yOffset){
    ctx.beginPath(); ctx.strokeStyle=color;
    for(let i=0;i<data.length;i++){
        const x=(i/maxPoints)*canvas.width;
        const y=canvas.height-(yOffset+data[i]*(yOffset-5));
        if(i==0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }
    ctx.stroke();
}

function drawGraph(){
    ctx.clearRect(0,0,canvas.width,canvas.height);
    drawGrid();
    drawLine(data1,"red"); drawLine(data2,"green"); drawLine(data3,"blue");
    drawDigital(din0Data,"orange",20); drawDigital(din1Data,"purple",40);
    drawDigital(dout0Data,"brown",60); drawDigital(dout1Data,"black",80);
}

async function update(){
    try{
        const res=await fetch('/data'); const d=await res.json();
        const v1=d.sensor1.voltage, v2=d.sensor2.voltage, v3=d.sensor3.voltage;
        document.getElementById('s1').textContent=v1.toFixed(3);
        document.getElementById('s2').textContent=v2.toFixed(3);
        document.getElementById('s3').textContent=v3.toFixed(3);
        document.getElementById('din0').textContent=d.din0;
        document.getElementById('din1').textContent=d.din1;
        document.getElementById('dout0').textContent=d.dout0;
        document.getElementById('dout1').textContent=d.dout1;

        data1.push(v1); data2.push(v2); data3.push(v3);
        din0Data.push(d.din0); din1Data.push(d.din1);
        dout0Data.push(d.dout0); dout1Data.push(d.dout1);

        if(data1.length>maxPoints){
            data1.shift(); data2.shift(); data3.shift();
            din0Data.shift(); din1Data.shift();
            dout0Data.shift(); dout1Data.shift();
        }

        drawGraph();
    }catch(e){console.log("Fetch error:",e);}
}

async function setOut(index,value){ await fetch(`/digital?out${index}=${value}`); update(); }

timer=setInterval(update,updateInterval); update();
</script>

</body>
</html>
"""

# ====== Startup ======
serve()
