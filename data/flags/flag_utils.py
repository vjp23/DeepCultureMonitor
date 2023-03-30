import json
import time


def read_flag(flag_path):
	flag_json = json.load(open(flag_path, 'r'))
	return flag_json['flag'], flag_json['at']


def set_flag(flag_path, value):
	json.dump({'flag': value, 'at': time.time()}, open(flag_path, 'w'))
