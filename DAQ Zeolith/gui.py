import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pyvisa


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Measurement Control")
        self.geometry("800x600")

        self.rm = pyvisa.ResourceManager(
            "@py"
        )  # Initialize PyVISA Resource Manager with pyvisa-py backend
        self.instruments = self.get_instruments()
        self.psus = self.get_power_supplies()
        self.num_channels = 4  # Example number of channels

        # Create main frames
        self.running = False  # Flag to control measurement loop
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.create_frames()

        # Initialize the GUI elements
        self.create_widgets()

    def get_instruments(self):
        """Retrieve available instruments using PyVISA."""
        try:
            resources = self.rm.list_resources()
            return [res for res in resources]
        except pyvisa.VisaIOError:
            return []

    def get_power_supplies(self):
        """Retrieve available power supplies using PyVISA."""
        try:
            resources = self.rm.list_resources()
            return [
                res for res in resources
            ]  # Customize based on your power supply identifiers
        except pyvisa.VisaIOError:
            return []

    def create_frames(self):
        self.top_left_frame = tk.Frame(self)
        self.top_right_frame = tk.Frame(self)
        self.middle_left_frame = tk.Frame(self)
        self.middle_right_frame = tk.Frame(self)
        self.bottom_frame = tk.Frame(self)

        self.top_left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.top_right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.middle_left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.middle_right_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.bottom_frame.grid(
            row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew"
        )

    def create_widgets(self):
        # Instrument selection and connection (top left)
        self.label = tk.Label(self.top_left_frame, text="Select Instrument:")
        self.label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.instrument_var = tk.StringVar(self)
        self.instrument_var.set(
            self.instruments[0] if self.instruments else "No instruments available"
        )

        self.instrument_menu = tk.OptionMenu(
            self.top_left_frame,
            self.instrument_var,
            *self.instruments if self.instruments else ["No instruments available"],
        )  # when no instruments are available
        self.instrument_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.connect_button = tk.Button(
            self.top_left_frame,
            text="Connect",
            command=self.connect_instrument,
            width=20,
        )
        self.connect_button.grid(row=1, column=0, padx=5, pady=5)

        self.clear_button = tk.Button(
            self.top_left_frame, text="Clear Chart", command=self.clear_chart, width=20
        )
        self.clear_button.grid(row=1, column=1, padx=5, pady=5)

        self.measure_button = tk.Button(
            self.top_left_frame,
            text="Start Measurement",
            command=self.start_measurement,
            width=20,
        )
        self.measure_button.grid(row=1, column=2, padx=5, pady=5)

        self.stop_button = tk.Button(
            self.top_left_frame,
            text="Stop Measurement",
            command=self.stop_measurement,
            state=tk.DISABLED,
            width=20,
        )
        self.stop_button.grid(row=1, column=3, padx=5, pady=5)

        # Power supply controls (top right)
        self.psu_label = tk.Label(self.top_right_frame, text="Select Power Supply:")
        self.psu_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.psu_var = tk.StringVar(self)
        self.psu_var.set(self.psus[0] if self.psus else "None")

        self.psu_menu = tk.OptionMenu(
            self.top_right_frame, self.psu_var, *self.psus if self.psus else ["None"]
        )
        self.psu_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.connect_psu_button = tk.Button(
            self.top_right_frame,
            text="Connect Power Supply",
            command=self.connect_power_supply,
            width=20,
        )
        self.connect_psu_button.grid(row=1, column=0, padx=5, pady=5, columnspan=2)

        # Set Voltage Controls (below Connect Power Supply button)
        self.voltage_label = tk.Label(self.top_right_frame, text="Set Voltage (V):")
        self.voltage_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        self.voltage_entry = tk.Entry(self.top_right_frame, width=10)
        self.voltage_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        self.set_voltage_button = tk.Button(
            self.top_right_frame, text="Set Voltage", command=self.set_voltage, width=20
        )
        self.set_voltage_button.grid(row=2, column=2, padx=5, pady=5)

        # PID Control Loop
        self.pid_frame = tk.Frame(self.top_right_frame)
        self.pid_frame.grid(
            row=3, column=0, columnspan=4, padx=10, pady=10, sticky=tk.W
        )

        self.channel_label = tk.Label(
            self.pid_frame, text="Select Channel for Temperature:"
        )
        self.channel_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.channel_var = tk.StringVar(self)
        self.channel_var.set("None")

        self.channel_menu = tk.OptionMenu(
            self.pid_frame,
            self.channel_var,
            *[f"CH{ch}" for ch in range(1, self.num_channels + 1)],
        )
        self.channel_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.setpoint_label = tk.Label(self.pid_frame, text="Setpoint Temperature:")
        self.setpoint_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.setpoint_entry = tk.Entry(self.pid_frame, width=10)
        self.setpoint_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        self.p_label = tk.Label(self.pid_frame, text="P:")
        self.p_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        self.p_entry = tk.Entry(self.pid_frame, width=10)
        self.p_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        self.i_label = tk.Label(self.pid_frame, text="I:")
        self.i_label.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)

        self.i_entry = tk.Entry(self.pid_frame, width=10)
        self.i_entry.grid(row=2, column=3, padx=5, pady=5, sticky=tk.W)

        self.d_label = tk.Label(self.pid_frame, text="D:")
        self.d_label.grid(row=2, column=4, padx=5, pady=5, sticky=tk.W)

        self.d_entry = tk.Entry(self.pid_frame, width=10)
        self.d_entry.grid(row=2, column=5, padx=5, pady=5, sticky=tk.W)

        self.start_pid_button = tk.Button(
            self.pid_frame,
            text="Start PID Control",
            command=self.start_pid_control,
            width=20,
        )
        self.start_pid_button.grid(row=3, column=0, padx=5, pady=5)

        self.stop_pid_button = tk.Button(
            self.pid_frame,
            text="Stop PID Control",
            command=self.stop_pid_control,
            width=20,
            state=tk.DISABLED,
        )
        self.stop_pid_button.grid(row=3, column=1, padx=5, pady=5)

        # Channel controls (middle right)
        self.channel_configs = {}
        self.channel_vars = {}
        self.channel_checkboxes = {}
        self.channel_names = {}

        self.create_channel_controls()

        # Initialize the matplotlib figure (middle left)
        self.figure, self.ax = plt.subplots()
        self.ax.set_title("Measurements Over Time")
        self.ax.set_xlabel("Time (HH:MM:SS)")
        self.ax.set_ylabel("Value")

        # Embed the figure in the Tkinter canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.middle_left_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Save buttons (bottom)
        self.save_chart_button = tk.Button(
            self.bottom_frame,
            text="Save Chart as PNG",
            command=self.save_chart_as_png,
            width=20,
        )
        self.save_chart_button.grid(row=0, column=0, padx=5, pady=5)

        self.save_csv_button = tk.Button(
            self.bottom_frame,
            text="Save Measurements as CSV",
            command=self.save_measurements_as_csv,
            width=20,
        )
        self.save_csv_button.grid(row=0, column=1, padx=5, pady=5)

        self.result_label = tk.Label(self.bottom_frame, text="", width=80)
        self.result_label.grid(row=0, column=2, columnspan=2, padx=5, pady=5)

    def connect_instrument(self):
        selected_instrument = self.instrument_var.get()
        print(f"Connecting to instrument: {selected_instrument}")
        # Implement the actual connection logic here

    def clear_chart(self):
        print("Clearing chart")
        self.ax.clear()
        self.canvas.draw()

    def start_measurement(self):
        print("Starting measurement")

    def stop_measurement(self):
        print("Stopping measurement")

    def connect_power_supply(self):
        selected_psu = self.psu_var.get()
        print(f"Connecting to power supply: {selected_psu}")
        # Implement the actual connection logic here

    def set_voltage(self):
        voltage = self.voltage_entry.get()
        print(f"Setting voltage to {voltage} V")
        # Implement the actual voltage setting logic here

    def start_pid_control(self):
        print("Start PID control")

    def stop_pid_control(self):
        print("Stop PID control")

    def create_channel_controls(self):
        # Example function to create channel controls dynamically
        for i in range(self.num_channels):
            var = tk.StringVar(self)
            var.set(f"Channel {i+1}")
            self.channel_vars[f"ch{i+1}"] = var
            cb = tk.Checkbutton(
                self.middle_right_frame, text=f"Channel {i+1}", variable=var
            )
            cb.grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            self.channel_checkboxes[f"ch{i+1}"] = cb
            self.channel_names[f"ch{i+1}"] = var

    def save_chart_as_png(self):
        print("Save chart as PNG")

    def save_measurements_as_csv(self):
        print("Save measurements as CSV")

    def on_closing(self):
        self.running = False  # Set running flag to False to stop any ongoing loops

        # Close any open instrument connections
        try:
            if hasattr(self, "instrument") and self.instrument:
                self.instrument.close()
        except:
            pass

        try:
            if hasattr(self, "psu") and self.psu:
                self.psu.close()
        except:
            pass

        try:
            if hasattr(self, "rm") and self.rm:
                self.rm.close()
        except:
            pass

        self.destroy()
        self.quit()  # Ensure the mainloop exits


if __name__ == "__main__":
    try:
        app = Application()
        app.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        # Ensure the process exits
        import sys

        sys.exit()
