# PlantHelper

## Overview
PlantHelper is a simple IoT project designed for home gardening. It uses Raspberry Pi and Arduino Uno to monitor and manage plant health via sensors that measure soil moisture, light, temperature, and humidity. The system automates watering based on sensor inputs and allows remote monitoring through a web application.

## Features
- Utilizes Arduino and Raspberry Pi for managing sensors and watering.
- Monitors plant conditions with sensors.
- Automates watering actions.
- Web application for remote management.

## Required Parts
- Arduino Uno
- Raspberry Pi 3 Model B+
- Soil Moisture Sensor
- Light-Dependent Resistor (LDR)
- DHT22 Temperature and Humidity Sensor
- Submersible Water Pump
- 5V Relay Module
- Silicon Tubing
- Power supplies for Raspberry Pi and water pump
- Miscellaneous (cables, connectors, breadboard, mounting tools, SD card for OS)

## Setup
1. Install Python, boto3, and pyserial on the Raspberry Pi.
2. Connect the Arduino.
3. Run `python3 PH-ArduinoSensorReader.py` in the terminal.
4. Access the web application at [planthelper.online/welcome.html](http://planthelper.online/welcome.html) to view or change settings.

## Conclusion
PlantHelper automates plant care by adjusting watering based on real-time data, easing the management of home gardens. It also serves as a hands-on introduction to IoT with its cloud integration and automated controls.

## Team Members
- Emmet Blassingame
- Blake Brown
