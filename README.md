# PlantHelper
The Automated Plant Caretaker is an innovative IoT project aimed at revolutionizing home gardening. Using a Raspberry Pi and Arduino Uno as the brain, this project employs various sensors to assess the vital parameters that affect plant health such as soil moisture, ambient light, temperature, and humidity. The system automatically adjusts watering schedules based on real-time sensor data, ensuring optimal plant growth. Additionally, the cloud-connected web application facilitates remote monitoring and control, providing a comprehensive solution for both novice and experienced gardeners to maintain their gardens with ease and efficiency.

## Core Features
- Arduino and Raspberry Pi integration for sensor data processing and system control.
- Monitors plant vitals through precision sensors.
- Executes watering actions based on data-driven decisions.
- Provides a web application for remote monitoring and manual control.
- DynamoDB AWS Integration

## Parts Required
- Arduino Uno
- Raspberry Pi 3 Model B+
- Soil Moisture Sensor x1
- Light-Dependent Resistor (LDR) x1
- DHT22 Temperature and Humidity Sensor x1
- Submersible Water Pump x1
- 5V Relay Module x1
- Silicon Tubing x1
- Power Supply for Raspberry Pi
- Power Supply for SWP
- Miscellaneous (cables, connectors, breadboard, mounting tools, SD for OS)

## Setup
On Raspberry Pi:
- install python
- install boto3
- install pyserial
- connect Arduino
- in terminal run 'python3 PH-ArduinoSensorReader.py'
- view and change settings and data at planthelper.online/welcome.html

## Conclusion
The Automated Plant Caretaker is an all-in-one system that combines gardening with smart technology. It keeps plants in the perfect conditions, making it easy for users by taking the guesswork out of plant care, leading to better growth. Additionally, it offers a practical introduction to IoT development through its integration of cloud technology, sensors, and automatic controls.

## Team Members
- Emmet Blassingame
- Blake Brown
