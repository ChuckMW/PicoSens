import time
from network_ap import start_ap
from sensors import init_sensors
from digital_io import init_digital
from webserver import serve
from mqtt_client import mqtt_connect
from debug import log

AP = True
SENS = True
DIGI = True
WEB = True
MQTT = True

if AP or SENS or DIGI or WEB or MQTT:
    log("Boot sequence starting...")
    
    if AP:
        log("AP Enabled")
    if SENS:
        log("SENS Enabled")
    if DIGI:
        log("DIGI Enabled")
    if WEB:
        log("WEB Enabled")
    if MQTT:
        log("MQTT Enabled")
else:
    log("Nothing enabled, enable features and reboot...")
     
     
     
if AP:
    log("Starting AP...")
    start_ap()
    time.sleep(0.25)
    
if SENS:
    log("Starting sensors...")
    init_sensors()
    time.sleep(0.25)
    
if DIGI:
    log("Starting digital...")
    init_digital()
    time.sleep(0.25)

if WEB:
    log("Starting webserver...")
    serve()
    time.sleep(0.25)
    
if MQTT:
    mqtt_connect()
    log("mqtt_connect")
    time.sleep(0.25)
