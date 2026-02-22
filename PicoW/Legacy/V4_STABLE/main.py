import time
from network_ap import start_ap
from Code.sensors import init_sensors
from digital_io import init_digital
from Code.webserver import serve

# ====== Startup sequence ======
start_ap()         # Bring up AP
time.sleep(1)      # small delay for hardware stability
init_sensors()     # Initialize ADC sensors
time.sleep(1)      # small delay for hardware stability
init_digital()     # Initialize digital I/O
time.sleep(5)      # small delay for hardware stability
serve()            # start the web server (blocking)
