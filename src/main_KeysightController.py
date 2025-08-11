from matplotlib.ticker import FuncFormatter
from datetime import datetime

import tkinter as tk
from tkinter import messagebox, filedialog
import pyvisa
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import math
import csv
from Keithley2000 import Keithley2000
from gui_keithley_2000 import KeithleyGUI


# class KeithleyController:
#     def __init__(self, master, num_channels=20, interval=1):
#         self.master = master
#         master.title("Keithley 2000 Controller")
#         self.num_channels = num_channels  # Set the number of channels
#         self.interval = interval  # Set the measurement interval
#         self.rm = pyvisa.ResourceManager()
#         self.instruments = self.rm.list_resources()

#         # Create main frames
#         self.top_left_frame = tk.Frame(master)
#         self.top_right_frame = tk.Frame(master)
#         self.middle_left_frame = tk.Frame(master)
#         self.middle_right_frame = tk.Frame(master)
#         self.bottom_frame = tk.Frame(master)

#         self.top_left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
#         self.top_right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
#         self.middle_left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
#         self.middle_right_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
#         self.bottom_frame.grid(
#             row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew"
#         )

#         # Instrument selection and connection (top left)
#         self.label = tk.Label(self.top_left_frame, text="Select Instrument:")
#         self.label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

#         self.instrument_var = tk.StringVar(master)
#         self.instrument_var.set(self.instruments[0] if self.instruments else "None")

#         self.instrument_menu = tk.OptionMenu(
#             self.top_left_frame, self.instrument_var, *self.instruments
#         )
#         self.instrument_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

#         self.connect_button = tk.Button(
#             self.top_left_frame,
#             text="Connect",
#             command=self.connect_instrument,
#             width=20,
#         )
#         self.connect_button.grid(row=1, column=0, padx=5, pady=5)

#         self.clear_button = tk.Button(
#             self.top_left_frame, text="Clear Chart", command=self.clear_chart, width=20
#         )
#         self.clear_button.grid(row=1, column=1, padx=5, pady=5)

#         self.measure_button = tk.Button(
#             self.top_left_frame,
#             text="Start Measurement",
#             command=self.start_measurement,
#             width=20,
#         )
#         self.measure_button.grid(row=1, column=2, padx=5, pady=5)

#         self.stop_button = tk.Button(
#             self.top_left_frame,
#             text="Stop Measurement",
#             command=self.stop_measurement,
#             state=tk.DISABLED,
#             width=20,
#         )
#         self.stop_button.grid(row=1, column=3, padx=5, pady=5)

#         # Power supply controls (top right)
#         self.psu_label = tk.Label(self.top_right_frame, text="Select Power Supply:")
#         self.psu_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

#         self.psu_var = tk.StringVar(master)
#         self.psu_var.set(self.instruments[0] if self.instruments else "None")

#         self.psu_menu = tk.OptionMenu(
#             self.top_right_frame, self.psu_var, *self.instruments
#         )
#         self.psu_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

#         self.connect_psu_button = tk.Button(
#             self.top_right_frame,
#             text="Connect Power Supply",
#             command=self.connect_power_supply,
#             width=20,
#         )
#         self.connect_psu_button.grid(row=1, column=0, padx=5, pady=5, columnspan=2)

#         # Set Voltage Controls (below Connect Power Supply button)
#         self.voltage_label = tk.Label(self.top_right_frame, text="Set Voltage (V):")
#         self.voltage_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

#         self.voltage_entry = tk.Entry(self.top_right_frame, width=10)
#         self.voltage_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

#         self.set_voltage_button = tk.Button(
#             self.top_right_frame, text="Set Voltage", command=self.set_voltage, width=20
#         )
#         self.set_voltage_button.grid(row=2, column=2, padx=5, pady=5)

#         # PID Control Loop
#         self.pid_frame = tk.Frame(self.top_right_frame)
#         self.pid_frame.grid(
#             row=3, column=0, columnspan=4, padx=10, pady=10, sticky=tk.W
#         )

#         self.channel_label = tk.Label(
#             self.pid_frame, text="Select Channel for Temperature:"
#         )
#         self.channel_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

#         self.channel_var = tk.StringVar(master)
#         self.channel_var.set("None")

#         self.channel_menu = tk.OptionMenu(
#             self.pid_frame,
#             self.channel_var,
#             *[f"CH{ch}" for ch in range(1, self.num_channels + 1)],
#         )
#         self.channel_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

#         self.setpoint_label = tk.Label(self.pid_frame, text="Setpoint Temperature:")
#         self.setpoint_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

