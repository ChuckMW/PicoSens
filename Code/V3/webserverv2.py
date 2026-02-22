import socket
import json
from sensors import read_sensors, check_thresholds
from digital_io import read_digital_inputs, digital_outputs, set_digital_output
from machine import Pin
import ure
import time

led = Pin("LED", Pin.OUT)

html_content = """ 
<!DOCTYPE html>
<html>
<head>
<title>Pico Multi-Sensor + Digital I/O</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family:Arial; padding:20px;">
<h1>PicoSense</h1>

<div style="margin-bottom:10px;">
  Connection Status: 
  <span id="connStatus" style="display:inline-block; width:12px; height:12px; border-radius:50%; background:red;"></span>
</div>

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

function applyInterval() { 
    updateInterval=parseInt(document.getElementById("intervalInput").value); 
    clearInterval(timer); 
    timer=setInterval(update, updateInterval);
}
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

// Connection status indicator
let statusDot = document.getElementById("connStatus");
let blink = 0;
function updateConnectionIndicator(success){
    if(success){
        blink = (blink + 0.1) % 1;
        let intensity = 0.5 + 0.5 * Math.sin(blink * 2 * Math.PI);
        statusDot.style.backgroundColor = `rgb(0, ${Math.floor(intensity*255)}, 0)`;
    } else {
        statusDot.style.backgroundColor = "red";
    }
}

async function update(){
    try{
        const res=await fetch('/data'); 
        const d=await res.json();

        document.getElementById('s1').textContent=d.sensor1.voltage.toFixed(3);
        document.getElementById('s2').textContent=d.sensor2.voltage.toFixed(3);
        document.getElementById('s3').textContent=d.sensor3.voltage.toFixed(3);
        document.getElementById('din0').textContent=d.din0;
        document.getElementById('din1').textContent=d.din1;
        document.getElementById('dout0').textContent=d.dout0;
        document.getElementById('dout1').textContent=d.dout1;

        data1.push(d.sensor1.voltage); data2.push(d.sensor2.voltage); data3.push(d.sensor3.voltage);
        din0Data.push(d.din0); din1Data.push(d.din1);
        dout0Data.push(d.dout0); dout1Data.push(d.dout1);

        if(data1.length>maxPoints){
            data1.shift(); data2.shift(); data3.shift();
            din0Data.shift(); din1Data.shift();
            dout0Data.shift(); dout1Data.shift();
        }

        drawGraph();
        updateConnectionIndicator(true);
    }catch(e){
        console.log("Fetch error:",e);
        updateConnectionIndicator(false);
    }
}

async function setOut(index,value){ await fetch(`/digital?out${index}=${value}`); update(); }

timer=setInterval(update,updateInterval); update();
</script>

</body>
</html>
"""

def blink_led(duration=0.05):
    led.on()
    time.sleep(duration)
    led.off()

def serve():
    addr = socket.getaddrinfo('0.0.0.0',80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print("Server listening on", addr)

    while True:
        try:
            cl, addr = s.accept()
            request = cl.recv(1024).decode()
            blink_led()

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

            elif "GET /digital" in request:
                for i in range(len(digital_outputs)):
                    match = ure.search(f"out{i}=([01])", request)
                    if match:
                        set_digital_output(i,int(match.group(1)))
                payload = json.dumps({
                    "dout0": digital_outputs[0].value(),
                    "dout1": digital_outputs[1].value()
                })
                cl.send('HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n')
                cl.send(payload)

            elif "GET /" in request:
                cl.send('HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n')
                cl.send(html_content)
            else:
                cl.send('HTTP/1.0 404 Not Found\r\n\r\n')

            cl.close()
        except Exception as e:
            print("Server error:", e)
            cl.close()
