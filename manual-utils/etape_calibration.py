import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from gpiozero import DigitalOutputDevice
import board
import busio
from math import sqrt
from operator import mul
from datetime import datetime
import csv
import time
import os
import statistics

ETAPE_CHANNEL = int(os.environ.get('ETAPE_CHANNEL', 0))
ETAPE_SWITCH_PIN = int(os.environ.get('ETAPE_SWITCH_PIN', 26))


class MOSFETSwitchDevice(object):

    def __init__(self, pin, fail_open=True):
        self.mosfet = DigitalOutputDevice(pin=pin,
                                          active_high=True,
                                          initial_value=False)
        self.fail_open = fail_open

    def __del__(self):
        if self.fail_open:
            self.off()
        else:
            self.on()

    def on(self):
        self.mosfet.on()

    def off(self):
        self.mosfet.off()



class WaterHeightSensor(object):

    def __init__(self, channel, mosfet_pin, slope=1, intercept=0):
        self.voltage = -1
        self.slope = slope
        self.intercept = intercept

        # Use a MOSFET controller to turn the sensor voltage off between readings to avoid zapping the pH sensor
        self.mosfet = MOSFETSwitchDevice(mosfet_pin)

        # Create the I2C bus
        i2c = busio.I2C(board.SCL, board.SDA)
        # Create the ADC object using the I2C bus
        ads = ADS.ADS1015(i2c)
        # Create single-ended input on channel
        input_chan = [ADS.P0, ADS.P1, ADS.P2, ADS.P3][channel]

        self.chan = AnalogIn(ads, input_chan)

    def read_voltage(self, num_samples=21):
        self.mosfet.on()

        time.sleep(0.25)

        samples = []
        for _ in range(num_samples):
            samples.append(self.chan.voltage)
            time.sleep(0.05)

        self.mosfet.off()

        return statistics.median(samples)

    def _voltage_to_gallons(self, voltage):
        return round(max(self.slope * self.voltage + self.intercept, 0), 1)

    def read(self, with_voltage=False):
        voltage = self.read_voltage()
        gallons = self._voltage_to_gallons()

        if with_voltage:
            return gallons, voltage

        return gallons


def measure_v():
    voltage = 0
    for _ in range(10):
        voltage += etape.read_voltage(num_samples=33)
        time.sleep(0.25)
    voltage = voltage / 10
    return voltage


def multiply_elementwise(x, y):
    # Returns the element-wise product of two lists of equal length
    return list(map(mul, x, y))


def square_elements(x):
    # Return a list with its elements squared
    return multiply_elementwise(x, x)


def least_squares_fit(voltages, gallons):
    # Least squares linear regression
    x = voltages
    y = gallons
    x_sq = square_elements(x)
    y_sq = square_elements(y)
    x_times_y = multiply_elementwise(x, y)
    n = len(x)

    # Compute slope and intercept
    b = (sum(x_sq) * sum(y) - sum(x) * sum(x_times_y)) / (n * sum(x_sq) - (sum(x))**2)
    m = (n * sum(x_times_y) - sum(x) * sum(y)) / (n * sum(x_sq) - (sum(x))**2)

    # Compute coefficient of determination
    r_num = n * sum(x_times_y) - sum(x) * sum(y)
    r_denom_sq = (n * sum(x_sq) - sum(x)**2) * (n * sum(y_sq) - sum(y)**2)
    r = r_num / sqrt(r_denom_sq)

    # Compute correlation coefficient
    r_sq = r * r

    return m, b, r_sq


def save_csv(volts, gals):
    local_time = datetime.now()
    csv_filename = local_time.strftime('etape_calibration_data' + '_%Y%m%d_%H%M.csv')

    with open(csv_filename, "w") as infile:
        writer = csv.writer(infile)
        writer.writerow(["Voltage", "Gallons"])    #Write Header
        for i in zip(v, g):
            writer.writerow(i)

    print('Calibration data saved to', csv_filename)



etape = WaterHeightSensor(channel=ETAPE_CHANNEL,
                          mosfet_pin=ETAPE_SWITCH_PIN,
                          slope=1,
                          intercept=0)


start_gallons = input("Enter the number of gallons we're starting with: ")
start_gallons = float(start_gallons)

print('Getting voltage for', start_gallons, 'gallons...')
start_voltage = measure_v()

v_to_g_map = {start_gallons: start_voltage}

print('Done.\n')

now_gallons = start_gallons
continue_input = input("Add water. Enter the number of gallons added and then press Enter. To stop collection, press E: ")

while continue_input != "E":
    now_gallons += float(continue_input)
    print('Getting voltage for', now_gallons, 'gallons...')
    now_voltage = measure_v()
    v_to_g_map[now_gallons] = now_voltage
    print('Done.\n')

    continue_input = input("Add water. Enter the number of gallons added and then press Enter. To stop collection, press E: ")

print('Done collecting data:\n')


v, g = [], []
for gals, volts in v_to_g_map.items():
    v.append(volts)
    g.append(gals)
    print(gals, 'gallons:', volts, 'volts')

print('\n')

print('Computing line of best fit...')

m, b, r_sq = least_squares_fit(v, g)

print('\nSlope:    ', m)
print('Intercept:', b)
print('r^2:      ', r_sq)

save_data = input('\nSave raw data as a CSV file? Enter Y/N: ')
if save_data == 'Y':
    save_csv(v, g)

print('\nDone!')