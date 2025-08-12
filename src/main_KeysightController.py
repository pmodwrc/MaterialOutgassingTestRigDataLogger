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


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    # app = KeithleyController(root, num_channels=4, interval=1)
    root.protocol(
        "WM_DELETE_WINDOW", root.quit
    )  # Ensure the application closes properly, when the window is closed
    app = KeithleyGUI(root, num_channels=10, interval=1)
    root.mainloop()
