# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 15:36:55 2024

@author: labor
"""

# keithley_measurement.py

import pyvisa
import math
import time

class KeithleyMeasurement:
    def __init__(self, rm):
        self.rm = rm
        self.channels = ['','','','','','','']
        
    def connect(self):
        
        instruments = self.rm.list_resources()
        if not instruments:
            print("No instruments found!")
            return None
        print("Connected Instruments:")
        for idx, instrument in enumerate(instruments):
            print(f"{idx}: {instrument}")
    
        """Prompt the user to select an instrument by its index."""
        
        while True:
            try:
                index = int(input(f"Select an instrument by its index (0-{len(instruments) - 1}): "))
                if 0 <= index < len(instruments):
                    resource_name =  instruments[index]
                    break
                else:
                    print(f"Please enter a number between 0 and {len(instruments) - 1}.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")


        self.keithley = self.rm.open_resource(resource_name)
        self.keithley.timeout = 5000
        
        idn_string = self.keithley.query("*IDN?")
        print(f"Connected to: {idn_string.strip()}")

        
    def set_channelConfiguration(self, CHnbr, config):
        # CHnbr: int    0 to 2
        # config string { Voltage, Current, Resistance, NTC_44006, NTC44007} 
        self.channels[CHnbr] = config
    
    def get_channelConfiguration(self):
        # CHnbr: int    0 to 2
        # config string { Voltage, Current, Resistance, NTC_44006, NTC44007} 
        return self.channels
        
    def configure(self, function):
        """Configure a specific channel based on the selected setting."""
        self.config = function
       
        if self.config  == "Voltage":
            self.keithley.write("CONF:VOLT:DC")
        if self.config  == "Current":
            self.keithley.write("CONF:CURR:DC")
        if self.config  == "Resistance":
            self.keithley.write("CONF:RES")
 
    def open_channel(self, channel):
        self.keithley.write("ROUT:OPEN:ALL")  # Open all channels
        
        time.sleep(0.1)
        self.keithley.write(f"ROUT:CLOS (@{channel})")  # Close the specific channel
        return        

    def measure_value(self, config):
        try:
            value  = float(self.keithley.query("READ?"))  # Read value
            return value
        except pyvisa.VisaIOError as e:
            print(f"Keithley measurement error: {e}")
            return None

    def NTC_44006(self, resistance):
        """Calculate temperature from NTC thermistor resistance using Steinhart-Hart equation."""
        A = 1.032e-3
        B = 2.387e-4
        C = 1.580e-7
        log_resistance = math.log(resistance)
        inv_temp = A + B * log_resistance + C * log_resistance**3
        temperature_kelvin = 1 / inv_temp
        temperature_celsius = temperature_kelvin - 273.15
        return temperature_celsius

    def NTC_44007(self, resistance):
        """Calculate temperature from NTC thermistor resistance using Steinhart-Hart equation."""
        A = 1.285e-3
        B = 2.362e-4
        C = 9.285e-8
        log_resistance = math.log(resistance)
        inv_temp = A + B * log_resistance + C * log_resistance**3
        temperature_kelvin = 1 / inv_temp
        temperature_celsius = temperature_kelvin - 273.15
        return temperature_celsius



    def close(self):
        self.keithley.close()
        
        print("Conection to Instrument closed")
    
        

if __name__ == "__main__":
    rm = pyvisa.ResourceManager()
    inst = KeithleyMeasurement(rm)
    inst.connect()
    inst.set_channelConfiguration(0, 'Resistance')
    inst.set_channelConfiguration(1, 'Resistance')
    inst.set_channelConfiguration(2, 'Resistance')
    inst.set_channelConfiguration(3, 'Resistance')
    inst.set_channelConfiguration(4, 'Resistance')
    inst.configure_channel(1)
    value = inst.measure_value()
    print(value)
    inst.configure_channel(2)
    value = inst.measure_value()
    print(value)
    inst.configure_channel(3)
    value = inst.measure_value()
    print(value)
    inst.configure_channel(4)
    value = inst.measure_value()
    print(value)
    inst.close()
    rm.close()
        
