import utils
import parameters as parms
from flask import Flask, render_template, jsonify, request, url_for
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import requests
import logging
import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')))
from db.database import DeviceDatabaseHandler, TIME_FMT
from flags.flag_utils import read_flag, set_flag

app = Flask(__name__)

DB = DeviceDatabaseHandler(parms.DB_NAME)
logging.basicConfig(format='%(asctime)s %(message)s', filename=parms.LOG_FILENAME, level=logging.INFO)


def _read_all_sensor_data(hours=48):
    all_raw = DB.read_all_since(since=datetime.now(ZoneInfo(parms.TIME_ZONE)) - timedelta(hours=hours))
    data_dict = utils.unpack_all(all_values=all_raw,
                                 from_fmt=TIME_FMT,
                                 to_fmt="ISO",
                                 from_tz=parms.TIME_ZONE,
                                 as_json=True)
    return data_dict


@app.route("/")
def index():
    logging.info('Get data from DB...')
    latest_values_packed = DB.read_all_latest()
    latest_values = utils.unpack_latest(latest_values_packed)

    plot_values = _read_all_sensor_data()

    logging.info('Rendering HTML template...')

    return render_template('metrics.html', gallons=latest_values.get('water_gallons', {'value': -1}).get('value', -1),
                                           temp=latest_values.get('water_temp_f', {'value': -1}).get('value', -1),
                                           ph=latest_values.get('ph', {'value': -1}).get('value', -1),
                                           ppm=int(latest_values.get('ec', {'value': -1}).get('value', -1)),
                                           ph_data=plot_values['ph'],
                                           ec_data=plot_values['ec'],
                                           temp_data=plot_values['water_temp_f'],
                                           level_data=plot_values['water_gallons'],
                                           timezone='"' + parms.TIME_ZONE + '"',
                                           post_endpoint=url_for("device_request"))


@app.route("/api_data", methods=['POST', 'GET'])
def api():
    logging.info('Responding to API data request...')

    request_data = request.get_json() or dict()

    days = request_data.get('days', 0)
    hours = request_data.get('hours', 0)
    minutes = request_data.get('minutes', 0)
    seconds = request_data.get('seconds', 0)

    if days + hours + minutes + seconds == 0:
        days = 1

    since = datetime.now() - timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    logging.info(f'Reading data for {days} days, {hours} hours, {minutes} minutes, {seconds} seconds for modalities {modalities}...')
    data = DB.read_since(since=since.timestamp(), modalities=modalities)

    logging.info('Returning data...')
    return jsonify(data)


@app.route("/make_request", methods=['POST', 'GET'])
def device_request():
    """
    Flag JSON/dict format:
    {device_name: {"status": status, "action": action, "value": value}, ...}

    Valid device names:
        - "ph"
        - "ec"
        - "level"

    Valid status values:
        - "request": Web server sets this value when requesting an action
        - "fulfilling": Device server sets this value when taking the action
        - "fulfilled": Device server sets this value when finished the action
        - "failed": Device server sets this value when the action fails

    Valid action names:
        - "ph" device
            + "up" to dispense "value" ml of ph up 
            + "down" to dispense "value" ml of ph down
        - "ec" device
            + "nute1" to dispense "value" ml of nutrient 1 (pump3)
            + "nute2" to dispense "value" ml of nutrient 2 (pump4)
            + "nute3" to dispense "value" ml of nutrient 3 (pump5)
            + "nute4" to dispense "value" ml of nutrient 4 (pump6)
        - "level" device
            + "set" to fill/drain to "set" gallons
            + "fill" to add "value" gallons
            + "drain" to drain out "value" gallons
    """
    request_data = request.get_json() or dict()
    flag, _ = read_flag(parms.FLAG_PATH)

    for flag_name in request_data:
        flag[flag_name]["status"] = "request"
        flag[flag_name]["action"] = request_data[flag_name]["action"]
        flag[flag_name]["value"] = request_data[flag_name]["value"]

    try:
        set_flag(parms.FLAG_PATH, flag)
        success = True
        message = 'Request flag set successfully.'

    except Exception as e:
        success = False
        message = e

    return jsonify({'success': success, 'message': message})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3141)))
