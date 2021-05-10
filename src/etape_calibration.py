import os
import csv
import time
from math import sqrt
from operator import mul
from datetime import datetime
from devices import WaterHeightSensor


ETAPE_CHANNEL = int(os.environ.get('ETAPE_CHANNEL', 0))
ETAPE_SWITCH_PIN = int(os.environ.get('ETAPE_SWITCH_PIN', 26))


etape = WaterHeightSensor(channel=ETAPE_CHANNEL,
                          mosfet_pin=ETAPE_SWITCH_PIN,
                          slope=1,
                          intercept=0,
                          modality=0)


def measure_v():
    voltage = 0
    for _ in range(10):
        voltage += etape._read_voltage(num_samples=11)
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
