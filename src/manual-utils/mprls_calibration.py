import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))from math import sqrt
from devices import MPRLSSensor
from operator import mul
from datetime import datetime
import csv
import time
import statistics


SAMPLES_PER_TRIAL = 7
TRIALS_PER_READING = 5
sensor = MPRLSSensor(slope=1, intercept=0)


def multiply_elementwise(x, y):
    # Returns the element-wise product of two lists of equal length
    return list(map(mul, x, y))


def square_elements(x):
    # Return a list with its elements squared
    return multiply_elementwise(x, x)


def least_squares_fit(pressures, gallons):
    # Least squares linear regression
    x = pressures
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


def save_csv(pressures, gallons):
    local_time = datetime.now()
    csv_filename = local_time.strftime('mprls_calibration_data' + '_%Y%m%d_%H%M.csv')

    with open(csv_filename, "w") as infile:
        writer = csv.writer(infile)
        writer.writerow(["Pressure (hPA)", "Gallons"])    #Write Header
        for i in zip(pressures, gallons):
            writer.writerow(i)

    print('Calibration data saved to', csv_filename)

start_gallons = input("Enter the number of gallons we're starting with: ")
start_gallons = float(start_gallons)

print('Getting pressure for', start_gallons, 'gallons...')
start_pressure = sensor.read_pressure(num_samples=SAMPLES_PER_TRIAL, num_trials=TRIALS_PER_READING)

p_to_g_map = {start_gallons: start_pressure}

print('Done.\n')

now_gallons = start_gallons
continue_input = input("Add water. Enter the number of gallons added and then press Enter. To stop collection, press E: ")

while continue_input != "E":
    now_gallons += float(continue_input)
    print('Getting pressure for', now_gallons, 'gallons...')
    now_pressure = sensor.read_pressure(num_samples=SAMPLES_PER_TRIAL, num_trials=TRIALS_PER_READING)
    p_to_g_map[now_gallons] = now_pressure
    print('Done.\n')

    continue_input = input("Add water. Enter the number of gallons added and then press Enter. To stop collection, press E: ")

print('Done collecting data:\n')


p, g = [], []
for gallons, pressure in p_to_g_map.items():
    p.append(pressure)
    g.append(gallons)
    print(gals, 'gallons:', volts, 'hPA')

print('\n')

print('Computing line of best fit...')

m, b, r_sq = least_squares_fit(p, g)

print('\nSlope:    ', m)
print('Intercept:', b)
print('r^2:      ', r_sq)

save_data = input('\nSave raw data as a CSV file? Enter Y/N: ')
if save_data.lower().strip() == 'y':
    save_csv(p, g)

print('\nDone!')