#         self.setpoint_entry = tk.Entry(self.pid_frame, width=10)
#         self.setpoint_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

#         default_setpoint = "45.0"  # Set your default value here
#         self.setpoint_entry.insert(0, default_setpoint)

#         self.p_label = tk.Label(self.pid_frame, text="P:")
#         self.p_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

#         self.p_entry = tk.Entry(self.pid_frame, width=10)
#         self.p_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
#         default_p = "5.0"  # Set your value here
#         self.p_entry.insert(0, default_p)

#         self.i_label = tk.Label(self.pid_frame, text="I:")
#         self.i_label.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)

#         self.i_entry = tk.Entry(self.pid_frame, width=10)
#         self.i_entry.grid(row=2, column=4, padx=5, pady=5, sticky=tk.W)
#         default_i = "1.0"  # Set your value here
#         self.i_entry.insert(0, default_i)

#         self.d_label = tk.Label(self.pid_frame, text="D:")
#         self.d_label.grid(row=2, column=5, padx=5, pady=5, sticky=tk.W)

#         self.d_entry = tk.Entry(self.pid_frame, width=10)
#         self.d_entry.grid(row=2, column=6, padx=5, pady=5, sticky=tk.W)
#         default_d = "0"  # Set your value here
#         self.d_entry.insert(0, default_d)

#         self.start_pid_button = tk.Button(
#             self.pid_frame,
#             text="Start PID Control",
#             command=self.start_pid_control,
#             width=20,
#         )
#         self.start_pid_button.grid(row=3, column=0, padx=5, pady=5)

#         self.stop_pid_button = tk.Button(
#             self.pid_frame,
#             text="Stop PID Control",
#             command=self.stop_pid_control,
#             width=20,
#             state=tk.DISABLED,
#         )
#         self.stop_pid_button.grid(row=3, column=1, padx=5, pady=5)

#         # Channel controls (middle right)
#         self.channel_configs = {}
#         self.channel_vars = {}
#         self.channel_checkboxes = {}
#         self.channel_names = {}

#         self.create_channel_controls()

#         # Initialize the matplotlib figure (middle left)
#         self.figure, self.ax = plt.subplots()
#         self.ax.set_title("Measurements Over Time")
#         self.ax.set_xlabel("Time (HH:MM:SS)")
#         self.ax.set_ylabel("Value")

#         # Embed the figure in the Tkinter canvas
#         self.canvas = FigureCanvasTkAgg(self.figure, master=self.middle_left_frame)
#         self.canvas.draw()
#         self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

#         # Save buttons (bottom)
#         self.save_chart_button = tk.Button(
#             self.bottom_frame,
#             text="Save Chart as PNG",
#             command=self.save_chart_as_png,
#             width=20,
#         )
#         self.save_chart_button.grid(row=0, column=0, padx=5, pady=5)

#         self.save_csv_button = tk.Button(
#             self.bottom_frame,
#             text="Save Measurements as CSV",
#             command=self.save_measurements_as_csv,
#             width=20,
#         )
#         self.save_csv_button.grid(row=0, column=1, padx=5, pady=5)

#         self.result_label = tk.Label(self.bottom_frame, text="", width=80)
#         self.result_label.grid(row=0, column=2, columnspan=2, padx=5, pady=5)

#         self.is_measuring = False
#         self.measurements = {channel: [] for channel in range(1, self.num_channels + 1)}
#         self.times = []

#         # PID control variables
#         self.pid_running = False
#         self.setpoint = 0
#         self.kp = 0
#         self.ki = 0
#         self.kd = 0
#         self.previous_error = 0
#         self.integral = 0

#     def update_connect_button_color(self, button):
#         """Change the button color to green to indicate a successful connection."""
#         button.config(bg="green", fg="white")

#     def connect_instrument(self):
#         selected_instrument = self.instrument_var.get()
#         if selected_instrument != "None":
#             try:
#                 self.instrument = self.rm.open_resource(selected_instrument)
#                 idn_response = self.instrument.query("*IDN?")  # Query the IDN string
#                 messagebox.showinfo(
#                     "Connected",
#                     f"Connected to {selected_instrument}\nIDN: {idn_response}",
#                 )
#                 self.update_connect_button_color(
#                     self.connect_button
#                 )  # Update button color
#             except pyvisa.VisaIOError:
#                 messagebox.showerror(
#                     "Connection Error", "Failed to connect to the instrument."
#                 )

