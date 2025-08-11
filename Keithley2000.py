# -*- coding: utf-8 -*-
"""***************************************************************************
* Title                 :   Configuration
* Filename              :   config.py
* Author                :   %(username)s
* Origin Date           :   %(date)s
* Version               :   00.10
* Project               :   TRUTHS
******************************************************************************
*************** MODULE REVISION LOG ******************************************
*
*  Date        Version    Initials  Description 
*  2021-10-21  00.10      LME       Module Created.
*
******************************************************************************
* \file    %(filename)
* \brief   This module contains the ...
*
***************************************************************************"""

#Standard Modules
import pyvisa
import time

class Keithley2000:
    """
    Base class for the Keithley2000 instrument control
    """
    def __init__(self, device):
        self.device= device
        self.numChannels =10
        self.aquisitionTime = 1
        
    def init(self):
        """Initializes the instruent and resets it"""
        self.device.write('*RST')
        self.device.write('*CLS')
    
    #---- Switch Control Functions ------------
    def closeChannel(self, channelNumber):
        self.device.write('ROUTE:CLOSE (@' + str(channelNumber)+')')
    
    def openChannel(self, channelNumber):
        self.device.write('ROUTE:OPEN:ALL')
    
    def openAllChannels(self):
        command = 'ROUTE:OPEN:ALL'
        self.device.write(command)
    
    def getNumChannels(self):
        return self.numChannels

    #---- Multimeter Functions ------------        
    def configFunction(self, function, measRange, resolution):
        if function =="VOLT":
            self.configVoltageDC(measRange,resolution)
        if function == "RES":
            self.configRes2W(measRange, resolution)
        if function == "FRES":
            self.configRes4W(measRange, resolution)
        
    def readValue(self):
        """ Triggers the meter for a measurement. 
           float measured voltage"""
        command ="INITiate:IMMediate"
        self.device.write(command)
        time.sleep(self.aquisitionTime)
        command = "FETCH?"
        value = self.device.query(command)
        return value
    
    #---- Local used functions -----
    def configVoltageDC(self, measRange,measResolution):
        """ Configures the Meter to DC voltage
             Arguments:
             measRange      -- float measurement range [0.1, 1, 10, 100, 1000]
             measResolution -- int measurement resolution in digit[4,5,6,7]"""
        #Check resolution limits & adjust if necessary
        if(measResolution < 4):
            measResolution = 4
        if(measResolution > 7):
            measResolution=7
        else:
            measResolution= int(measResolution)

        command = "FUNC \"VOLT:DC\";SENS:VOLT:NPLC 10" # Config to Voltage DC
        self.device.write(command)
        
        command = "SENS:VOLT:DC:RANG "+ str(measRange)
        self.device.write(command)
        
        command = "SENS:VOLT:DC:DIG "+ str(measResolution)
        self.device.write(command)
        
        self.aquisitionTime = 1
        
    def configRes2W(self, measRange,measResolution):
        """ Configures the Meter to 2 Wire Resistance 
             Arguments:
             measRange      -- float measurement range [0.1, 1, 10, 100, 1000]
             measResolution -- int measurement resolution in digit[4,5,6,7]"""
        #Check resolution limits & adjust if necessary
        if(measResolution < 4):
            measResolution = 4
        if(measResolution > 7):
            measResolution=7
        else:
            measResolution= int(measResolution)

        command = "FUNC \"RES\";SENS:RES:NPLC 10"
        self.device.write(command)
        
        command = "SENS:RES:RANG "+ str(measRange)
        self.device.write(command)
        
        command = "SENS:RES:DIG "+ str(measResolution)
        self.device.write(command)
        
        self.aquisitionTime = 2

    def getConfig(self):
        config = self.device.query("FUNC?")
        return config
    
    