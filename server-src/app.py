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
from flags.flag_utils import set_flag

app = Flask(__name__)

DB = DeviceDatabaseHandler(parms.DB_NAME)
logging.basicConfig(format='%(asctime)s %(message)s', filename=parms.LOG_FILENAME, level=logging.INFO)


def _read_all_sensor_data(hours=24):
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
                                           timezone='"' + parms.TIME_ZONE + '"')


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


@app.route("/fill_tank")
def fill_tank():
    try:
        logging.info('Fill tank request receieved.')
        set_flag(parms.FILL_FLAG_PATH, 1)
        logging.info('Fill flag set to 1.')
        success = True
        message = 'Fill flag set successfully.'

    except Exception as e:
        success = False
        message = e

    return jsonify({'success': success, 'message': message})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3141)))
