import customtkinter as ctk
from tkinter import messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
import pyvisa
import time
from datetime import datetime
import csv
from Keithley2000 import Keithley2000
from keyseight_DAC970A import KeysightDAQ970A
import os


class KeithleyCustomTkinterGUI:
    """This is the ui for the Material Outgassing Test Rig Data Logger."""

    def __init__(self, master):
        master.title("measurement ui")
        self.master = master
        self.number_of_channels = 20
        self.channel_configs = {}
        self.config_file = "channel_configs_default.csv"
        self.config_file_path = ""
        self.config_file_change_flag = False
        self.interval = 1
        self.rm = pyvisa.ResourceManager()
        self.instruments = self.get_instruments()
        self.selected_instrument = None
        self.instrument = None
        # Define default button colors
        self.default_button_fg_color = "#3b8ed0"
        self.default_button_text_color = "white"
        self.default_grid_color = "#f7f7f7"
        master.configure(bg="white")

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
        self.top_left_frame = ctk.CTkFrame(
            master, corner_radius=5, fg_color=self.default_grid_color
        )
        self.top_right_frame = ctk.CTkFrame(
            master, corner_radius=5, fg_color=self.default_grid_color
        )
        self.middle_left_frame = ctk.CTkFrame(
            master, corner_radius=5, fg_color=self.default_grid_color
        )
        self.middle_right_frame = ctk.CTkFrame(
            master, corner_radius=5, fg_color=self.default_grid_color
        )
        self.bottom_frame = ctk.CTkFrame(
            master, corner_radius=5, fg_color=self.default_grid_color
        )

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
        self.create_instrument_controls(master)

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

        # Embed the figure in the CustomTkinter canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.middle_left_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        # Save buttons (bottom)
        self.save_chart_button = ctk.CTkButton(
            self.bottom_frame,
            text="Save Chart as PNG",
            command=self.save_chart_as_png,
            width=20,
            fg_color=self.default_button_fg_color,
            text_color=self.default_button_text_color,
        )
        self.save_chart_button.grid(row=0, column=0, padx=5, pady=5)
        self.save_csv_button = ctk.CTkButton(
            self.bottom_frame,
            text="Save Measurements as CSV",
            command=self.save_measurements_as_csv,
            width=20,
            fg_color=self.default_button_fg_color,
            text_color=self.default_button_text_color,
        )
        self.save_csv_button.grid(row=0, column=1, padx=5, pady=5)
        self.result_label = ctk.CTkLabel(self.bottom_frame, text="", width=80)
        self.result_label.grid(row=0, column=2, columnspan=2, padx=5, pady=5)
        self.is_measuring = False
        self.measurements = {
            channel: [] for channel in range(1, self.number_of_channels + 1)
        }
        self.times = []
        self.clear_button = ctk.CTkButton(
            self.bottom_frame,
            text="Clear Chart",
            command=self.clear_chart,
            width=20,
            fg_color="#ff0000",
            text_color=self.default_button_text_color,
        )
        self.clear_button.grid(row=0, column=4, padx=5, pady=5)

    def create_instrument_controls(self, master):
        # Add a dropdown menu for device type selection
        self.label = ctk.CTkLabel(self.top_left_frame, text="Select Instrument Model:")
        self.label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        device_types = ["Keithley2000", "KeysightDAQ970A"]
        self.device_type_var = ctk.StringVar(value=device_types[0])
        self.device_type_menu = ctk.CTkOptionMenu(
            self.top_left_frame,
            variable=self.device_type_var,
            values=device_types,
            fg_color=self.default_button_fg_color,
            text_color=self.default_button_text_color,
        )
        self.device_type_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Instrument address selection
        self.label = ctk.CTkLabel(
            self.top_left_frame, text="Select Instrument Address:"
        )
        self.label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.instrument_var = ctk.StringVar(master)
        self.instrument_var.set(self.instruments[0] if self.instruments else "None")
        self.instrument_menu = ctk.CTkOptionMenu(
            self.top_left_frame,
            variable=self.instrument_var,
            values=self.instruments,
            command=self.on_instrument_change,
            fg_color=self.default_button_fg_color,
            text_color=self.default_button_text_color,
        )
        self.instrument_menu.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.connect_button = ctk.CTkButton(
            self.top_left_frame,
            text="Connect",
            command=self.connect_instrument,
            width=15,
            fg_color=self.default_button_fg_color,
            text_color=self.default_button_text_color,
        )

        self.connect_button.grid(row=1, column=0, padx=5, pady=5)

        self.measure_button = ctk.CTkButton(
            self.top_left_frame,
            text="Start Measurement",
            command=self.start_measurement,
            width=20,
            fg_color=self.default_button_fg_color,
            text_color=self.default_button_text_color,
        )
        self.measure_button.grid(row=1, column=2, padx=5, pady=5)

        self.stop_button = ctk.CTkButton(
            self.top_left_frame,
            text="Stop Measurement",
            command=self.stop_measurement,
            state="disabled",
            width=20,
            fg_color=self.default_button_fg_color,
            text_color=self.default_button_text_color,
        )
        self.stop_button.grid(row=1, column=3, padx=5, pady=5)

    def create_channel_controls(self):
        """Create controls for each channel in the middle right frame."""
        channel_frame = self.middle_right_frame
        # channel_frame.pack()
        self.load_channel_configs(self.config_file)
        for channel in range(1, self.number_of_channels + 1):
            active = False
            config = "None"
            name = "channel_name"
            if channel in self.channel_configs:
                print(
                    f"Channel {channel} settings found in config: {self.channel_configs[channel]}"
                )
                active = self.channel_configs[channel]["active"]
                config = self.channel_configs[channel]["config"]
            print(f"Channel {channel} settings: {active}, {config}")
            var = ctk.BooleanVar(value=active)
            checkbox = ctk.CTkCheckBox(channel_frame, text=f"CH{channel}", variable=var)
            # Add extra padding only to the first channel
            pady_val = (5, 2) if channel == 1 else 2
            checkbox.grid(row=channel - 1, column=0, padx=5, pady=pady_val, sticky="w")
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
            config_var = ctk.StringVar(value=config)
            config_menu = ctk.CTkOptionMenu(
                channel_frame,
                variable=config_var,
                values=options,
                fg_color=self.default_button_fg_color,
                text_color=self.default_button_text_color,
            )
            config_menu.grid(
                row=channel - 1, column=1, padx=5, pady=pady_val, sticky=ctk.W
            )
            self.channel_configs[channel] = config_var
            name_entry = ctk.CTkEntry(channel_frame, width=100)
            name_entry.insert(0, name)
            name_entry.grid(
                row=channel - 1, column=2, padx=5, pady=pady_val, sticky=ctk.W
            )
            self.channel_names[channel] = name_entry
        # Add a dropdown menu to select config files in the folder
        config_files = [
            f
            for f in os.listdir(os.path.dirname(os.path.abspath(__file__)))
            if f.startswith("channel_configs") and f.endswith(".csv")
        ]
        self.config_file_var = ctk.StringVar(value=os.path.basename(self.config_file))
        config_menu = ctk.CTkOptionMenu(
            channel_frame,
            variable=self.config_file_var,
            values=config_files,
            fg_color=self.default_button_fg_color,
            text_color=self.default_button_text_color,
            command=lambda value: self.on_config_file_change(value),
        )
        config_menu.grid(
            row=self.number_of_channels,
            column=0,
            columnspan=3,
            padx=5,
            pady=(10, 2),
            sticky="ew",
        )
        # Add "Open Channel Config CSV" button at the bottom of the channel controls
        open_config_button = ctk.CTkButton(
            channel_frame,
            text="Open Channel Config CSV",
            command=lambda: (
                os.startfile(self.config_file_path)
                if os.path.exists(self.config_file_path)
                else messagebox.showwarning(
                    "File Not Found", "Channel config CSV not found."
                )
            ),
            width=20,
            fg_color=self.default_button_fg_color,
            text_color=self.default_button_text_color,
        )
        open_config_button.grid(
            row=self.number_of_channels + 1,
            column=0,
            columnspan=3,
            padx=5,
            pady=2,
            sticky="ew",
        )

    def on_config_file_change(self, config_file):
        # Set new config file path
        self.config_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), config_file
        )
        self.config_file = config_file
        # Destroy and rebuild the window with new config
        for widget in self.middle_right_frame.winfo_children():
            widget.destroy()
        self.config_file_change_flag = False
        self.create_channel_controls()

    def load_channel_configs(self, config_file):
        # Try to load channel config from CSV
        self.config_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), config_file
        )
        self.channel_configs = {}
        if os.path.exists(self.config_file_path):
            with open(self.config_file_path, mode="r", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        ch = int(row.get("channel_nr"))
                        active = row.get("active", "False")
                        config = row.get("configuration", "None")
                        self.channel_configs[ch] = {
                            "active": active,
                            "config": config,
                        }
                    except Exception:
                        continue
        self.number_of_channels = max(self.channel_configs.keys())
        print(
            f"Loaded {self.number_of_channels} channel configurations from {config_file}"
        )
        return

    def update_connect_button(self, button):
        """Change the button color to green to indicate a successful connection."""
        button.configure(fg_color="green", text_color="white")
        button.configure(text="Connected")

    def on_instrument_change(self, _value):
        """Reset Connect button color when a new instrument is selected."""
        # Switch back to white to indicate not connected after selection change
        if hasattr(self, "connect_button"):
            self.connect_button.configure(fg_color="#3b8ed0", text_color="white")
            self.connect_button.configure(text="Connect")
        # Optionally clear any existing instrument handle (kept minimal per request)
        self.instrument = None

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

                self.update_connect_button(self.connect_button)
                if self.device_type_var.get() == "Keithley2000":
                    self.instrument = Keithley2000(self.instrument)
                elif self.device_type_var.get() == "KeysightDAQ970A":
                    self.instrument = KeysightDAQ970A(self.instrument)
                # Set a longer timeout for measurements (10 seconds)
                self.instrument.timeout = 10000
                # Initialize the instrument
                self.instrument.init()
            except pyvisa.VisaIOError:
                messagebox.showerror(
                    "Connection Error", "Failed to connect to the instrument."
                )

    def measure_and_plot(self):
        start_time = time.time()
        while self.is_measuring:
            full_timestamp = datetime.now()
            self.times.append(full_timestamp)
            for channel in range(1, self.number_of_channels + 1):
                if self.channel_vars[channel].get():  # if channel is selected
                    config = self.channel_configs[channel].get()
                    measurement = self.instrument.measureChannel(config, channel, 10, 5)
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
            for channel in range(1, self.number_of_channels + 1):
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
                for channel in range(1, self.number_of_channels + 1)
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
                for channel in range(1, self.number_of_channels + 1)
            ]
            self.result_label.configure(
                text=f"Latest Measurements: {latest_measurements}"
            )
            self.master.update()
            time.sleep(self.interval)

    def start_measurement(self):
        if hasattr(self, "instrument"):
            self.is_measuring = True
            self.stop_button.configure(state=ctk.NORMAL)
            self.measure_button.configure(state=ctk.DISABLED)
            self.measure_and_plot()
        else:
            messagebox.showwarning("Warning", "No instrument connected.")

    def stop_measurement(self):
        self.is_measuring = False
        self.stop_button.configure(state=ctk.DISABLED)
        self.measure_button.configure(state=ctk.NORMAL)

    def clear_chart(self):
        # Clear measurements and reset plot
        self.measurements = {
            channel: [] for channel in range(1, self.number_of_channels + 1)
        }
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
                    f"CH{channel}" for channel in range(1, self.number_of_channels + 1)
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
                        for channel in range(1, self.number_of_channels + 1)
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
