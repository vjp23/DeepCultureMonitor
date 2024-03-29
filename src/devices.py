import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_mprls as mprls
from atlas_i2c import sensors, commands
from w1thermsensor import W1ThermSensor, Unit
from gpiozero import DigitalOutputDevice, DeviceClosed
from qwiic_relay import QwiicRelay
import board
import busio
import statistics
import time
import sys
import os


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


class SolenoidDevice:
    def __init__(self, pin, fail_open=True):
        # By "fail open," we refer to the state of the circuit, not the solenoid
        self.output = MOSFETSwitchDevice(pin=pin, fail_open=fail_open)

    def open(self):
        self.output.on()

    def close(self):
        self.output.off()


class MultichannelSolidStateRelayDevice:
    def __init__(self, address=0x08, channels=4, fail_open=True):
        # Wrapper class for the Qwiic relays from SparkFun
        self.relays = QwiicRelay(address)
        self.available = self.relays.begin()
        self.state = [False] * channels
        self.fail_open = fail_open

    def __del__(self):
        try:
            if self.fail_open:
                self.relays.set_all_relays_off()
            else:
                self.set_all_relays_on()
        except OSError:
            # Device not connected
            pass

    def status(self, channel):
        return self.state[channel]

    def on(self, channel):
        self.relays.set_relay_on(channel + 1)

    def off(self, channel):
        self.relays.set_relay_off(channel + 1)

    def all_off(self):
            self.relays.set_all_relays_off()


class PeristalticPumpDevice:
    def __init__(self, pin, ml_per_min=59.4075):
        self.pump = MOSFETSwitchDevice(pin, fail_open=True)
        self.rate = ml_per_min / 60

    def __del__(self):
        self.pump.off()

    def abort(self):
        self.pump.off()

    def prime(self, run_time=5):
        # Alias for run() but with a default run_time
        self.run(run_time=run_time)

    def dose(self, ml):
        run_time = ml / self.rate
        self.run(run_time=run_time)

    def run(self, run_time):
        try:
            self.pump.on()
            time.sleep(run_time)
        finally:
            # No matter what happens, ensure that we stop pumping
            self.pump.off()


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


class ETapeSensor:
    def __init__(self, channel, slope=1, intercept=0):
        self.voltage = -1
        self.slope = slope
        self.intercept = intercept

        # Create the I2C bus
        i2c = busio.I2C(board.SCL, board.SDA)
        # Create the ADC object using the I2C bus
        ads = ADS.ADS1015(i2c)
        # Create single-ended input on channel
        input_chan = [ADS.P0, ADS.P1, ADS.P2, ADS.P3][channel]

        self.chan = AnalogIn(ads, input_chan)

    def read_voltage(self, num_samples=25, num_trials=8):
        # Return the mean of num_trials medians of num_samples samples
        sample_medians = []
        for _ in range(num_trials):
            samples = []
            for _ in range(num_samples):
                samples.append(self.chan.voltage)
                time.sleep(0.005)
            sample_medians.append(statistics.median(samples))

        return sum(sample_medians) / num_trials

    def _voltage_to_gallons(self, voltage):
        return round(max(self.slope * voltage + self.intercept, 0), 1)

    def read(self, with_voltage=False, num_samples=25, num_trials=8):
        voltage = self.read_voltage(num_samples, num_trials)
        gallons = self._voltage_to_gallons(voltage)

        if with_voltage:
            return gallons, voltage

        return gallons


class MPRLSSensor:
    def __init__(self, slope=1, intercept=0):
        self.slope = slope
        self.intercept = intercept
        # Create the I2C bus
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = mprls.MPRLS(i2c)
        # 1 PSI = psi_conversion_factor hPA
        self.psi_conversion_factor = 1 / 68.947572932

    def read_pressure(self, num_samples=5, num_trials=3):
        # Return the mean of num_trials medians of num_samples samples
        sample_medians = []
        for _ in range(num_trials):
            samples = []
            for _ in range(num_samples):
                samples.append(self.sensor.pressure)
                time.sleep(0.005)
            sample_medians.append(statistics.median(samples))

        return sum(sample_medians) / num_trials

    def _pressure_to_gallons(self, pressure):
        return round(max(self.slope * pressure + self.intercept, 0), 1)

    def read(self, with_pressure=False, as_psi=False, num_samples=5, num_trials=3):
        pressure = self.read_pressure(num_samples, num_trials)
        gallons = self._pressure_to_gallons(pressure)

        if as_psi:
            pressure *= self.psi_conversion_factor

        if with_pressure:
            return gallons, pressure

        return gallons


class TempSensor:
    def __init__(self):
        self.sensor = W1ThermSensor()

    def read(self, decimals=1):
        temp = self.sensor.get_temperature(Unit.DEGREES_F)

        return round(temp, decimals)
