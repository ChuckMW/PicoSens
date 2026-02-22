import time
from network_ap import start_ap
from sensors import init_sensors
from digital_io import init_digital
from webserver import serve
from debug import log

log("Boot sequence starting...")

start_ap()
time.sleep(1)

init_sensors()
time.sleep(1)

init_digital()
time.sleep(1)

log("Starting webserver...")
serve()

