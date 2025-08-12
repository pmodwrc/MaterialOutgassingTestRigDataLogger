import pyvisa
import time


class Keithley2000:
    """
    Base class for the Keithley2000 instrument control
    """

    def __init__(self, device):
        self.device = device
        self.numChannels = 10
        self.aquisitionTime = 1

    def init(self):
        """Initializes the instruent and resets it"""
        self.device.write("*RST")
        self.device.write("*CLS")

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

    def measureChanel(self, config, chanel, measRange=1000, measResolution=7):
        """closes one specific channel, configures it and measures the value, which is cleaned and returned"""
        try:
            self.openAllChannels()
            self.closeChannel(chanel)
            if config == "Voltage":
                self.configVoltageDC(measRange, measResolution)
            elif config == "Resistance":
                self.configRes2W(measRange, measResolution)
            elif config == "Current":
                self.configCurrentDC(measRange, measResolution)
            elif config == "PT100":
                self.configRes2W(measRange, measResolution)
                response = self.device.query("READ?")
                cleaned = float("".join(c for c in response if c in "0123456789.-eE+"))
                # t=(-AR_0+srt((AR_0)^2-4BR_0(R_0-R)))/2BR_0
                A = 3.9827e-3
                B = -5.875e-7
                R_0 = 100.0  # PT100 resistance at 0°C
                temperature = (
                    -A * R_0 + (A**2 * R_0**2 - 4 * B * R_0 * (R_0 - cleaned)) ** 0.5
                ) / (2 * B * R_0)
                return temperature
            elif config == "Frequency":
                self.configFreq(measRange, measResolution)
            time.sleep(self.aquisitionTime)
            response = self.device.query("READ?")
            # Filter out the response to numeric
            cleaned = "".join(c for c in response if c in "0123456789.-eE+")
            try:
                value = float(cleaned)
            except ValueError:
                value = None
            return value
        except (pyvisa.VisaIOError, ValueError) as e:
            print(f"Keithley measurement error: {e}")
            return None

    # ---- Local used functions -----
    def configVoltageDC(self, measRange, measResolution):
        """Configures the Meter to DC voltage
        Arguments:
        measRange      -- float measurement range [0.1, 1, 10, 100, 1000]
        measResolution -- int measurement resolution in digit[4,5,6,7]"""
        # Check resolution limits & adjust if necessary
        if measResolution < 4:
            measResolution = 4
        if measResolution > 7:
            measResolution = 7
        else:
            measResolution = int(measResolution)

        command = 'FUNC "VOLT:DC";SENS:VOLT:NPLC 10'  # Config to Voltage DC
        self.device.write(command)

        command = "SENS:VOLT:DC:RANG " + str(measRange)
        self.device.write(command)

        command = "SENS:VOLT:DC:DIG " + str(measResolution)
        self.device.write(command)

        self.aquisitionTime = 1

    def configRes2W(self, measRange, measResolution):
        """Configures the Meter to 2 Wire Resistance
        Arguments:
        measRange      -- float measurement range [0.1, 1, 10, 100, 1000]
        measResolution -- int measurement resolution in digit[4,5,6,7]"""
        command = "CONF:RES"
        self.device.write(command)

    def configCurrentDC(self, measRange, measResolution):
        """Configures the Meter to DC current
        Arguments:
        measRange      -- float measurement range [0.1, 1, 10, 100, 1000]
        measResolution -- int measurement resolution in digit[4,5,6,7]"""
        # Check resolution limits & adjust if necessary
        if measResolution < 4:
            measResolution = 4
        if measResolution > 7:
            measResolution = 7
        else:
            measResolution = int(measResolution)

        command = 'FUNC "CURR:DC";SENS:CURR:NPLC 10'  # Config to Current DC
        self.device.write(command)

        command = "SENS:CURR:DC:RANG " + str(measRange)
        self.device.write(command)

        command = "SENS:CURR:DC:DIG " + str(measResolution)
        self.device.write(command)

        self.aquisitionTime = 1

    def configFreq(self, measRange, measResolution):
        """Configures the Meter to Frequency
        Arguments:
        measRange      -- float measurement range [0.1, 1, 10, 100, 1000]
        measResolution -- int measurement resolution in digit[4,5,6,7]"""
        command = "conf:FREQ"
        self.device.write(command)

    def getConfig(self):
        config = self.device.query("FUNC?")
        return config
