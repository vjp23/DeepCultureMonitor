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

            return ph

        except SystemError as e:
            logging.error(f"Sensor read error for {self.name}: " + str(e))
            self.db.write_error(self.name, str(e))

            return 0

    def next(self, result):
        return SensorStateMachine.ec


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

            return ec

        except SystemError as e:
            logging.error(f"Sensor read error for {self.name}: " + str(e))
            self.db.write_error(self.name, str(e))

            return 0

    def next(self, result):
        return SensorStateMachine.water_height


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

            return gallons

        except SystemError as e:
            logging.error(f"Sensor read error for {self.name}: " + str(e))
            self.db.write_error(self.name, str(e))

            return 0

    def next(self, result):
        return SensorStateMachine.water_temp


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

            return temp_f

        except SystemError as e:
            logging.error(f"Sensor read error for {self.name}: " + str(e))
            self.db.write_error(self.name, str(e))

            return 0

    def next(self, _):
        return None


class StateMachine:
    def __init__(self, initial_state):
        self.initial_state = initial_state
        self.current_state = initial_state

    def step(self):
        current_state_name = str(self.current_state)
        logging.info("Step: " + current_state_name)
        result = self.current_state.run()
        self.results[current_state_name] = result
        self.current_state = self.current_state.next(result)


class SensorStateMachine(StateMachine):
    # Initialize static variables
    ph = pH(prm.PH_ADDRESS, DB)
    ec = EC(prm.EC_ADDRESS, DB)
    water_height = WaterHeight(prm.ETAPE_CHANNEL,
                               prm.ETAPE_SLOPE,
                               prm.ETAPE_INTERCEPT,
                               DB)
    water_temp = WaterTemp(DB)

    def __init__(self):
        super().__init__(SensorStateMachine.ph)

    def cycle(self):
        logging.info(">>>========= Begin new cycle =========<<<")
        self.current_state = self.initial_state
        self.results = dict()
        while self.current_state is not None:
            self.step()

        return self.results


class RequestMonitor(State):
    def __init__(self, cycle_duration=900, flag_path='', sensor_machine=None):
        self.name = "sleep"
        self.file_err_flag = False
        self.run_times = []
        self.cycle_duration = cycle_duration
        self.flag_path = flag_path
        self.sensor_machine = sensor_machine
        self.db = DB

    def __str__(self):
        return self.name

    def _get_wait_time(self):
        if len(self.run_times) >= 11:
            # Once we've done at least 11 trials, start using a mean of medians
            sorted_times = sorted(self.run_times)
            mid_times = sorted_times[3:8]
            mean_runtime = sum(mid_times) / len(mid_times)
            return max(0, self.cycle_duration - (mean_runtime - self.cycle_duration))
        else:
            # Until then, just guess- like, 5 seconds or so?
            return max(0, self.cycle_duration - 5)

    def wait_for_requests(self, wait_for, sleep_time=0.25):
        stop_at = time.time() + wait_for - sleep_time
        while time.time() < stop_at:
            try:
                flag, set_at = read_flag(self.flag_path)
            except FileNotFoundError:
                # Use this flag to ensure we don't log this error 4 times a second :]
                if not self.file_err_flag:
                    logging.error(f'Flag file not found at {self.flag_path}!')
                    self.file_err_flag = True
                flag = dict()
            self.process_flag_requests(flag)
            time.sleep(sleep_time)

    def _update_flag(self, flag, flag_name, key, value):
        flag[flag_name][key] = value
        set_flag(self.flag_path, flag)
        return flag

    def process_flag_requests(self, flag):
        for flag_name in flag:
            if flag[flag_name]['status'] == 'request':
                self._update_flag(flag, flag_name, 'status', 'fulfilling')
                
                time.sleep(10)

                self._update_flag(flag, flag_name, 'status', 'fulfilled')
                # self.db.write_value(name, value)

    def watch(self, sensor_data, cycle_time):
        self.run_times = [cycle_time] + self.run_times[:10]
        self.file_err_flag = False
        wait_for = self._get_wait_time()
        logging.info(f"Monitor for requests for {wait_for} seconds...")
        self.wait_for_requests(wait_for)

sensor_state_machine = SensorStateMachine()
request_monitor = RequestMonitor(prm.CYCLE_DURATION, prm.FLAG_PATH, sensor_state_machine)