#     def connect_power_supply(self):
#         selected_psu = self.psu_var.get()
#         if selected_psu != "None":
#             try:
#                 self.psu = self.rm.open_resource(selected_psu)
#                 idn_response = self.psu.query("*IDN?")  # Query the IDN string
#                 messagebox.showinfo(
#                     "Connected", f"Connected to {selected_psu}\nIDN: {idn_response}"
#                 )
#                 self.update_connect_button_color(
#                     self.connect_psu_button
#                 )  # Update button color
#             except pyvisa.VisaIOError:
#                 messagebox.showerror(
#                     "Connection Error", "Failed to connect to the power supply."
#                 )

#     def set_voltage(self):
#         if hasattr(self, "psu"):
#             try:
#                 voltage = float(self.voltage_entry.get())
#                 # Calculate the voltage for each channel
#                 voltage_positive = voltage / 2
#                 voltage_negative = -voltage / 2

#                 # Set voltage on +25V channel
#                 self.psu.write("INST:SEL P25V")
#                 self.psu.write(f"VOLT:TRIG {voltage_positive}")

#                 # Set voltage on -25V channel
#                 self.psu.write("INST:SEL N25V")
#                 self.psu.write(f"VOLT:TRIG {voltage_negative}")

#                 # Set trigger source to immediate
#                 self.psu.write("TRIG:SOUR IMM")
#                 # Initiate the trigger
#                 self.psu.write("INIT")

#                 messagebox.showinfo(
#                     "Voltage Set",
#                     f"Triggered Voltage set to +{voltage_positive}V and {voltage_negative}V",
#                 )
#             except ValueError:
#                 messagebox.showerror("Invalid Input", "Please enter a valid voltage.")
#         else:
#             messagebox.showwarning("Warning", "No power supply connected.")

#     def start_pid_control(self):
#         self.pid_running = True
#         self.start_pid_button.config(state=tk.DISABLED)
#         self.stop_pid_button.config(state=tk.NORMAL)

#         try:
#             self.setpoint = float(self.setpoint_entry.get())
#             self.kp = float(self.p_entry.get())
#             self.ki = float(self.i_entry.get())
#             self.kd = float(self.d_entry.get())
#         except ValueError:
#             messagebox.showerror("Invalid Input", "Please enter valid PID parameters.")
#             self.stop_pid_control()
#             return

#         # Start the PID control loop in a separate thread or process
#         self.master.after(100, self.pid_control_loop)

#     def stop_pid_control(self):
#         self.pid_running = False
#         self.start_pid_button.config(state=tk.NORMAL)
#         self.stop_pid_button.config(state=tk.DISABLED)

#     def pid_control_loop(self):
#         if self.pid_running:
#             channel = self.channel_var.get()
#             if channel != "None":
#                 try:
#                     if channel == "CH1":
#                         ch = 1
#                     if channel == "CH2":
#                         ch = 2
#                     if channel == "CH3":
#                         ch = 3
#                     temperature = self.measurements[ch][
#                         -1
#                     ]  # get the last value from the selected channel

#                     error = self.setpoint - temperature

#                     self.integral += error * self.interval

#                     if self.ki * self.integral > 10:
#                         self.integral = 10 / self.ki
#                     if self.ki * self.integral < 0:
#                         self.integral = 0

#                     derivative = (error - self.previous_error) / self.interval

#                     p = self.kp * error
#                     i = self.ki * self.integral
#                     d = self.kd * derivative

#                     output = p + i + d

#                     print(
#                         "T: ",
#                         temperature,
#                         "O: ",
#                         output,
#                         "  P: ",
#                         p,
#                         "  I: ",
#                         i,
#                         "  D: ",
#                         d,
#                         "  E: ",
#                         error,
#                     )

#                     # Adjust power supply voltage accordingly
#                     self.set_voltage_from_pid(output)

#                     self.previous_error = error

#                 except ValueError:
#                     messagebox.showerror(
#                         "Measurement Error",
#                         "Failed to read temperature from the selected channel.",
#                     )

#             # Continue the PID loop
#             self.master.after(int(self.interval * 1000), self.pid_control_loop)

#     def set_voltage_from_pid(self, pid_output):
#         """Set voltage to power supply based on PID output."""
#         # Ensure the voltage is within the range of the power supply
#         max_voltage = 25  # or whatever is your maximum voltage
#         min_voltage = 0
#         pid_output = min(pid_output, max_voltage)
#         pid_output = max(pid_output, min_voltage)

#         if hasattr(self, "psu"):
#             try:
#                 voltage_positive = pid_output
#                 voltage_negative = -pid_output

