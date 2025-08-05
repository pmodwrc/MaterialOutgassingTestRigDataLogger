from keithley_measurement import KeithleyMeasurement
from power_supply_control import PowerSupplyControl


class ControlLoop:
    def __init__(self, keithley_resource, power_supply_resource):
        self.keithley = KeithleyMeasurement(keithley_resource)
        self.psu = PowerSupplyControl(power_supply_resource)

    def run(self, ctrlValue):
        try:
            while True:
                voltage = self.keithley.measure_voltage()
                if voltage is not None:
                    print(f"Measured Voltage: {voltage} V")
                # Add control loop logic here
        finally:
            self.psu.turn_off()
            self.keithley.close()
            self.psu.close()
