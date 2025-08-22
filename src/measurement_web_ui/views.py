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
                device_type = request.form.get("device_type") or next(
                    iter(controller.device_types), None
                )
                address = request.form.get("instrument_address")
                if not address:
                    flash("Please select an instrument address", "error")
                else:
                    idn = controller.connect(device_type, address)
                    flash(f"Connected: {idn}", "success")
            elif action == "start":
                try:
                    # capture any posted channel config fields (injected via JS before submit)
                    controller.set_channels_from_form(request.form)
                    controller.start()
                    flash("Measurement started", "success")
                except RuntimeError as re:
                    flash(str(re), "error")
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
    instrument = controller.instrument
    device_types = controller.device_types
    config_files = controller.list_config_files()

    return render_template(
        "dashboard.html",
        state=state,
        instruments=instruments,
        instrument=instrument,
        device_types=device_types,
        channel_options=CHANNEL_OPTIONS,
        config_files=config_files,
        selected_device_type=controller.device_type,
        selected_address=controller.instrument_addr,
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


@views.route("/selection", methods=["POST"])
def selection_changed():
    data = request.get_json(silent=True) or request.form
    new_device_type = data.get("device_type") or controller.device_type
    new_addr = data.get("instrument_address") or controller.instrument_addr
    if (
        new_device_type != controller.device_type
        or new_addr != controller.instrument_addr
    ):
        # Close current instrument and update selection
        controller.close()
        controller.device_type = new_device_type
        controller.instrument_addr = new_addr
    return ("", 204)