#                 self.psu.write("INST:SEL P25V")
#                 self.psu.write(f"VOLT:TRIG {voltage_positive}")

#                 self.psu.write("INST:SEL N25V")
#                 self.psu.write(f"VOLT:TRIG {voltage_negative}")

#                 self.psu.write("TRIG:SOUR IMM")
#                 self.psu.write("INIT")

#             except pyvisa.VisaIOError:
#                 messagebox.showerror(
#                     "Power Supply Error", "Failed to set voltage on the power supply."
#                 )

#     def create_channel_controls(self):
#         channel_frame = tk.Frame(self.middle_right_frame)
#         channel_frame.pack()

#         for channel in range(
#             1, self.num_channels + 1
#         ):  # Create controls for each channel
#             var = tk.BooleanVar(value=True)
#             checkbox = tk.Checkbutton(channel_frame, text=f"CH{channel}", variable=var)
#             checkbox.grid(row=channel - 1, column=0, padx=5, pady=2, sticky=tk.W)
#             self.channel_vars[channel] = var

#             options = ["Voltage", "Current", "Resistance", "NTC_44006", "NTC_44007"]
#             config_var = tk.StringVar(value="Voltage")
#             config_menu = tk.OptionMenu(channel_frame, config_var, *options)
#             config_menu.grid(row=channel - 1, column=1, padx=5, pady=2, sticky=tk.W)
#             self.channel_configs[channel] = config_var

#             name_entry = tk.Entry(channel_frame, width=20)
#             name_entry.grid(row=channel - 1, column=2, padx=5, pady=2, sticky=tk.W)
#             self.channel_names[channel] = name_entry

#     def configure_channel(self, channel):
#         """Configure a specific channel based on the selected setting."""
#         if self.channel_vars[channel].get():
#             config = self.channel_configs[channel].get()
#             self.instrument.write(
#                 f"ROUT:CLOS (@{channel})"
#             )  # Close the specific channel

#             if config == "Voltage":
#                 self.instrument.write("CONF:VOLT:DC")
#             elif config == "Current":
#                 self.instrument.write("CONF:CURR:DC")
#             elif config == "Resistance":
#                 self.instrument.write("CONF:RES")
#             elif config == "NTC_44006":
#                 self.instrument.write(
#                     "CONF:RES"
#                 )  # Configure for resistance measurement
#                 self.instrument.write(f"ROUT:OPEN:ALL")  # Open all channels
#                 self.instrument.write(
#                     f"ROUT:CLOS (@{channel})"
#                 )  # Close the specific channel
#             elif config == "NTC_44007":
#                 self.instrument.write(
#                     "CONF:RES"
#                 )  # Configure for resistance measurement
#                 self.instrument.write(f"ROUT:OPEN:ALL")  # Open all channels
#                 self.instrument.write(
#                     f"ROUT:CLOS (@{channel})"
#                 )  # Close the specific channel

#     def NTC_44006(self, resistance):
#         """Calculate temperature from NTC thermistor resistance using Steinhart-Hart equation."""
#         A = 1.032e-3
#         B = 2.387e-4
#         C = 1.580e-7
#         log_resistance = math.log(resistance)
#         inv_temp = A + B * log_resistance + C * log_resistance**3
#         temperature_kelvin = 1 / inv_temp
#         temperature_celsius = temperature_kelvin - 273.15
#         return temperature_celsius

#     def NTC_44007(self, resistance):
#         """Calculate temperature from NTC thermistor resistance using Steinhart-Hart equation."""
#         A = 1.285e-3
#         B = 2.362e-4
#         C = 9.285e-8
#         log_resistance = math.log(resistance)
#         inv_temp = A + B * log_resistance + C * log_resistance**3
#         temperature_kelvin = 1 / inv_temp
#         temperature_celsius = temperature_kelvin - 273.15
#         return temperature_celsius

#     def start_measurement(self):
#         if hasattr(self, "instrument"):
#             self.is_measuring = True
#             self.stop_button.config(state=tk.NORMAL)
#             self.measure_button.config(state=tk.DISABLED)
#             self.measure_and_plot()
#         else:
#             messagebox.showwarning("Warning", "No instrument connected.")

#     def stop_measurement(self):
#         self.is_measuring = False
#         self.stop_button.config(state=tk.DISABLED)
#         self.measure_button.config(state=tk.NORMAL)

#     def measure_and_plot(self):
#         start_time = time.time()

#         while self.is_measuring:
#             # Store the full timestamp
#             full_timestamp = datetime.now()
#             self.times.append(full_timestamp)

