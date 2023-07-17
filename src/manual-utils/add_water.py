import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
from devices import SolenoidDevice
import argparse
import time

parser = argparse.ArgumentParser(description="Manually pump some water.",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-t", "--seconds", default=5, help="Number of seconds to run the pump for.")
parser.add_argument("-p", "--solenoid", default=21, help="Solenoid pin number.")

args = parser.parse_args()
config = vars(args)

sol = SolenoidDevice(pin=int(config['solenoid']))

try:
    print('Open solenoid...')
    sol.open()
    print(f"Solenoid open. Sleep for {config['seconds']} seconds...")
    time.sleep(float(config['seconds']))
finally:
    print('Closing solenoid...')
    sol.close()
    print('Solenoid closed.')
