import socket
import json
import time
import urandom
import gc
from machine import Pin, reset
from sensors import read_sensors, check_thresholds
from digital_io import read_digital_inputs, digital_outputs, set_digital_output
from config import load_config, save_config
from logger import log_data
from mqtt_client import mqtt_publish

led = Pin("LED", Pin.OUT)
sessions = {}

# --------------------------
# Utility functions
# --------------------------
def blink():
    led.on()
    time.sleep(0.02)
    led.off()

def generate_token():
    return str(urandom.getrandbits(32))

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

def is_authenticated(req):
    if "Cookie:" not in req:
        return False
    for line in req.split("\r\n"):
        if line.startswith("Cookie:") and "session=" in line:
            token = line.split("session=")[1].strip()
            return token in sessions
    return False

def load_html(filename):
    path = "html/" + filename
    try:
        with open(path, "r") as f:
            content = f.read()
            print("[DEBUG] Loaded HTML:", path)
            return content
    except Exception as e:
        print("[ERROR] Cannot load HTML:", path, e)
        return f"<h1>Error loading {filename}</h1>"

def send_html(cl, html):
    chunk_size = 256
    for i in range(0, len(html), chunk_size):
        cl.send(html[i:i+chunk_size])

# --------------------------
# HTTP Server
# --------------------------
def serve():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(2)
    print("[INFO] Webserver running on 0.0.0.0:80")

    while True:
        gc.collect()
        cl, addr = s.accept()
        try:
            req = cl.recv(2048).decode()
            if not req:
                cl.close()
                continue

            blink()
            line = req.split("\n")[0]
            parts = line.split()
            if len(parts) < 2:
                cl.close()
                continue
            method, path = parts[0], parts[1]
            print("[DEBUG] Request:", method, path)

            # --------------------------
            # LOGIN PAGE
            # --------------------------
            if path.startswith("/login"):
                cl.send("HTTP/1.0 200 OK\r\nContent-Type:text/html\r\n\r\n")
                send_html(cl, load_html("login.html"))
                cl.close()
                continue

            # --------------------------
            # DO LOGIN
            # --------------------------
            if path.startswith("/dologin"):
                if method == "GET":
                    q = parse_query(path)
                elif method == "POST":
                    try:
                        body = req.split("\r\n\r\n")[1]
                        q = parse_query("?" + body)
                    except:
                        q = {}
                cfg = load_config()
                if q.get("u") == cfg["auth"]["username"] and q.get("p") == cfg["auth"]["password"]:
                    token = generate_token()
                    sessions[token] = True
                    cl.send("HTTP/1.0 302 Found\r\nSet-Cookie: session="+token+"\r\nLocation:/\r\n\r\n")
                    print("[INFO] Login successful")
                else:
                    cl.send("HTTP/1.0 302 Found\r\nLocation:/login\r\n\r\n")
                    print("[WARN] Login failed")
                cl.close()
                continue

            # --------------------------
            # LOGOUT
            # --------------------------
            if path.startswith("/logout"):
                cl.send("HTTP/1.0 302 Found\r\nLocation:/login\r\n\r\n")
                cl.close()
                print("[INFO] Logout")
                continue

            # --------------------------
            # SYSTEM REBOOT
            # --------------------------
            if path.startswith("/reboot"):
                try:
                    cl.send("HTTP/1.0 200 OK\r\nContent-Type:text/plain\r\n\r\nRebooting Pico...\r\n")
                    cl.close()
                    time.sleep(0.3)
                    print("[INFO] Rebooting system now")
                    reset()
                except Exception as e:
                    print("[ERROR] Reboot failed:", e)
                continue

            # --------------------------
            # AUTHENTICATION CHECK
            # --------------------------
            if not is_authenticated(req):
                if path.startswith("/data") or path.startswith("/digital"):
                    cl.send("HTTP/1.0 401 Unauthorized\r\nContent-Type: application/json\r\n\r\n")
                    cl.send('{"error":"auth"}')
                else:
                    cl.send("HTTP/1.0 302 Found\r\nLocation:/login\r\n\r\n")
                cl.close()
                continue

            # --------------------------
            # DATA ENDPOINT
            # --------------------------
            if path.startswith("/data"):
                sens = read_sensors()
                dins = read_digital_inputs()
                check_thresholds(sens)
                data = {
                    "s1": sens[0]["voltage"],
                    "s2": sens[1]["voltage"],
                    "s3": sens[2]["voltage"],
                    "i0": dins[0],
                    "i1": dins[1],
                    "o0": digital_outputs[0].value(),
                    "o1": digital_outputs[1].value()
                }
                log_data(data)
                mqtt_publish(json.dumps(data))
                cl.send("HTTP/1.0 200 OK\r\nContent-Type:application/json\r\n\r\n")
                cl.send(json.dumps(data))
                cl.close()
                continue

            # --------------------------
            # DIGITAL OUTPUT CONTROL
            # --------------------------
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
                cl.send("HTTP/1.0 200 OK\r\nContent-Type:application/json\r\n\r\n")
                cl.send(payload)
                cl.close()
                continue

            # --------------------------
            # ROUTING FOR HTML PAGES
            # --------------------------
            page_map = {
                "/": "dashboard.html",
                "/sensors": "sensors.html",
                "/digital": "digital.html",
                "/wifi": "wifi.html",
                "/system": "system.html",
                "/graph": "graph.html"
            }
            if path in page_map:
                cl.send("HTTP/1.0 200 OK\r\nContent-Type:text/html\r\n\r\n")
                send_html(cl, load_html(page_map[path]))
                cl.close()
                continue

            # --------------------------
            # NOT FOUND
            # --------------------------
            cl.send("HTTP/1.0 404 Not Found\r\n\r\n")
            cl.close()
            print("[WARN] 404 Not Found:", path)

        except Exception as e:
            print("[ERROR] Exception:", e)
            try:
                cl.close()
            except:
                pass