#             for channel in range(1, self.num_channels + 1):
#                 if self.channel_vars[channel].get():
#                     # Switch to the channel and configure it, then read the measurement
#                     self.instrument.write("ROUT:OPEN:ALL")  # Open all channels first
#                     self.configure_channel(channel)

#                     # Sleep for 0.5 seconds to allow the instrument to stabilize
#                     time.sleep(0.5)

#                     if self.channel_configs[channel].get() == "NTC_44006":
#                         resistance = float(
#                             self.instrument.query("READ?")
#                         )  # Read resistance
#                         measurement = self.NTC_44006(resistance)
#                     elif self.channel_configs[channel].get() == "NTC_44007":
#                         resistance = float(
#                             self.instrument.query("READ?")
#                         )  # Read resistance
#                         measurement = self.NTC_44007(resistance)
#                     else:
#                         measurement = self.instrument.query("READ?")
#                         measurement = float(
#                             "".join(c for c in measurement if c in "0123456789.-eE+")
#                         )  # Clean the response
#                     self.measurements[channel].append(measurement)

#             # Update plot
#             self.ax.clear()
#             for channel, values in self.measurements.items():
#                 if self.channel_vars[channel].get():
#                     # Use the text in the name entry field for the legend
#                     legend_text = self.channel_names[channel].get() or f"CH{channel}"
#                     self.ax.plot(self.times, values, label=legend_text)

#             self.ax.set_title("Measurements Over Time")
#             self.ax.set_xlabel("Time (HH:MM:SS)")
#             self.ax.set_ylabel("Value")
#             self.ax.legend()

#             # Format the x-axis to display HH:MM:SS
#             self.ax.xaxis.set_major_formatter(
#                 FuncFormatter(
#                     lambda x, _: datetime.fromtimestamp(x).strftime("%H:%M:%S")
#                 )
#             )

#             # Redraw the canvas
#             self.canvas.draw()

#             latest_measurements = [
#                 self.measurements[channel][-1] if self.measurements[channel] else None
#                 for channel in range(1, self.num_channels + 1)
#             ]
#             self.result_label.config(text=f"Latest Measurements: {latest_measurements}")

#             # Wait for a specified interval before taking the next measurement
#             self.master.update()
#             time.sleep(self.interval)

#     def clear_chart(self):
#         # Clear measurements and reset plot
#         self.measurements = {channel: [] for channel in range(1, self.num_channels + 1)}
#         self.times = []
#         self.ax.clear()
#         self.ax.set_title("Measurements Over Time")
#         self.ax.set_xlabel("Time (s)")
#         self.ax.set_ylabel("Value")
#         self.ax.legend()
#         self.canvas.draw()

#     def save_chart_as_png(self):
#         """Save the current chart as a PNG file."""
#         file_path = filedialog.asksaveasfilename(
#             defaultextension=".png", filetypes=[("PNG files", "*.png")]
#         )
#         if file_path:
#             self.figure.savefig(file_path)
#             messagebox.showinfo("Saved", f"Chart saved as {file_path}")

#     def save_measurements_as_csv(self):
#         """Save measurements to a CSV file."""
#         file_path = filedialog.asksaveasfilename(
#             defaultextension=".csv", filetypes=[("CSV files", "*.csv")]
#         )
#         if file_path:
#             with open(file_path, mode="w", newline="") as file:
#                 writer = csv.writer(file)
#                 # Write header
#                 header = ["Timestamp"] + [
#                     f"CH{channel}" for channel in range(1, self.num_channels + 1)
#                 ]
#                 writer.writerow(header)

#                 # Find the longest measurement list to determine rows
#                 max_len = max(
#                     len(self.times), max(len(v) for v in self.measurements.values())
#                 )

#                 # Write rows
#                 for i in range(max_len):
#                     row = (
#                         [self.times[i].strftime("%Y-%m-%d %H:%M:%S")]
#                         if i < len(self.times)
#                         else ""
#                     )
#                     row += [
#                         (
#                             self.measurements[channel][i]
#                             if i < len(self.measurements[channel])
#                             else ""
#                         )
#                         for channel in range(1, self.num_channels + 1)
#                     ]
#                     writer.writerow(row)

#             messagebox.showinfo("Saved", f"Measurements saved as {file_path}")


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    # app = KeithleyController(root, num_channels=4, interval=1)
    root.protocol("WM_DELETE_WINDOW", root.quit) # Ensure the application closes properly, when the window is closed
    app = KeithleyGUI(root, num_channels=4, interval=1)
    root.mainloop()
