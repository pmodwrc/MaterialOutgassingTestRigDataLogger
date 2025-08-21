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
from measurement_ui import KeithleyCustomTkinterGUI
import multiprocessing
from measurement_web_ui import create_app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(debug=True)

    # root = tk.Tk()
    # root.protocol(
    #     "WM_DELETE_WINDOW", root.quit
    # )  # Ensure the application closes properly, when the window is closed
    # app = KeithleyCustomTkinterGUI(root)
    # root.mainloop()
    # app.stop_measurement()