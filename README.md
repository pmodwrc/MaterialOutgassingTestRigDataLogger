# Material Outgassing Test Rig Data Logger

This repository contains the software for the Material Outgassing Test Rig Data Logger. This system is designed to monitor and log various parameters during material outgassing tests.

## Virtual Environment Setup

To set up a virtual environment for this project, follow these steps:

1. **Create a Virtual Environment:**

   ```sh
   python -m venv venv
   ```

2. **Activate the Virtual Environment:**
  
    ```sh
    venv\Scripts\activate
    ```

3. **Install Required Packages:**

   ```sh
   pip install -r requirements.txt
   ```

## Keithley Multiplexer Setup

[Documentation](https://www.tek.com/en/search?keywords=2000&facets=_templatename%3dmanual&sort=desc) of Keithley Multiplexer 2000

* **Install Keysight IO** you can download the latest version of the Keysight I/O from the [Keysight website](https://www.keysight.com/us/en/lib/software-detail/computer-software/io-libraries-suite-downloads-2175637.html). This software is essential for communicating with Keithley instruments.
  * Install "IO library" and leave everything at default settings.
  * open the "Connection Expert" and add the Keithley instrument.
  * Make sure to select the correct communication port (e.g., COM1, COM2, GPIB, Serial) and configure the settings according to your instrument's specifications.
  * You might have to install the driver for the connection adapter (e.g., [UPort1150](https://www.moxa.com/en/products/industrial-edge-connectivity/usb-to-serial-converters-usb-hubs/usb-to-serial-converters/uport-1100-series#resources)).
* Once the connection is established, you can test the communication by running following command in the terminal:
  
    ```sh
    python -c "import pyvisa; print(pyvisa.ResourceManager().list_resources())"
    ```

    the output should include the address of your Keithley instrument (e.g., `('ASRL1::INSTR',)`).
