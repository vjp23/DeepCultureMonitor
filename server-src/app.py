import os
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from flag_utils import set_flag
from db_utils import DWCServerDatabaseHandler


app = Flask(__name__)

DB = DWCServerDatabaseHandler(os.environ['DB_NAME'])
FILL_FLAG = os.environ['FILL_FLAG_PATH']


@app.route("/")
def index():
    print('Get data from DB...')
    db_values = DB.read_latest()

    print(f'Got {db_values[0]} gallons, {round(db_values[3], 1)} degrees F, {db_values[1]} pH, {db_values[2]} PPM.')
    print('Rendering HTML template...')

    return render_template('metrics.html', gallons=db_values[0], 
                                           temp=round(db_values[3],1), 
                                           ph=db_values[1],
                                           ppm=int(db_values[2]))


@app.route("/modality_names")
def introduce():
    modality_map = DB.get_modality_map()

    return jsonify(modality_map)


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

    modalities = tuple(int(m) for m in request_data.get('modalities', (0, 1, 2, 3)))

    since = datetime.now() - timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    print(f'Reading data for {days} days, {hours} hours, {minutes} minutes, {seconds} seconds for modalities {modalities}...')
    data = DB.read_since(since=since.timestamp(), modalities=modalities)

    print('Returning data...')
    return jsonify(data)


@app.route("/sms_data")
def sms():
    print('Responding to SMS...')

    db_values = DB.read_latest()

    db_dict = {'gallons': db_values[0], 'temp': db_values[3], 'ph': db_values[1], 'ppm': int(db_values[2])}

    print(f'Sending {db_dict} in response to SMS request...')

    return jsonify(db_dict)


@app.route("/fill_tank")
def fill_tank():
    try:
        print('Fill tank request receieved.')
        set_flag(FILL_FLAG, 1)
        print('Fill flag set to 1.')
        success = True
        message = 'Fill flag set successfully.'

    except Exception as e:
        success = False
        message = e

    return jsonify({'success': success, 'message': message})


if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3141)))
    finally:
        if DB:
            DB.close()
