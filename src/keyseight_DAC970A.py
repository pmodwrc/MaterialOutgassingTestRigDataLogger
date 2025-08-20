import pyvisa
import time
import math


class KeysightDAQ970A:
    """A class to interface with the Keysight DAQ970A Data Acquisition System."""

    def __init__(self, device):
        self.device = device
        self.num_of_channels = 19
        self.aquisition_time = 1

    def init(self):
        """Initializes the instruent and resets it"""
        self.device.write("*RST")
        self.device.write("*CLS")
        # self.device.write("*ABOR")

    # ---- Switch Control Functions ------------
    def closeChannel(self, channelNumber):
        self.device.write("ROUT:OPEN:ALL")  # Open all channels
        time.sleep(0.1)
        self.device.write(f"ROUT:CLOS (@{channelNumber})")  # Close the specific channel
        return

    def openChannel(self, channelNumber):
        self.device.write("ROUTE:OPEN (@" + str(channelNumber) + ")")

    def openAllChannels(self):
        command = "ROUTE:OPEN:ALL"
        self.device.write(command)

    def getNumChannels(self):
        return self.numChannels

    # ---- Multimeter Functions ------------
    def configFunction(self, function, measRange, resolution):
        if function == "VOLT":
            self.configVoltageDC(measRange, resolution)
        if function == "RES":
            self.configRes2W(measRange, resolution)
        if function == "FRES":
            self.configRes4W(measRange, resolution)

    def readValue(self):
        """Reads the value from the instrument in the current configuration."""
        try:
            response = self.device.query("READ?")
            # Remove non-numeric and non-standard characters
            cleaned = "".join(c for c in response if c in "0123456789.-eE+")
            value = float(cleaned)
            return value
        except (pyvisa.VisaIOError, ValueError) as e:
            print(f"Keithley measurement error: {e}")
            return None

    def measureChannel(self, config, channel, measRange=1000, measResolution=7):
        """closes one specific channel, configures it and measures the value, which is cleaned and returned"""
        channel += 100  # channel numbering starts at 100
        try:
            if config == "Voltage":
                self.configVoltageDC(channel, measRange, measResolution)
            elif config == "Resistance":
                self.configRes2W(channel, measRange, measResolution)
            elif config == "Current":
                self.configCurrentDC(channel, measRange, measResolution)
            elif config == "Frequency":
                self.configFreq(channel, measRange, measResolution)
            elif config == "PT100":
                return self.measurePt100(channel, measRange, measResolution)
            elif config == "NTC_44006":
                return self.measureNTC_44006(channel, measRange, measResolution)
            elif config == "NTC_44007":
                return self.measureNTC_44007(channel, measRange, measResolution)
            time.sleep(self.aquisition_time)
            return self.readValue()
        except pyvisa.VisaIOError as e:
            print(f"Keyseight DAQ970A measurement error: {e}")
            return None

    # ---- Local used functions -----
    def configVoltageDC(self, channel, measRange, measResolution):
        """Configures the Meter to DC voltage
        Arguments:
        measRange      -- float measurement range [0.1, 1, 10, 100, 1000]
        measResolution -- int measurement resolution in digit[4,5,6,7]"""
        self.device.write(f"CONF:VOLT:DC (@{channel})")

    def configRes2W(self, channel, measRange, measResolution):
        """Configures the Meter to 2 Wire Resistance
        Arguments:
        measRange      -- float measurement range [0.1, 1, 10, 100, 1000]
        measResolution -- int measurement resolution in digit[4,5,6,7]"""
        self.device.timeout = 10000  # Set timeout to 10 seconds
        command = f"CONF:RES (@{channel})"
        self.device.write(command)

    def configCurrentDC(self, channel, measRange, measResolution):
        """Configures the Meter to DC current
        Arguments:
        measRange      -- float measurement range [0.1, 1, 10, 100, 1000]
        measResolution -- int measurement resolution in digit[4,5,6,7]"""
        self.device.write(f"CONF:CURR:DC (@{channel})")

    def configFreq(self, channel, measRange, measResolution):
        """Configures the Meter to Frequency
        Arguments:
        measRange      -- float measurement range [0.1, 1, 10, 100, 1000]
        measResolution -- int measurement resolution in digit[4,5,6,7]"""
        command = f"CONF:FREQ (@{channel})"
        self.device.write(command)

    def measurePt100(self, measRange, measResolution):
        """Configures the Meter to PT100 temperature measurement"""
        self.configRes2W(measRange, measResolution)
        resistance = self.readValue()
        # t=(-AR_0+srt((AR_0)^2-4BR_0(R_0-R)))/2BR_0
        A = 3.9827e-3
        B = -5.875e-7
        R_0 = 100.0  # PT100 resistance at 0°C
        temperature = (
            -A * R_0 + (A**2 * R_0**2 - 4 * B * R_0 * (R_0 - resistance)) ** 0.5
        ) / (2 * B * R_0)
        return temperature

    def measureNTC_44006(self, measRange, measResolution):
        """Calculate temperature from NTC thermistor resistance using Steinhart-Hart equation."""
        self.configRes2W(measRange, measResolution)
        resistance = self.readValue()
        A = 1.032e-3
        B = 2.387e-4
        C = 1.580e-7
        log_resistance = math.log(resistance)
        inv_temp = A + B * log_resistance + C * log_resistance**3
        temperature_kelvin = 1 / inv_temp
        temperature_celsius = temperature_kelvin - 273.15
        return temperature_celsius

    def measureNTC_44007(self, measRange, measResolution):
        """Calculate temperature from NTC thermistor resistance using Steinhart-Hart equation."""
        self.configRes2W(measRange, measResolution)
        resistance = self.readValue()
        A = 1.285e-3
        B = 2.362e-4
        C = 9.285e-8
        log_resistance = math.log(resistance)
        inv_temp = A + B * log_resistance + C * log_resistance**3
        temperature_kelvin = 1 / inv_temp
        temperature_celsius = temperature_kelvin - 273.15
        return temperature_celsius

    def close(self):
        self.device.close()

    def getConfig(self):
        config = self.device.query("FUNC?")
        return config
