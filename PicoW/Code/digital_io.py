from machine import Pin
from config import load_config
from debug import log

cfg = load_config()

log("Initializing digital I/O...")

din0 = Pin(15, Pin.IN, Pin.PULL_DOWN)
din1 = Pin(14, Pin.IN, Pin.PULL_DOWN)
digital_inputs = [din0, din1]

dout0 = Pin(13, Pin.OUT)
dout1 = Pin(12, Pin.OUT)
digital_outputs = [dout0, dout1]

log("Applying default digital output states...")
for i, val in enumerate(cfg["digital"]["output_default"]):
    log(f"Setting DOUT{i} = {val}")
    digital_outputs[i].value(val)

def read_digital_inputs():
    vals = [pin.value() for pin in digital_inputs]
    log("Digital inputs read: " + str(vals))
    return vals

def set_digital_output(index, value):
    log(f"Setting digital output {index} to {value}")
    if 0 <= index < len(digital_outputs):
        digital_outputs[index].value(value)
    else:
        log("Invalid digital output index!")

def init_digital():
    log("Digital I/O initialized")

