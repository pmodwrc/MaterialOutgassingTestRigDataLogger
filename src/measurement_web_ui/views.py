from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    flash,
)
from .controller import controller, CHANNEL_OPTIONS
from io import BytesIO

views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
def dashboard():
    # Handle form actions
    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "connect":
                device_type = request.form.get("device_type", "Keithley2000")
                address = request.form.get("instrument_address")
                if not address:
                    flash("Please select an instrument address", "error")
                else:
                    idn = controller.connect(device_type, address)
                    flash(f"Connected: {idn}", "success")
            elif action == "start":
                controller.start()
                flash("Measurement started", "success")
            elif action == "stop":
                controller.stop()
                flash("Measurement stopped", "success")
            elif action == "clear":
                controller.clear()
                flash("Cleared", "success")
            elif action == "save_channels":
                controller.set_channels_from_form(request.form)
                flash("Channel settings saved", "success")
            elif action == "load_config_file":
                cfg = request.form.get("config_file")
                if cfg:
                    controller.load_channel_configs(cfg)
                    flash(f"Loaded config {cfg}", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect(url_for("views.dashboard"))

    state = controller.get_state()
    instruments = controller.list_instruments()
    config_files = controller.list_config_files()

    return render_template(
        "dashboard.html",
        state=state,
        instruments=instruments,
        channel_options=CHANNEL_OPTIONS,
        config_files=config_files,
    )


@views.route("/chart.png")
def chart_png():
    data = controller.build_chart_png()
    return send_file(BytesIO(data), mimetype="image/png")


@views.route("/export.csv")
def export_csv():
    data = controller.build_csv()
    return send_file(
        BytesIO(data),
        mimetype="text/csv",
        as_attachment=True,
        download_name="measurements.csv",
    )
