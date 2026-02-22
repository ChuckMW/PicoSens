# 📄**PicoSens Dashboard Setup Guide**

---

## 🚀 Overview

This guide walks you through setting up a **Raspberry Pi Pico W** as a **wireless access point** that hosts a **sensor dashboard** via a built-in web server. No external Wi-Fi network is needed — just power up the Pico W, and connect directly to its Wi-Fi.

---

## 🔧 What You Need

- Raspberry Pi Pico W
- USB cable
- [Thonny IDE](https://thonny.org/) (or another MicroPython editor)
- MicroPython firmware installed on your Pico W  
  ([Install guide here](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html))
- This project’s Python script (see below)

---

## 📡 Wi-Fi Network Details (Hosted by Pico W)

| Setting       | Value        |
|---------------|--------------|
| SSID          | `PicoSens`   |
| Password      | `pico1234`   |
| Dashboard URL | `http://192.168.4.1` |

---

## 📁 Files

### 1. `main.py`

This is the main MicroPython script you need to upload and run on the Pico W. It:

- Starts a Wi-Fi access point
- Serves a local HTML dashboard
- Simulates sensor readings and returns them via a `/data` endpoint

### 2. `dashboard.html` (optional)

If you want to keep your HTML separate from the Python script, you can store it in a file and load it dynamically. However, in the default setup, the HTML is embedded directly inside `main.py`.

---
