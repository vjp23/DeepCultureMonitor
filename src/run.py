from parameters import LOG_FILENAME, CYCLE_DURATION, DB_FILENAME
from state_machine import sensor_state_machine, request_monitor
import logging
import time

logging.basicConfig(format='%(asctime)s %(message)s', filename=LOG_FILENAME, level=logging.INFO)

logging.info("\\\\\\\\\\\\\\\\\\\\\\\\ Prepare to being recording device data ////////////")
logging.info(f"Recording period: {CYCLE_DURATION}s")
logging.info(f"Using DB file:    {DB_FILENAME}")
logging.info(f"Logs recorded in: {LOG_FILENAME}s")
logging.info("Begin recording...")

while True:
    cycle_start_time = time.time()
    sensor_data = sensor_state_machine.cycle()
    cycle_time = time.time() - cycle_start_time

    request_monitor.watch(sensor_data, cycle_time)
