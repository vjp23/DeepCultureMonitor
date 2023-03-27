# usage: python3 get_data.py [-h] [-n HOURS] [-d DEVICE]

from src.database import DeviceDatabaseHandler
import argparse
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

DB = DeviceDatabaseHandler("data/db/device_data.db")
TIME_ZONE = "America/New_York"

parser = argparse.ArgumentParser(description="Get latest data from the device database.",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-n", "--hours", default=0.5, help="Number of hours of data to retrieve")
parser.add_argument("-d", "--device", default=None, help="Name of device to get, ignore to get all devices. Available options: ph, ec, water_gallons, water_height_volts, water_temp_f")

args = parser.parse_args()
config = vars(args)

start_time = datetime.now(ZoneInfo(TIME_ZONE)) - timedelta(hours=float(config['hours']))

if config['device'] is None:
    data = DB.read_all_since(since=start_time)
else:
    data = DB.read_device_since(device_name=config['device'], since=start_time)

print('Time'.ljust(27) + ' ' + 'Device'.ljust(20) + ' ' + 'Value')
print("===================================================================")
for (write_time, device_name, value) in data:
    print(write_time.ljust(27) + ' ' + device_name.ljust(20) + ' ' + str(value))