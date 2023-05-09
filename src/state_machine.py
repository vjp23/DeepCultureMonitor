from devices import (SolenoidDevice, MOSFETSwitchDevice, PeristalticPumpDevice, 
    AtlasSensor, WaterHeightSensor, TempSensor, MultichannelSolidStateRelayDevice)
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

    def run(self, silent=False):
        try:
            self.value = self.device.read()
            ph = round(float(self.value), 2)

            if not silent:
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

    def run(self, silent=False):
        try:
            self.value = self.device.read()
            ec = int(round(float(self.value) / 2))

            if not silent:
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

    def run(self, silent=False, **kwargs):
        try:
            self.value = self.device.read(with_voltage=True, **kwargs)
            gallons, voltage = self.value

            if not silent:
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

    def run(self, silent=False):
        try:
            self.value = self.device.read()
            temp_f = self.value

            if not silent:
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

    def query(self, device, silent=False, **kwargs):
        device = device.lower()

        if device == "ph":
            return self.ph.run(silent=silent, **kwargs)
        if device == "ec":
            return self.ec.run(silent=silent, **kwargs)
        if device == "level":
            return self.water_height.run(silent=silent, **kwargs)

        return None

    def cycle(self):
        logging.info(">>>========= Begin new cycle =========<<<")
        self.current_state = self.initial_state
        self.results = dict()
        while self.current_state is not None:
            self.step()

        return self.results


class ReservoirSolenoid:
    def __init__(self, pin, database):
        self.device = SolenoidDevice(pin=pin, fail_open=True)
        self.db = database
        self.name = "solenoid"
        self.value = 0

    def __str__(self):
        return self.name

    def __del__(self):
        try:
            self.device.close()
            self.value = 0
        except:
            pass

    def open(self):
        if self.value != 1:
            try:
                self.device.open()
                self.value = 1

                self.db.write_value("solenoid", 1)
                logging.info(f"Solenoid open")

            except Exception as e:
                logging.error("Solenoid open error")
                self.db.write_error(self.name, str(e))        

    def close(self):
        if self.value != 0:
            try:
                self.device.close()
                self.value = 0

                self.db.write_value("solenoid", 0)
                logging.info(f"Solenoid closed")

            except Exception as e:
                logging.error(f"Solenoid close error: {e}")
                self.db.write_error(self.name, str(e))


class DosingPump:
    def __init__(self, name, pin, ml_per_min, database):
        self.device = PeristalticPumpDevice(pin=pin, ml_per_min=ml_per_min)
        self.db = database
        self.name = name

    def __str__(self):
        return self.name

    def __del__(self):
        try:
            self.device.abort()
        except:
            pass

    def dose(self, ml):
        try:
            logging.info(f"Dosing {ml} mL of {self.name}")
            self.device.dose(ml)
            self.db.write_value(self.name, ml)

        except Exception as e:
            logging.error(f"{self.name} dosing error: {e}")
            self.db.write_error(self.name, str(e))


class Relay:
    def __init__(self, device, channel, name, db):
        # device should be and instance of MultichannelSolidStateRelayDevice atm
        self.device = device
        self.channel = channel
        self.name = name
        self.db = db

    def status(self):
        return self.device.status(self.channel)

    def on(self):
        try:
            logging.info(f"Powering on {self.name}")
            self.device.on(self.channel)
            self.db.write_value(self.name, 1)

        except Exception as e:
            logging.error(f"{self.name} power on error: {e}")
            self.db.write_error(self.name, str(e))
        
    def off(self):
        try:
            logging.info(f"Powering off {self.name}")
            self.device.off(self.channel)
            self.db.write_value(self.name, 0)

        except Exception as e:
            logging.error(f"{self.name} power off error: {e}")
            self.db.write_error(self.name, str(e))


class Controls:
    def __init__(self, **kwargs):
        ok_keys = {'solenoid', 'ph_up', 'ph_down', 'nute1', 'nute2', 'nute3', 
                   'nute4', 'drain', 'topfeed', 'veg_light', 'bloom_light'}
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in ok_keys)


