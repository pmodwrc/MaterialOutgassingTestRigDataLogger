from flask import Flask, render_template, request, jsonify
import pyvisa
from datetime import datetime
import time

app = Flask(__name__)

# Initialize PyVISA resource manager
rm = pyvisa.ResourceManager()
instruments = rm.list_resources()
selected_instrument = None


@app.route("/")
def index():
    return render_template("index.html", instruments=instruments)


@app.route("/connect", methods=["POST"])
def connect_instrument():
    global selected_instrument
    instrument_address = request.form["instrument"]
    try:
        selected_instrument = rm.open_resource(instrument_address)
        selected_instrument.write("*IDN?")
        return jsonify(
            {"status": "success", "message": f"Connected to {instrument_address}"}
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/measure", methods=["POST"])
def measure():
    global selected_instrument
    if not selected_instrument:
        return jsonify({"status": "error", "message": "No instrument connected."})

    try:
        channel = request.form["channel"]
        selected_instrument.write(f"MEAS:VOLT:DC? (@{channel})")
        measurement = selected_instrument.read()
        return jsonify({"status": "success", "measurement": measurement})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/save", methods=["POST"])
def save_measurements():
    data = request.json
    filename = f"measurements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    try:
        with open(filename, "w") as f:
            f.write("Channel,Measurement\n")
            for channel, measurement in data.items():
                f.write(f"{channel},{measurement}\n")
        return jsonify({"status": "success", "message": f"Saved to {filename}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
