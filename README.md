# PicoSens

# **PicoSens** – Industrial Remote Sensor Dashboard with Raspberry Pi Pico W

**PicoSens** is a compact, Wi-Fi-enabled monitoring system designed for industrial environments. It interfaces with industry-standard 4–20 mA current loop sensors to measure critical parameters like temperature, pressure, flow, and current. Using a Raspberry Pi Pico W, PicoSens provides real-time data visualization via a responsive web dashboard, logs historical readings, and supports configurable alerts to detect anomalies and prevent equipment failure.

---

## ✅ Key Use Cases

Ideal for remote monitoring, diagnostics, and preventive maintenance in:

- **HVAC systems**: Monitor air temperature, pressure, or flow  
- **Data centers & server rooms**: Track thermal and humidity conditions  
- **Electrical infrastructure**: Supervise transformer temperature or breaker currents  
- **Industrial automation**: Check line pressure or tank levels on the factory floor  

---

## ⚙️ Core Features

- **4–20 mA Sensor Interface**: Read analog signals using precision current-to-voltage conversion and onboard ADC  
- **Wi-Fi-Enabled Dashboard**: Hosted on the Pico W, accessible from any device on the network  
- **Live Data Visualization**: Dynamic charts via Chart.js to monitor trends in real time  
- **Sensor Calibration & Conversion**: Easily map sensor current values to engineering units (e.g., °C, PSI, L/min)  
- **Threshold Alerts**: Set min/max thresholds to receive immediate notifications via web interface or webhook  
- **Data Logging**: Save timestamped readings to CSV files on internal flash or SD card for analysis and reporting  
- **Mobile-Friendly Interface**: Works seamlessly on smartphones, tablets, and desktops  

---

## 🔩 Hardware Requirements

| Component                   | Purpose                                                  |
|----------------------------|----------------------------------------------------------|
| **Raspberry Pi Pico W**     | Wi-Fi-enabled microcontroller for processing & hosting   |
| **4–20 mA Sensor**          | Industrial sensor (e.g., temperature, flow, pressure)     |
| **165 Ω Precision Resistor**| Converts current signal to readable voltage for ADC      |
| **Power Supply (e.g., 24 V)** | Powers sensor current loop                            |
| *(Optional)* TVS Diode / Op-amp | Protects ADC from voltage spikes/noise             |
| *(Optional)* SD Card Module | Enables high-capacity long-term data logging            |

---

## 🛠️ Future Enhancements (Optional)

- Cloud integration (e.g., MQTT or HTTP push to cloud dashboards)  
- Remote firmware updates  
- Multi-sensor support with dynamic channel selection  
- Enclosure and power supply integration for rugged deployments  

---