class RequestMonitor(State):
    def __init__(self, cycle_duration=900, flag_path='', sensors=None, controls=None):
        self.name = "sleep"
        self.file_err_flag = False
        # At first, assume a 7.7-second runtime (but get better data over time)
        self.run_times = [7.7] * 11
        self.cycle_duration = cycle_duration
        self.flag_path = flag_path
        self.sensors = sensors
        self.controls = controls
        self.db = DB

    def __str__(self):
        return self.name

    def _get_wait_time(self):
        sorted_times = sorted(self.run_times)
        mid_times = sorted_times[3:8]
        mean_runtime = sum(mid_times) / len(mid_times)
        logging.info(f"Mean runtime: {round(mean_runtime, 3)} seconds")
        return max(0, self.cycle_duration - mean_runtime)

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

    def _update_flag(self, flag, device, action, key, value):
        flag[device][action][key] = value
        set_flag(self.flag_path, flag)
        return flag

    def process_flag_requests(self, flag):
        new_requests = []

        for device in flag:
            for action, req in flag[device].items():
                if req['status'] == 'request':
                    logging.info(f"New request for {device}: {flag[device]}")
                    new_requests.append((device, action, flag[device][action]['value']))

        if new_requests:
            plan = self._build_plan(new_requests)
            self.execute_plan(plan, flag)

    def _build_plan(self, new_requests):
        """Here, we essentially just reorder the list of requests.

        The order matters because some operations make sense only in one
        serial direction, e.g. empyting a reservoir and then filling it, or
        always adding FloraMicro before other nutrients.

        Order algo:
        0   [TODO: Relay controls (lights, top-feed pump)]
        1   Empty reservoir
        2   Set reservoir water level
        3   Fill reservoir
        4   Dose FloraMicro
        5-7 Dose other nutrients (arbitrary order)
        8   Dose ph Up
        9   Dose pH Down

        O(n^2), triangular in n really, but n <= 9 so not worth optimizing :)
        """
        optimal_order = [('level', 'empty'), ('level', 'set'), 
                         ('level', 'fill'), ('ec', 'nute2'), ('ec', 'nute1'), 
                         ('ec', 'nute3'), ('ec', 'nute4'), ('ph', 'up'), 
                         ('ph', 'down')]

        plan = []
        for device, action in optimal_order:
            for req in new_requests:
                req_device, req_action, _ = req
                if device == req_device and action == req_action:
                    plan.append(req)
                    new_requests.remove(req)

        return plan

    def execute_plan(self, plan, flag):
        for (device, action, value) in plan:
            took_action = False
            mixin = False
            # Water level controls
            if device == 'level':
                # Start by getting the current water level
                current = self.sensors.query('level', silent=True)

                # Add water
                if (action == 'fill') or (action == 'set' and value > current):
                    # Add water! :)
                    try:
                        latest_level = self.sensors.query('level', silent=True, 
                                                          num_samples=5, 
                                                          num_trials=3)
                        while latest_level < value:
                            self.controls.solenoid.open()
                            logging.info(f"Water level: {latest_level}")
                            latest_level = self.sensors.query('level', 
                                                              silent=True, 
                                                              num_samples=5, 
                                                              num_trials=3)
                        logging.info(f"Water level: {latest_level}")

                    finally:
                        self.controls.solenoid.close()
                        # Let stuff mix and settle for a few seconds
                        mixin = 10
                        took_action = True
                        
                # Remove water
                elif (action == 'drain') or (action == 'set' and value < current):
                    # Turn on the drain pump
                    logging.info("Activate drain pump relay")
                    pass

            elif device == 'ec':
                if action == 'nute1':
                    logging.info("EC plan executed for FloraGro :)")
                elif action == 'nute2':
                    self.controls.nute2.dose(value)
                    took_action = True
                    mixin = 10
                elif action == 'nute3':
                    self.controls.nute3.dose(value)
                    took_action = True
                    mixin = 10
                elif action == 'nute4':
                    self.controls.nute4.dose(value)
                    took_action = True
                    mixin = 10

            elif device == 'ph':
                if action == 'up':
                    self.controls.ph_up.dose(value)
                    took_action = True
                    mixin = 10
                elif action == 'down':
                    self.controls.ph_down.dose(value)
                    took_action = True
                    mixin = 10

            self._update_flag(flag, device, action, "status", "fulfilled")

        if took_action:
            # Sleep for mixin, then update the sensor data
            if mixin:
                logging.info(f"Sleep for {mixin} seconds to allow for mixing")
                time.sleep(mixin)
            self.sensors.cycle()

    def watch(self, sensor_data, cycle_time):
        logging.info(f"Last sensor cycle took {round(cycle_time, 3)} seconds")
        self.run_times = [cycle_time] + self.run_times[:10]
        self.file_err_flag = False
        wait_for = self._get_wait_time()
        logging.info(f"Monitor for requests for {wait_for} seconds...")
        self.wait_for_requests(wait_for)


relays_device = MultichannelSolidStateRelayDevice(address=prm.RELAY_ADDRESS, 
                                                  channels=4)
sensor_state_machine = SensorStateMachine()
controls = Controls(solenoid=ReservoirSolenoid(prm.SOLENOID_PIN, DB),
                    ph_up=DosingPump("pH Up", prm.PHUPPIN, prm.PHUPRATE, DB),
                    ph_down=DosingPump("pH Down", prm.PHDOWNPIN, prm.PHDOWNRATE, DB),
                    nute1=DosingPump("FloraGro", prm.NUTE1PIN, prm.NUTE1RATE, DB),
                    nute2=DosingPump("FloraMicro", prm.NUTE2PIN, prm.NUTE2RATE, DB),
                    nute3=DosingPump("FloraBloom", prm.NUTE3PIN, prm.NUTE3RATE, DB),
                    nute4=DosingPump("CALiMAGic", prm.NUTE4PIN, prm.NUTE4RATE, DB),
                    drain=Relay(relays_device, 1, "Drain Pump", DB),
                    topfeed=Relay(relays_device, 2, "Top Fee Pump", DB),
                    veg_light=Relay(relays_device, 3, "Veg Lights", DB),
                    bloom_light=Relay(relays_device, 4, "Flower Lights", DB))
request_monitor = RequestMonitor(prm.CYCLE_DURATION, prm.FLAG_PATH, 
                                 sensor_state_machine, controls)