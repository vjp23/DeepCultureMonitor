from collections import defaultdict
from datetime import datetime
import time


def unpack_latest(latest_values):
	data = dict()
	for (write_time, device_name, value) in latest_values:
		data[device_name] = {'time': write_time, 'value': value}

	return data


def unpack_all(all_values, from_format=None, to_format=None, as_json_str=True):
	data = defaultdict(lambda: defaultdict(list))
	if from_format:
		# Either two formats supplied or just from_format supplied
		for (write_time, device_name, value) in all_values:
			data[device_name]['time'].append(fmt_timestamp(write_time, from_format, to_format))
			data[device_name]['value'].append(value)	
	else:
		# No formats supplied, don't convert times
		for (write_time, device_name, value) in all_values:
			data[device_name]['time'].append(write_time)
			data[device_name]['value'].append(value)
	if as_json_str:
		return convert_to_json_strs(data)
	return data


def fmt_timestamp(timestamp, from_format, to_format):
	if to_format is None:
		# Only from_format supplied (return UNIX ms since epoch timestamp)
		return int(1000 * datetime.strptime(timestamp, from_format).timestamp())
	return datetime.strptime(timestamp, from_format).strftime(to_format)


def convert_to_json_strs(data):
	data_json = dict()
	for device in data:
		device_strs = []
		for write_time, value in zip(data[device]['time'], data[device]['value']):
			device_strs.append("{" + f'"x": {write_time}, "y": {value}' + "}")
		data_json[device] = "[" + ",".join(device_strs) + "]"
	return data_json
