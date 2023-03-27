from parameters import PH_ADDRESS, EC_ADDRESS, ETAPE_CHANNEL, ETAPE_MOSFET_PIN, ETAPE_SLOPE, ETAPE_INTERCEPT, CYCLE_DURATION, DB_FILENAME
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from atlas_i2c import sensors, commands
from w1thermsensor import W1ThermSensor, Unit
from gpiozero import DigitalOutputDevice
import board
import busio
import statistics
import logging
import time
import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')))
from db.database import DeviceDatabaseHandler

DB = DeviceDatabaseHandler(DB_FILENAME)


class SolenoidDevice(object):

    def __init__(self, pin, fail_open=True):
        # By "fail open," we refer to the state of the circuit, not the solenoid
        self.output = MOSFETSwitchDevice(pin=pin, fail_open=fail_open)

    def open(self):
        self.output.on()

    def close(self):
        self.output.off()


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


class TempSensor(object):

    def __init__(self):
        self.sensor = W1ThermSensor()

    def read(self, decimals=1):
        temp = self.sensor.get_temperature(Unit.DEGREES_F)

        return round(temp, decimals)


class State:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def run(self):
        logging.error(f"run() not implemented for {self.name} node.")
        return None

    def next(self, result):
        logging.error(f"next() not implemented for {self.name} node.")
        return None


class DeviceState(State):
    def __init__(self, name, device, database):
        super().__init__(name=name)
        self.device = device
        self.db = database
        self.value = None


class pH(DeviceState):
    def __init__(self, address, database):
        device = AtlasSensor(name="ph", address=address, max_attempts=3)
        super().__init__(name="ph", device=device, database=database)

    def run(self):
        try:
            self.value = self.device.read()
            ph = round(float(self.value), 2)

            self.db.write_value("ph", ph)

            logging.info(f"pH: {ph}")
            return True

        except SystemError as e:
            logging.error(f"Sensor read error for {self.name}: " + str(e))

            self.db.write_error(self.name, str(e))

            return False

    def next(self, result):
        return DeviceStateMachine.ec


class EC(DeviceState):
    def __init__(self, address, database):
        device = AtlasSensor(name="ec", address=address, max_attempts=3)
        super().__init__(name="ec", device=device, database=database)

    def run(self):
        try:
            self.value = self.device.read()
            ec = int(round(float(self.value) / 2))

            self.db.write_value("ec", ec)

            logging.info(f"EC: {ec}")
            return True

        except SystemError as e:
            logging.error(f"Sensor read error for {self.name}: " + str(e))

            self.db.write_error(self.name, str(e))

            return False

    def next(self, result):
        return DeviceStateMachine.water_height


class WaterHeight(DeviceState):
    def __init__(self, channel, mosfet_pin, slope, intercept, database):
        device = WaterHeightSensor(channel=channel, mosfet_pin=mosfet_pin, slope=slope, intercept=intercept)
        super().__init__(name="water_height", device=device, database=database)

    def run(self):
        try:
            self.value = self.device.read(with_voltage=True)
            gallons, voltage = self.value

            self.db.write_value("water_gallons", gallons)
            self.db.write_value("water_height_volts", voltage)

            logging.info(f"Reservoir level: {gallons} gallons")
            logging.info(f"ETape Voltage: {voltage} volts")
            return True

        except SystemError as e:
            logging.error(f"Sensor read error for {self.name}: " + str(e))

            self.db.write_error(self.name, str(e))

            return False

    def next(self, result):
        return DeviceStateMachine.water_temp


class WaterTemp(DeviceState):
    def __init__(self, database):
        device = TempSensor()
        super().__init__(name="water_temp_f", device=device, database=database)

    def run(self):
        try:
            self.value = self.device.read()
            temp_f = self.value

            self.db.write_value("water_temp_f", temp_f)

            logging.info(f"Water temperature: {temp_f} degrees F")
            return True

        except SystemError as e:
            logging.error(f"Sensor read error for {self.name}: " + str(e))

            self.db.write_error(self.name, str(e))

            return False

    def next(self, result):
        return DeviceStateMachine.sleep


class Sleep(State):
    def __init__(self, cycle_duration=3600):
        super().__init__(name="sleep")
        self.last_cycle_start = time.time()
        self.cycle_duration = cycle_duration

    def run(self):
        sleep_for = max(0, self.cycle_duration - (time.time() - self.last_cycle_start))
        logging.info(f"Sleep for {sleep_for} seconds...")
        time.sleep(sleep_for)
        self.last_cycle_start = time.time()

    def next(self, _):
        return None


class StateMachine:
    def __init__(self, initial_state):
        self.initial_state = initial_state
        self.current_state = initial_state

    def step(self):
        logging.info("Step: " + str(self.current_state))
        result = self.current_state.run()
        self.current_state = self.current_state.next(result)


class DeviceStateMachine(StateMachine):
    def __init__(self):
        super().__init__(DeviceStateMachine.ph)

    def cycle(self):
        logging.info(">>>========= Begin new cycle =========<<<")
        self.current_state = self.initial_state
        while self.current_state is not None:
            self.step()

# Initialize static variables
DeviceStateMachine.ph = pH(PH_ADDRESS, DB)
DeviceStateMachine.ec = EC(EC_ADDRESS, DB)
DeviceStateMachine.water_height = WaterHeight(ETAPE_CHANNEL, ETAPE_MOSFET_PIN, ETAPE_SLOPE, ETAPE_INTERCEPT, DB)
DeviceStateMachine.water_temp = WaterTemp(DB)
DeviceStateMachine.sleep = Sleep(CYCLE_DURATION)

device_state_machine = DeviceStateMachine()
