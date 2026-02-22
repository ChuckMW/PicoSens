import socket, json, time
from machine import Pin, reset
from sensors import read_sensors, check_thresholds
from digital_io import read_digital_inputs, digital_outputs, set_digital_output
from config import load_config, save_config

led = Pin("LED", Pin.OUT)

html_page = """<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>PicoSense</title>
<style>
body{font-family:Arial,sans-serif;margin:10px;background:#f5f5f5;color:#333}
h1{color:#007acc;margin:5px 0}
h2{color:#005fa3;margin:8px 0}
.section{background:#fff;padding:8px;border-radius:6px;margin-bottom:8px;box-shadow:0 1px 3px rgba(0,0,0,.1)}
.status-dot{width:10px;height:10px;border-radius:50%;background:red;display:inline-block;margin-left:5px}
button{padding:4px 8px;border:none;border-radius:4px;background:#007acc;color:#fff;cursor:pointer;margin:2px}
button:hover{background:#005fa3}
input{padding:3px;border:1px solid #ccc;border-radius:4px;width:120px}
canvas{border:1px solid #ccc;border-radius:6px;background:#fff;margin-top:8px}
.acc-h{background:#007acc;color:#fff;padding:6px;border-radius:6px;cursor:pointer;font-size:14px}
.acc-c{display:none;background:#fff;border-radius:6px;margin-top:4px;padding:6px}
</style></head><body>
<h1>PicoSense</h1>

<div class="section">
<strong>Status:</strong><span id="cs" class="status-dot"></span>
</div>

<div class="section">
<strong>Sensors (V):</strong><br>
S1:<span id="s1">--</span><br>
S2:<span id="s2">--</span><br>
S3:<span id="s3">--</span>
</div>

<div class="section">
<h2>Digital Inputs</h2>
DIN0:<span id="i0">--</span><br>
DIN1:<span id="i1">--</span>
</div>

<div class="section">
<h2>Digital Outputs</h2>
<button onclick="setOut(0,1)">DOUT0 ON</button>
<button onclick="setOut(0,0)">DOUT0 OFF</button>
<button onclick="setOut(1,1)">DOUT1 ON</button>
<button onclick="setOut(1,0)">DOUT1 OFF</button><br>
DOUT0:<span id="o0">--</span><br>
DOUT1:<span id="o1">--</span>
</div>

<div class="acc-h" onclick="tgAcc()">Advanced Settings</div>
<div id="adv" class="acc-c">
<h3>Update interval (ms)</h3>
<input type="number" id="iv" value="2000" min="200" step="200">
<button onclick="apIv()">Apply</button>
<h3>Graph max voltage</h3>
<input type="number" id="sc" value="3.3" min="1" step="0.1">
<button onclick="apSc()">Apply</button>
<h3>WiFi</h3>
SSID:<input id="ws" type="text"><br><br>
Password:<input id="wp" type="text"><br><br>
<button onclick="svW()">Save WiFi</button>
<h3>System</h3>
<button onclick="if(confirm('Reboot Pico?'))fetch('/reboot')">Reboot</button>
</div>

<canvas id="g" width="500" height="250"></canvas>

<script>
var c=document.getElementById("g"),x=c.getContext("2d");
var iv=2000,sc=3.3,t=null,mp=100;
var d1=[],d2=[],d3=[],i0d=[],i1d=[],o0d=[],o1d=[];
var cs=document.getElementById("cs"),gt=false,ok=true;

function tgAcc(){var a=document.getElementById("adv");a.style.display=a.style.display=="block"?"none":"block";}

function apIv(){iv=parseInt(document.getElementById("iv").value)||2000;clearInterval(t);t=setInterval(up,iv);}
function apSc(){sc=parseFloat(document.getElementById("sc").value)||3.3;}

function ldW(){fetch("/getwifi").then(r=>r.json()).then(j=>{document.getElementById("ws").value=j.ssid||"";document.getElementById("wp").value=j.password||"";}).catch(e=>{});}
function svW(){var s=encodeURIComponent(document.getElementById("ws").value),p=encodeURIComponent(document.getElementById("wp").value);fetch("/setwifi?ssid="+s+"&pass="+p).then(r=>r.text()).then(_=>{alert("WiFi saved, rebooting");fetch("/reboot");});}

function grd(){
 x.clearRect(0,0,c.width,c.height);
 x.strokeStyle="#eee";x.fillStyle="#000";x.font="10px Arial";
 for(var i=0;i<=5;i++){
  var y=i*c.height/5;
  x.beginPath();x.moveTo(0,y);x.lineTo(c.width,y);x.stroke();
  var v=(sc*(5-i)/5).toFixed(1);
  x.fillText(v,2,y-2);
 }
}

function ln(d,col){
 if(!d.length)return;
 x.beginPath();x.strokeStyle=col;
 for(var i=0;i<d.length;i++){
  var xx=i*c.width/mp;
  var yy=c.height-(d[i]/sc)*c.height;
  if(i==0)x.moveTo(xx,yy);else x.lineTo(xx,yy);
 }
 x.stroke();
}

function dg(d,col,yb){
 if(!d.length)return;
 x.beginPath();x.strokeStyle=col;
 for(var i=0;i<d.length;i++){
  var xx=i*c.width/mp;
  var yy=c.height-(yb+d[i]*(yb-5));
  if(i==0)x.moveTo(xx,yy);else x.lineTo(xx,yy);
 }
 x.stroke();
}

function dr(){
 grd();
 ln(d1,"red");ln(d2,"green");ln(d3,"blue");
 dg(i0d,"orange",20);dg(i1d,"purple",40);
 dg(o0d,"brown",60);dg(o1d,"black",80);
}

function setConn(s){
 ok=s;
 if(!ok){cs.style.backgroundColor="red";return;}
 gt=!gt;cs.style.backgroundColor=gt?"#0c0":"#090";
}

setInterval(function(){if(ok)setConn(true);},1000);

function up(){
 fetch("/data").then(r=>r.json()).then(j=>{
  document.getElementById("s1").textContent=j.s1.toFixed(3);
  document.getElementById("s2").textContent=j.s2.toFixed(3);
  document.getElementById("s3").textContent=j.s3.toFixed(3);
  document.getElementById("i0").textContent=j.i0;
  document.getElementById("i1").textContent=j.i1;
  document.getElementById("o0").textContent=j.o0;
  document.getElementById("o1").textContent=j.o1;

  d1.push(j.s1);d2.push(j.s2);d3.push(j.s3);
  i0d.push(j.i0);i1d.push(j.i1);o0d.push(j.o0);o1d.push(j.o1);
  if(d1.length>mp){
   d1.shift();d2.shift();d3.shift();
   i0d.shift();i1d.shift();o0d.shift();o1d.shift();
  }
  dr();setConn(true);
 }).catch(e=>{ok=false;setConn(false);});
}

function setOut(i,v){fetch("/digital?out"+i+"="+v).then(_=>up()).catch(_=>{});}

ldW();dr();up();t=setInterval(up,iv);
</script>
</body></html>
"""

