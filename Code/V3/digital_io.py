from machine import Pin

din0 = Pin(15, Pin.IN, Pin.PULL_DOWN)
din1 = Pin(14, Pin.IN, Pin.PULL_DOWN)
digital_inputs = [din0,din1]

dout0 = Pin(13, Pin.OUT)
dout1 = Pin(12, Pin.OUT)
digital_outputs = [dout0,dout1]

def read_digital_inputs():
    return [pin.value() for pin in digital_inputs]

def set_digital_output(index, value):
    if 0 <= index < len(digital_outputs):
        digital_outputs[index].value(value)

def init_digital():
    print("Digital I/O initialized")
