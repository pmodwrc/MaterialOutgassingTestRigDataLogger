# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 22:30:20 2024

@author: labor
"""
import keithley_measurement as instr
import power_supply_control as psu

import threading
import time
import pyvisa

class MeasurementController:
    def __init__(self,file):
        """
        Initialize the MeasurementController with an Instrument and PowerSupply instance.
        
        :param instrument: An instance of the Instrument class.
        :param power_supply: An instance of the PowerSupply class.
        """
        self.rm = pyvisa.ResourceManager()
        self.instrument = instr.KeithleyMeasurement(self.rm)
        self.power_supply = psu.PowerSupplyControl(self.rm)
        self.PSU_stat= "OFF"
        file_path = ""#"//ad.pmodwrc.ch/Institute/Projects/SOLAR-C/30_Product_Assurance/Zeolite/Messergebnisse/MessungenEvelyn"
        file_path +=file
        
        # Open the file in append mode
        self.file = open(file_path, "a")
        self._initialize_file()

    def _initialize_file(self):
        """Initialize the results file with headers if it does not already exist."""
        self.file.write("Time, ValueCH1, ValueCH2, ValueCH3,  ValueCH4,  PSUstat\n")

    def initialize_system(self):
        """Connect to the instrument and power supply, and prepare the system."""
        # Connect to the instrument
        self.instrument.connect()
        # Initialize the power supply (assuming it has a similar connect method)
        self.power_supply.connect()
        

    def configInstrCH(self):
        """
        Configure the instrument channel with the desired configuration.
        
        :param channel: int, channel number to configure.
        :param config: str, configuration for the channel (e.g., "Voltage").
        """
        self.instrument.set_channelConfiguration( 2, "NTC_44006")
        #•self.instrument.set_channelConfiguration( 2, "Resistance")
        print("Instrument channel 2 configured with NTC_44006")
        
        self.instrument.set_channelConfiguration( 3, "NTC_44007")
        #self.instrument.set_channelConfiguration( 3, "Resistance") 
        print("Instrument channel 3 configured with NTC_44007")
        
        self.instrument.set_channelConfiguration( 4, "NTC_44007")
        #self.instrument.set_channelConfiguration( 4, "Resistance")
        print("Instrument channel 4 configured with NTC_44007") 
        
        self.instrument.configure("Resistance")
        
    def perform_measurement(self):
        """
        Perform measurement on all three channels, print results to console, and store them in a file.
        
        :param config: str, the configuration for the channels (e.g., "Voltage").
        """
        values = [0,0,0,0,0,0,0,0,0,0,0,0]
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        config = self.instrument.get_channelConfiguration()
        for channel in range(2,5):
            # if channel == 1:
            #     measured_value = 0
            # else:
                # Configure each channel with the given configuration
                self.instrument.open_channel(channel)
                time.sleep(1)
                #print("CH",channel, ":",config[channel])
                # Measure the value from the current channel
                value = float(self.instrument.measure_value(config[channel]))
                if config[channel] == "NTC_44006":
                    value = round(self.instrument.NTC_44006(value),3)
                if config[channel] == "NTC_44007":
                    value = round(self.instrument.NTC_44007(value),3)
                values[channel] = value
                 

        print(f"{current_time}, {values[2]}, {values[3]}, {values[4]}, PSU {self.PSU_stat}")
        # Write the timestamp and values to the file
        self.file.write(f"{current_time}, {values[0]}, {values[1]}, {values[2]} ,{values[3]},{values[4]},{self.PSU_stat}\n")
        return values        

    def control_power_supply(self, set_value, measured_value):
        """
        Control the power supply based on the comparison of set value and measured value.
        
        :param set_value: float, the set value to compare against.
        :param measured_value: float, the current measured value.
        :param action_if_above: str, the action to perform if the measured value is above the set value.
        :param action_if_below: str, the action to perform if the measured value is below the set value.
        """
        hysteresis = 0.05
        if measured_value > (set_value + hysteresis):
            self.power_supply.set_voltage(0,'P25V')
            self.power_supply.set_voltage(0,'N25V')
            self.PSU_stat= "OFF"
        if measured_value < (set_value - hysteresis):
            self.power_supply.set_voltage(25,'P25V')
            self.power_supply.set_voltage(-25,'N25V')
            self.PSU_stat= "ON"
        #else:
            #do nothing keep output as is
            
    def CloseController(self):
         self.instrument.close()
         self.power_supply.set_voltage(0,'P6V')
         self.power_supply.set_voltage(0,'P25V')
         self.power_supply.set_voltage(0,'N25V')
         self.power_supply.close()
         self.rm.close()
            
if __name__ == "__main__":

    file = "12_Print4HCZB150E_Temp.csv"
    mc = MeasurementController(file)
    mc.initialize_system()
    mc.configInstrCH()
    try:
        while True:
        # Simulate some work
            values = mc.perform_measurement()
            #mc.control_power_supply(80, values[2])
            mc.control_power_supply(40, values[2])
            # Check for user input
            time.sleep(10)

    except KeyboardInterrupt:
        print("Program interrupted with Ctrl+C.")
    
    finally:
        mc.CloseController()
        print("Cleanup complete. Program exiting.")
        
