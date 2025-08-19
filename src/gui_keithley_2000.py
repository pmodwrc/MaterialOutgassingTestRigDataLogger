import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
import pyvisa
import time
from datetime import datetime
import csv
from Keithley2000 import Keithley2000


class KeithleyGUI:
    def __init__(self, master, num_channels=20, interval=1):
        self.master = master
        self.num_channels = num_channels
        self.interval = interval
        self.rm = pyvisa.ResourceManager()
        self.instruments = self.get_instruments()
        self.selected_instrument = None
        self.keithley = None

        self.create_frames(master)
        self.create_widgets(master)

    def get_instruments(self):
        """Retrieve available instruments using PyVISA."""
        try:
            resources = self.rm.list_resources()
            return [res for res in resources]
        except pyvisa.VisaIOError:
            return []

    def create_frames(self, master):
        """Create the main frames for the GUI."""
        self.top_left_frame = tk.Frame(master)
        self.top_right_frame = tk.Frame(master)
        self.middle_left_frame = tk.Frame(master)
        self.middle_right_frame = tk.Frame(master)
        self.bottom_frame = tk.Frame(master)

        self.top_left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.top_right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.middle_left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.middle_right_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.bottom_frame.grid(
            row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew"
        )

    def create_widgets(self, master):
        """Create the widgets for the GUI."""
        # Instrument selection and connection (top left)
        self.label = tk.Label(self.top_left_frame, text="Select Instrument:")
        self.label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.instrument_var = tk.StringVar(master)
        self.instrument_var.set(self.instruments[0] if self.instruments else "None")

        self.instrument_menu = tk.OptionMenu(
            self.top_left_frame,
            self.instrument_var,
            *self.instruments,
            command=self.on_instrument_change,
        )
        self.instrument_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.connect_button = tk.Button(
            self.top_left_frame,
            text="Connect",
            command=self.connect_instrument,
            width=15,
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
        self.is_measuring = False
        self.measurements = {channel: [] for channel in range(1, self.num_channels + 1)}
        self.times = []

    def create_channel_controls(self):
        """Create controls for each channel in the middle right frame."""
        channel_frame = tk.Frame(self.middle_right_frame)
        channel_frame.pack()

        for channel in range(
            1, self.num_channels + 1
        ):  # Create controls for each channel
            var = tk.BooleanVar(value=True)
            checkbox = tk.Checkbutton(channel_frame, text=f"CH{channel}", variable=var)
            checkbox.grid(row=channel - 1, column=0, padx=5, pady=2, sticky=tk.W)
            self.channel_vars[channel] = var

            options = [
                "Voltage",
                "Current",
                "Resistance",
                "NTC_44006",
                "NTC_44007",
                "PT100",
                "Frequency",
            ]
            config_var = tk.StringVar(value="Voltage")
            config_menu = tk.OptionMenu(channel_frame, config_var, *options)
            config_menu.grid(row=channel - 1, column=1, padx=5, pady=2, sticky=tk.W)
            self.channel_configs[channel] = config_var

            name_entry = tk.Entry(channel_frame, width=20)
            name_entry.grid(row=channel - 1, column=2, padx=5, pady=2, sticky=tk.W)
            self.channel_names[channel] = name_entry

    def update_connect_button_color(self, button):
        """Change the button color to green to indicate a successful connection."""
        button.config(bg="green", fg="white")

    def on_instrument_change(self, _value):
        """Reset Connect button color when a new instrument is selected."""
        # Switch back to white to indicate not connected after selection change
        if hasattr(self, "connect_button"):
            self.connect_button.config(bg="white", fg="black")
        # Optionally clear any existing instrument handle (kept minimal per request)
        # self.instrument = None
        # self.keithley = None

    def connect_instrument(self):
        self.selected_instrument = self.instrument_var.get()
        if self.selected_instrument != "None":
            try:
                self.instrument = self.rm.open_resource(self.selected_instrument)
                idn_response = self.instrument.query("*IDN?")
                messagebox.showinfo(
                    "Connected",
                    f"Connected to {self.selected_instrument}\nIDN: {idn_response}",
                )
                self.update_connect_button_color(self.connect_button)
                self.keithley = Keithley2000(self.instrument)
                # Set a longer timeout for measurements (10 seconds)
                self.instrument.timeout = 10000
                # Initialize the instrument
                self.keithley.init()
            except pyvisa.VisaIOError:
                messagebox.showerror(
                    "Connection Error", "Failed to connect to the instrument."
                )

    def measure_and_plot(self):
        start_time = time.time()
        while self.is_measuring:
            full_timestamp = datetime.now()
            self.times.append(full_timestamp)
            for channel in range(1, self.num_channels + 1):
                if self.channel_vars[channel].get():  # if channel is selected
                    config = self.channel_configs[channel].get()
                    measurement = self.keithley.measureChanel(config, channel, 10, 5)
                    print(f"Channel {channel} measurement: {measurement}")
                    # Handle None values - replace with 0
                    if measurement is None:
                        # Use 0 if no previous measurements
                        measurement = 0.0
                        print(
                            f"Channel {channel} timeout/error - using fallback value: {measurement}"
                        )
                    self.measurements[channel].append(measurement)
            self.ax.clear()
            self.ax.set_title("Measurements Over Time")
            self.ax.set_xlabel("Time (HH:MM:SS)")
            self.ax.set_ylabel("Value")
            # Plot data for each selected channel
            for channel in range(1, self.num_channels + 1):
                if (
                    self.channel_vars[channel].get()
                    and len(self.measurements[channel]) > 0
                ):
                    times_plot = [
                        dt.timestamp()
                        for dt in self.times[: len(self.measurements[channel])]
                    ]
                    self.ax.plot(
                        times_plot, self.measurements[channel], label=f"CH{channel}"
                    )
            if any(
                self.channel_vars[channel].get()
                for channel in range(1, self.num_channels + 1)
            ):
                self.ax.legend()
            self.ax.xaxis.set_major_formatter(
                FuncFormatter(
                    lambda x, _: datetime.fromtimestamp(x).strftime("%H:%M:%S")
                )
            )
            self.canvas.draw()
            latest_measurements = [
                (self.measurements[channel][-1] if self.measurements[channel] else None)
                for channel in range(1, self.num_channels + 1)
            ]
            self.result_label.config(text=f"Latest Measurements: {latest_measurements}")
            self.master.update()
            time.sleep(self.interval)

    def start_measurement(self):
        if hasattr(self, "instrument"):
            self.is_measuring = True
            self.stop_button.config(state=tk.NORMAL)
            self.measure_button.config(state=tk.DISABLED)
            self.measure_and_plot()
        else:
            messagebox.showwarning("Warning", "No instrument connected.")

    def stop_measurement(self):
        self.is_measuring = False
        self.stop_button.config(state=tk.DISABLED)
        self.measure_button.config(state=tk.NORMAL)

    def clear_chart(self):
        # Clear measurements and reset plot
        self.measurements = {channel: [] for channel in range(1, self.num_channels + 1)}
        self.times = []
        self.ax.clear()
        self.ax.set_title("Measurements Over Time")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Value")
        self.ax.legend()
        self.canvas.draw()

    def save_chart_as_png(self):
        """Save the current chart as a PNG file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png", filetypes=[("PNG files", "*.png")]
        )
        if file_path:
            self.figure.savefig(file_path)
            messagebox.showinfo("Saved", f"Chart saved as {file_path}")

    def save_measurements_as_csv(self):
        """Save measurements to a CSV file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            with open(file_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                # Write header
                header = ["Timestamp"] + [
                    f"CH{channel}" for channel in range(1, self.num_channels + 1)
                ]
                writer.writerow(header)

                # Find the longest measurement list to determine rows
                max_len = max(
                    len(self.times), max(len(v) for v in self.measurements.values())
                )

                # Write rows
                for i in range(max_len):
                    row = (
                        [self.times[i].strftime("%Y-%m-%d %H:%M:%S")]
                        if i < len(self.times)
                        else ""
                    )
                    row += [
                        (
                            self.measurements[channel][i]
                            if i < len(self.measurements[channel])
                            else ""
                        )
                        for channel in range(1, self.num_channels + 1)
                    ]
                    writer.writerow(row)

            messagebox.showinfo("Saved", f"Measurements saved as {file_path}")

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
