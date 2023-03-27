from collections import defaultdict
from datetime import datetime
import time
import json


def read_flag(flag_path):
	flag_json = json.load(open(flag_path, 'r'))

	return flag_json['flag'], flag_json['at']


def set_flag(flag_path, value):
	json.dump({'flag': value, 'at': time.time()}, open(flag_path, 'w'))


def unpack_latest(latest_values):
	data = dict()
	for (write_time, device_name, value) in latest_values:
		data[device_name] = {'time': write_time, 'value': value}

	return data


def unpack_all(all_values, from_format=None, to_format=None):
	data = defaultdict(lambda: defaultdict(list))
	if from_format and to_format:
		for (write_time, device_name, value) in all_values:
			data[device_name]['time'].append(fmt_timestamp(write_time, from_format, to_format))
			data[device_name]['value'].append(value)
	else:
		for (write_time, device_name, value) in all_values:
			data[device_name]['time'].append(write_time)
			data[device_name]['value'].append(value)
	return data


def fmt_timestamp(timestamp, from_format, to_format):
	return datetime.strptime(timestamp, from_format).strftime(to_format)
