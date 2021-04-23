import csv
import time
from twilio.rest import Client
from flag_utils import read_flag, set_flag


ONE_DAY_IN_SECONDS = 24*60*60


def _get_twilio_creds(cred_file='twilio_creds.csv'):
	with open(cred_file, 'r', newline='') as f:
		reader = csv.reader(f)
		all_values = list(reader)
		sid, token, number = all_values[0]

	return sid, token, number


def _send(msg, to):
	sid, token, from_number = _get_twilio_creds()
	client = Client(sid, token)
	message = client.messages.create(body=msg, from_=from_number, to=to)

	_update_sms_flag()

	return message.sid


def _validate_sms_delay(sms_flag='sms_status.json'):
	now = time.time()
	flag_val, last_set = read_flag(sms_flag)

	if flag_val == 0 or (now - last_set) >= ONE_DAY_IN_SECONDS:
		return True

	return False


def _update_sms_flag(sms_flag='sms_status.json'):
	set_flag(sms_flag, 1)


def reset_sms_status(sms_flag='sms_status.json'):
	set_flag(sms_flag, 0)


def send_sms(msg, to=None, skip_validation=False):
	if skip_validation or _validate_sms_delay():
		return _send(msg, to)

	# If send fails at Twilio level, message.sid is None; indicate failure here with -1
	return -1
