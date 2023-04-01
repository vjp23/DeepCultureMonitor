import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from atlas_i2c import sensors, commands
from w1thermsensor import W1ThermSensor, Unit
from gpiozero import DigitalOutputDevice, Motor, DeviceClosed
import board
import busio
import statistics
import time
import sys
import os


class SolenoidDevice:
    def __init__(self, pin, fail_open=True):
        # By "fail open," we refer to the state of the circuit, not the solenoid
        self.output = MOSFETSwitchDevice(pin=pin, fail_open=fail_open)

    def open(self):
        self.output.on()

    def close(self):
        self.output.off()


class MOSFETSwitchDevice:
    def __init__(self, pin, fail_open=True):
        self.mosfet = DigitalOutputDevice(pin=pin,
                                          active_high=True,
                                          initial_value=False)
        self.fail_open = fail_open

    def __del__(self):
        try:
            if self.fail_open:
                self.off()
            else:
                self.on()
        except DeviceClosed:
            pass

    def on(self):
        self.mosfet.on()

    def off(self):
        self.mosfet.off()


class PeristalticPumpDevice:
    def __init__(self, forward_pin, backward_pin, speed=0.5, mL_per_min=100):
        self.pump = Motor(forward_pin, backward_pin)
        self.speed = speed
        self.rate = mL_per_min / 60

    def __del__(self):
        try:
            self.pump.stop()
        except DeviceClosed:
            pass

    def prime(self, prime_time=10):
        self.run(run_time=prime_time)

    def empty(self, empty_time=10):
        self.run(run_time=empty_time, reverse=True)

    def dispense(self, mL):
        run_time = mL / self.rate
        self.run(run_time=run_time)

    def run(self, run_time, reverse=False):
        try:
            if reverse:
                self.pump.backward(self.speed)
            else:
                self.pump.forward(self.speed)
            time.sleep(run_time)
        finally:
            self.pump.stop()


class AtlasSensor:
    # Interfaces with Atlas Scientific device i2c library
    def __init__(self, name: str, address: int, max_attempts: int = 3):
        self.sensor = self._setup(name, address)
        self.name = name
        self.max_attempts = max_attempts

    def _setup(self, name, address):
        sensor = sensors.Sensor(name, address)
        sensor.connect()
        return sensor

    def read(self, attempts=0):
        if attempts < self.max_attempts:
            # Retry with linear backoff
            time.sleep(attempts + 1)
            try:
                response = self.sensor.query(commands.READ)
                return response.data.decode("ascii")

            except Exception as e:
                return self.read(attempts=attempts+1)

        raise SystemError(f'There is a problem communicating with the {self.name} sensor. {attempts} attempts failed.')


class WaterHeightSensor:
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

    def read_voltage(self, num_samples=75):
        self.mosfet.on()

        time.sleep(0.25)

        samples = []
        for _ in range(num_samples):
            samples.append(self.chan.voltage)
            time.sleep(0.0025)

        self.mosfet.off()

        return statistics.median(samples)

    def _voltage_to_gallons(self, voltage):
        return round(max(self.slope * voltage + self.intercept, 0), 1)

    def read(self, with_voltage=False):
        voltage = self.read_voltage()
        gallons = self._voltage_to_gallons(voltage)

        if with_voltage:
            return gallons, voltage

        return gallons


class TempSensor:
    def __init__(self):
        self.sensor = W1ThermSensor()

    def read(self, decimals=1):
        temp = self.sensor.get_temperature(Unit.DEGREES_F)

        return round(temp, decimals)