def blink():
    led.on()
    time.sleep(0.03)
    led.off()

def parse_query(path):
    if "?" not in path:
        return {}
    qs = path.split("?", 1)[1]
    out = {}
    for pair in qs.split("&"):
        if "=" in pair:
            k, v = pair.split("=", 1)
            out[k] = v.replace("%20", " ").replace("+", " ")
    return out

def serve():
    cfg = load_config()

    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)

    while True:
        cl, addr = s.accept()
        try:
            req = cl.recv(1024).decode()
            blink()
            if not req:
                cl.close()
                continue

            line = req.split("\n")[0]
            parts = line.split()
            if len(parts) < 2:
                cl.close()
                continue
            method, path = parts[0], parts[1]

            if path.startswith("/data"):
                sens = read_sensors()
                dins = read_digital_inputs()
                check_thresholds(sens)
                payload = json.dumps({
                    "s1": sens[0]["voltage"],
                    "s2": sens[1]["voltage"],
                    "s3": sens[2]["voltage"],
                    "i0": dins[0],
                    "i1": dins[1],
                    "o0": digital_outputs[0].value(),
                    "o1": digital_outputs[1].value()
                })
                cl.send("HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n")
                cl.send(payload)
                cl.close()
                continue

            if path.startswith("/digital"):
                q = parse_query(path)
                for k in q:
                    if k.startswith("out"):
                        try:
                            idx = int(k[3:])
                            val = int(q[k])
                            set_digital_output(idx, val)
                        except:
                            pass
                payload = json.dumps({
                    "o0": digital_outputs[0].value(),
                    "o1": digital_outputs[1].value()
                })
                cl.send("HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n")
                cl.send(payload)
                cl.close()
                continue

            if path.startswith("/getwifi"):
                wifi = cfg["wifi"]
                cl.send("HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n")
                cl.send(json.dumps({"ssid": wifi["ssid"], "password": wifi["password"]}))
                cl.close()
                continue

            if path.startswith("/setwifi"):
                q = parse_query(path)
                ssid = q.get("ssid", "")
                pw = q.get("pass", "")
                cfg["wifi"]["ssid"] = ssid
                cfg["wifi"]["password"] = pw
                save_config(cfg)
                cl.send("HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\nOK")
                cl.close()
                continue

            if path.startswith("/reboot"):
                cl.send("HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\nRebooting")
                cl.close()
                time.sleep(0.2)
                reset()

            if path == "/" or path.startswith("/ "):
                cl.send("HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
                cl.send(html_page)
                cl.close()
                continue

            cl.send("HTTP/1.0 404 Not Found\r\n\r\n")
            cl.close()

        except Exception as e:
            try:
                cl.close()
            except:
                pass
