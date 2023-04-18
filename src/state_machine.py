from devices import (SolenoidDevice, MOSFETSwitchDevice, PeristalticPumpDevice, 
    AtlasSensor, WaterHeightSensor, TempSensor)
import parameters as prm
import logging
import time
import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')))
from db.database import DeviceDatabaseHandler
from flags.flag_utils import read_flag, set_flag

DB = DeviceDatabaseHandler(prm.DB_FILENAME)


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
    def __init__(self, channel, slope, intercept, database):
        device = WaterHeightSensor(channel=channel, slope=slope, intercept=intercept)
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
    def __init__(self, cycle_duration=3600, fill_flag_path=''):
        super().__init__(name="sleep")
        self.last_cycle_start = time.time()
        self.cycle_duration = cycle_duration
        self.fill_flag_path = fill_flag_path

    def _monitor(self, sleep_for, cycle_period=0.25):
        stop_at = time.time() + sleep_for
        while time.time() < stop_at:
            try:
                flag, set_at = read_flag(self.fill_flag_path)
            except FileNotFoundError:
                flag = 0
            if flag:
                logging.info('++++++++++++++++++++++++++++++!!!! FLAG SET !!!!++++++++++++++++++++++++++++++')
                set_flag(self.fill_flag_path, 0)
            time.sleep(cycle_period)

    def run(self):
        sleep_for = max(0, self.cycle_duration - (time.time() - self.last_cycle_start))
        logging.info(f"Monitor for requests for {sleep_for} seconds...")
        self._monitor(sleep_for)
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
    # Initialize static variables
    ph = pH(prm.PH_ADDRESS, DB)
    ec = EC(prm.EC_ADDRESS, DB)
    water_height = WaterHeight(prm.ETAPE_CHANNEL,
                               prm.ETAPE_SLOPE,
                               prm.ETAPE_INTERCEPT,
                               DB)
    water_temp = WaterTemp(DB)
    sleep = Sleep(prm.CYCLE_DURATION, prm.FILL_FLAG_PATH)

    def __init__(self):
        super().__init__(DeviceStateMachine.ph)

    def cycle(self):
        logging.info(">>>========= Begin new cycle =========<<<")
        self.current_state = self.initial_state
        while self.current_state is not None:
            self.step()

device_state_machine = DeviceStateMachine()
