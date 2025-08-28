import threading
import time
import csv
from datetime import datetime
from io import BytesIO, StringIO
from typing import Dict, List, Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

import pyvisa

# Local instrument drivers
from Keithley2000 import Keithley2000
from keyseight_DAC970A import KeysightDAQ970A
import os


CHANNEL_OPTIONS = [
    "Voltage",
    "Current",
    "Resistance",
    "NTC_44006",
    "NTC_44007",
    "PT100",
    "Frequency",
    "IKR020",
]


class MeasurementController:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.instrument = None
        self.instrument_addr: Optional[str] = None
        self.device_type: str = ""
        self.device_types: List[str] = ["Keithley2000", "KeysightDAQ970A"]

        self.config_file: str = "channel_configs_default.csv"
        self.config_file_path: str = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", self.config_file
        )
        self.number_of_channels: int = 20
        self.channel_active: Dict[int, bool] = {}
        self.channel_config: Dict[int, str] = {}
        self.channel_name: Dict[int, str] = {}

        self.interval: float = 1.0
        self.is_measuring: bool = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        self.times: List[datetime] = []
        self.measurements: Dict[int, List[float]] = {
            i: [] for i in range(1, self.number_of_channels + 1)
        }

        # initialize channel configs
        self.load_channel_configs(self.config_file)

    def list_instruments(self) -> List[str]:
        try:
            return list(self.rm.list_resources())
        except Exception:
            return []

    def connect(self, device_type: str, address: str) -> str:
        self.device_type = device_type
        self.instrument_addr = address
        self.close()
        inst = self.rm.open_resource(address)
        idn = inst.query("*IDN?")
        if device_type == "Keithley2000":
            self.instrument = Keithley2000(inst)
        elif device_type == "KeysightDAQ970A":
            self.instrument = KeysightDAQ970A(inst)
        else:
            return "unknown"
        # 10s timeout
        self.instrument.timeout = 10000
        # Initialize
        self.instrument.init()
        return idn

    def close(self):
        try:
            if self.instrument:
                self.instrument.close()
        except Exception:
            pass
        self.instrument = None

    def load_channel_configs(self, config_file: str):
        """Load channel configuration from a CSV.

        Expected columns: channel_nr, configuration, active, (optional) name
        Active is interpreted case-insensitively: true/false, 1/0, yes/no, on/off.
        Gaps in channel numbering are filled with default inactive entries so that
        UI renders a contiguous block from 1..max_channel.
        """
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(src_dir, config_file)
        self.config_file = config_file
        self.config_file_path = path

        # Temporary storage
        ch_active: Dict[int, bool] = {}
        ch_config: Dict[int, str] = {}
        ch_name: Dict[int, str] = {}

        if os.path.exists(path):
            with open(path, mode="r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        raw_ch = row.get("channel_nr")
                        if raw_ch is None or raw_ch == "":
                            continue
                        ch = int(raw_ch)
                        raw_active = str(row.get("active", "False")).strip().lower()
                        active_bool = raw_active in ("true", "1", "yes", "y", "on")
                        ch_active[ch] = active_bool
                        ch_config[ch] = row.get("configuration", "None") or "None"
                        ch_name[ch] = row.get("name", f"CH{ch}") or f"CH{ch}"
                    except Exception:
                        continue
        # Determine max channel even if there are gaps
        if ch_active:
            max_ch = max(ch_active.keys())
            self.number_of_channels = max_ch
        # Fill / update internal dicts contiguously 1..number_of_channels
        for i in range(1, self.number_of_channels + 1):
            self.channel_active[i] = ch_active.get(i, False)
            self.channel_config[i] = ch_config.get(
                i, self.channel_config.get(i, "None")
            )
            self.channel_name[i] = ch_name.get(i, self.channel_name.get(i, f"CH{i}"))
        # Resize measurements dict preserving existing collected data
        for i in range(1, self.number_of_channels + 1):
            if i not in self.measurements:
                self.measurements[i] = []
        # Drop measurements for channels beyond new max (unlikely shrinking case)
        for ch in list(self.measurements.keys()):
            if ch > self.number_of_channels:
                del self.measurements[ch]

    def set_channels_from_form(self, form: dict):
        for i in range(1, self.number_of_channels + 1):
            self.channel_active[i] = form.get(f"channel_{i}") is not None
            self.channel_config[i] = form.get(
                f"config_{i}", self.channel_config.get(i, "None")
            )
            self.channel_name[i] = form.get(
                f"name_{i}", self.channel_name.get(i, f"CH{i}")
            )

    def list_config_files(self) -> List[str]:
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        files = [
            f
            for f in os.listdir(src_dir)
            if f.startswith("channel_configs") and f.endswith(".csv")
        ]
        return sorted(files)

    def has_active_channels(self) -> bool:
        return any(
            self.channel_active.get(i) for i in range(1, self.number_of_channels + 1)
        )

    def start(self):
        if self.is_measuring:
            return
        if not self.instrument:
            raise RuntimeError("No instrument connected")
        if not self.has_active_channels():
            raise RuntimeError("No active channels selected")
        self.is_measuring = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.is_measuring = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.1)

    def clear(self):
        with self._lock:
            self.times = []
            self.measurements = {i: [] for i in range(1, self.number_of_channels + 1)}

    def _run_loop(self):
        while self.is_measuring:
            try:
                ts = datetime.now()
                with self._lock:
                    self.times.append(ts)
                for ch in range(1, self.number_of_channels + 1):
                    if self.channel_active.get(ch):
                        config = self.channel_config.get(ch, "None")
                        try:
                            val = self.instrument.measureChannel(config, ch, 10, 5)
                        except Exception:
                            val = None
                        if val is None:
                            val = 0.0
                        with self._lock:
                            self.measurements[ch].append(val)
                time.sleep(self.interval)
            except Exception:
                time.sleep(self.interval)

    def get_state(self) -> dict:
        with self._lock:
            latest = {
                ch: (vals[-1] if vals else None)
                for ch, vals in self.measurements.items()
            }
            times = [t.strftime("%H:%M:%S") for t in self.times]
            return {
                "is_measuring": self.is_measuring,
                "times": times,
                "latest": latest,
                "channel_active": self.channel_active,
                "channel_config": self.channel_config,
                "channel_name": self.channel_name,
                "number_of_channels": self.number_of_channels,
                "has_active": any(
                    self.channel_active.get(i)
                    for i in range(1, self.number_of_channels + 1)
                ),
            }

    def build_chart_png(self) -> bytes:
        fig, ax = plt.subplots(figsize=(8, 4))
        with self._lock:
            # convert times to timestamps
            if self.times:
                t0 = self.times[0]
                xt = [(t - t0).total_seconds() for t in self.times]
            else:
                xt = []
            for ch in range(1, self.number_of_channels + 1):
                if self.channel_active.get(ch) and len(self.measurements.get(ch, [])):
                    ys = self.measurements[ch]
                    xplot = xt[: len(ys)]
                    ax.plot(xplot, ys, label=f"CH{ch}")
        ax.set_title("Measurements Over Time")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Value")
        ax.legend(loc="best")
        buf = BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        return buf.read()

    def build_csv(self) -> bytes:
        with self._lock:
            output = StringIO()
            writer = csv.writer(output)
            header = ["Timestamp"] + [
                f"CH{i}" for i in range(1, self.number_of_channels + 1)
            ]
            writer.writerow(header)
            max_len = max(
                [len(self.times)] + [len(v) for v in self.measurements.values()] or [0]
            )
            for i in range(max_len):
                ts = (
                    self.times[i].strftime("%Y-%m-%d %H:%M:%S")
                    if i < len(self.times)
                    else ""
                )
                row = [ts]
                for ch in range(1, self.number_of_channels + 1):
                    vals = self.measurements.get(ch, [])
                    row.append(vals[i] if i < len(vals) else "")
                writer.writerow(row)
            data = output.getvalue().encode("utf-8")
        return data

    def get_series(self, max_points: int = 500) -> dict:
        with self._lock:
            # Trim to last max_points for efficiency
            if len(self.times) > max_points:
                times = self.times[-max_points:]
            else:
                times = list(self.times)
            series = {}
            for ch in range(1, self.number_of_channels + 1):
                if self.channel_active.get(ch):
                    vals = self.measurements.get(ch, [])
                    if len(vals) > max_points:
                        vals = vals[-max_points:]
                    series[ch] = vals
            return {
                "times": [t.isoformat() for t in times],
                "series": series,
                "names": {
                    ch: self.channel_name.get(ch, f"CH{ch}") for ch in series.keys()
                },
                "running": self.is_measuring,
            }


# Singleton controller for the app
controller = MeasurementController()
