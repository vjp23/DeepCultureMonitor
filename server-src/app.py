from database import DeviceDatabaseHandler, TIME_FMT
import utils
from flask import Flask, render_template, jsonify, request, url_for
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import requests
import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')))
from db.database import DeviceDatabaseHandler

app = Flask(__name__)

DB = DeviceDatabaseHandler(os.environ['DB_NAME'])
FILL_FLAG = os.environ['FILL_FLAG_PATH']

TIME_ZONE = "America/New_York"
PLOT_TIME_FMT = "%-H:%M"


def _read_all_sensor_data(hours=12):
    all_raw = DB.read_all_since(since=datetime.now(ZoneInfo(TIME_ZONE)) - timedelta(hours=hours))
    data_dict = utils.unpack_all(all_raw, TIME_FMT, PLOT_TIME_FMT)
    return data_dict


@app.route("/")
def index():
    print('Get data from DB...')
    latest_values_packed = DB.read_all_latest()
    latest_values = utils.unpack_latest(latest_values_packed)

    plot_values = _read_all_sensor_data()

    print('Rendering HTML template...')

    return render_template('metrics.html', gallons=latest_values.get('water_gallons', {'value': -1}).get('value', -1),
                                           temp=latest_values.get('water_temp_f', {'value': -1}).get('value', -1),
                                           ph=latest_values.get('ph', {'value': -1}).get('value', -1),
                                           ppm=int(latest_values.get('ec', {'value': -1}).get('value', -1)),
                                           ph_times=plot_values['ph']['time'],
                                           ph_values=plot_values['ph']['value'],
                                           ec_times=plot_values['ec']['time'],
                                           ec_values=plot_values['ec']['value'],
                                           temp_times=plot_values['water_temp_f']['time'],
                                           temp_values=plot_values['water_temp_f']['value'],
                                           level_times=plot_values['water_gallons']['time'],
                                           level_values=plot_values['water_gallons']['value'])


@app.route("/api_data", methods=['POST', 'GET'])
def api():
    print('Responding to API data request...')

    request_data = request.get_json() or dict()

    days = request_data.get('days', 0)
    hours = request_data.get('hours', 0)
    minutes = request_data.get('minutes', 0)
    seconds = request_data.get('seconds', 0)

    if days + hours + minutes + seconds == 0:
        days = 1

    since = datetime.now() - timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    print(f'Reading data for {days} days, {hours} hours, {minutes} minutes, {seconds} seconds for modalities {modalities}...')
    data = DB.read_since(since=since.timestamp(), modalities=modalities)

    print('Returning data...')
    return jsonify(data)


@app.route("/fill_tank")
def fill_tank():
    try:
        print('Fill tank request receieved.')
        utils.set_flag(FILL_FLAG, 1)
        print('Fill flag set to 1.')
        success = True
        message = 'Fill flag set successfully.'

    except Exception as e:
        success = False
        message = e

    return jsonify({'success': success, 'message': message})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3141)))
