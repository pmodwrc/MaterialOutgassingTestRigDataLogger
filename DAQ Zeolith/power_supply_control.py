import pyvisa


class PowerSupplyControl:
    def __init__(self, rm):
        self.rm = rm

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
                index = int(
                    input(
                        f"Select the Powersupply by its index (0-{len(instruments) - 1}): "
                    )
                )
                if 0 <= index < len(instruments):
                    resource_name = instruments[index]
                    break
                else:
                    print(
                        f"Please enter a number between 0 and {len(instruments) - 1}."
                    )
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        self.psu = self.rm.open_resource(resource_name)
        self.psu.timeout = 5000

        idn_string = self.psu.query("*IDN?")
        print(f"Connected to: {idn_string.strip()}")

    def set_voltage(self, voltage, channel):
        if not self.psu.query("OUTP?"):
            self.turn_on()
        # @ voltage float
        # @ channel [P6V, P25V, N25V]

        if channel == "P6V":
            voltage = max(0, min(6.0, voltage))
        if channel == "P25V":
            voltage = min(25.0, voltage)
        if channel == "N25V":
            voltage = max(-25, voltage)
        try:
            self.psu.write("INST ", channel)
            self.psu.write(f"VOLT {voltage}")
        except pyvisa.VisaIOError as e:
            print(f"Power supply control error: {e}")

    def trig_output(self):
        # Set trigger source to immediate
        self.psu.write("TRIG:SOUR IMM")
        # Initiate the trigger
        self.psu.write("INIT")

    def turn_on(self):
        self.psu.write("OUTP ON")

    def turn_off(self):
        self.psu.write("OUTP OFF")

    def close(self):
        self.psu.close()
        print("Conection to PSU closed")


if __name__ == "__main__":
    rm = pyvisa.ResourceManager()
    psu = PowerSupplyControl(rm)
    psu.connect()
    psu.set_voltage(0, "P25V")
    psu.close()
    rm.close()
