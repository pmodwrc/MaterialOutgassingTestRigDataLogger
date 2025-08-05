# Material Outgassing Test Rig Data Logger

This repository contains the software for the Material Outgassing Test Rig Data Logger. This system is designed to monitor and log various parameters during material outgassing tests.

## Keithley Multiplexer Setup

* **Install Keysight IO** you can download the latest version of the Keysight I/O from the [Keysight website](https://www.keysight.com/us/en/lib/software-detail/computer-software/io-libraries-suite-downloads-2175637.html). This software is essential for communicating with Keithley instruments.

## Hardware Requirements

* **[Specify Microcontroller/SBC]:** e.g., Arduino Uno, Raspberry Pi, ESP32
* **Pressure Transducers:** e.g., [Specify model/type]
* **Temperature Sensors:** e.g., PT100, Thermocouples (with appropriate amplifiers)
* **Display (Optional):** e.g., LCD, OLED
* **SD Card Module (for logging):** If data is stored locally
* **Power Supply:** Appropriate for all components

## Software Requirements

* **Arduino IDE / PlatformIO:** For flashing the microcontroller code.
* **Python 3.x:** For the data logging and visualization application (if applicable).
* **Required Python Libraries:** (e.g., `pyserial`, `matplotlib`, `pandas`, `tkinter` for GUI)

## Installation and Setup

### 1. Hardware Assembly

Follow the wiring diagrams and schematics provided in the `hardware/` directory (if available) to connect all sensors and components to the microcontroller.

### 2. Microcontroller Code

1. **Open the Project:** Open the `firmware/` directory in your Arduino IDE or PlatformIO.
2. **Install Libraries:** Ensure you have all necessary libraries installed. Check the `firmware/firmware.ino` (or equivalent) file for `#include` statements and install any missing libraries via the Arduino IDE Library Manager or PlatformIO's library management.
    * Example libraries: `Adafruit_Sensor`, `Adafruit_BME280`, `SD`, `RTClib`
