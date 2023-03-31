from collections import defaultdict
from zoneinfo import ZoneInfo
from datetime import datetime
import time


def unpack_latest(latest_values):
	data = dict()
	for (write_time, device_name, value) in latest_values:
		data[device_name] = {'time': write_time, 'value': value}
	return data


def unpack_all(all_values, from_fmt=None, to_fmt=None, from_tz=None, as_json=True):
	data = defaultdict(lambda: defaultdict(list))
	if from_fmt:
		# Either two formats supplied or just from_fmt supplied
		for (write_time, device_name, value) in all_values:
			data[device_name]['time'].append(fmt_timestamp(write_time, from_fmt, to_fmt, from_tz))
			data[device_name]['value'].append(value)	
	else:
		# No formats supplied, don't convert times
		for (write_time, device_name, value) in all_values:
			data[device_name]['time'].append(write_time)
			data[device_name]['value'].append(value)
	if as_json:
		return repack_to_json(data)
	return data


def fmt_timestamp(timestamp, from_fmt, to_fmt, from_tz=None):
	if to_fmt is None:
		# Only from_fmt supplied (return UNIX ms since epoch timestamp)
		return int(1000 * datetime.strptime(timestamp, from_fmt).timestamp())
	if to_fmt.lower() == "iso":
		from_tz = from_tz or "US/Eastern"
		return to_utc_string(timestamp, from_fmt, from_tz)
	return datetime.strptime(timestamp, from_fmt).strftime(to_fmt)


def repack_to_json(data):
	data_json = dict()
	for device in data:
		device_strs = []
		for write_time, value in zip(data[device]['time'], data[device]['value']):
			device_strs.append("{" + f'"x": "{write_time}", "y": {value}' + "}")
		data_json[device] = "[" + ",".join(device_strs) + "]"
	return data_json


def to_utc_string(timestamp, from_fmt, from_tz):
	write_time_obj = datetime.strptime(timestamp, from_fmt)
	iso_fmt = "%Y-%m-%dT%H:%M:%SZ"
	offset = write_time_obj.astimezone(ZoneInfo(from_tz)).utcoffset()
	return (write_time_obj - offset).strftime(iso_fmt)
