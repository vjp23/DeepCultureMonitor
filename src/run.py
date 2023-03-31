from parameters import LOG_FILENAME, CYCLE_DURATION, DB_FILENAME
from state_machine import device_state_machine
import logging


logging.basicConfig(format='%(asctime)s %(message)s', filename=LOG_FILENAME, level=logging.INFO)

logging.info("\\\\\\\\\\\\\\\\\\\\\\\\ Prepare to being recording device data ////////////")
logging.info(f"Recording period: {CYCLE_DURATION}s")
logging.info(f"Using DB file:    {DB_FILENAME}")
logging.info(f"Logs recorded in: {LOG_FILENAME}s")
logging.info("Begin recording...")

while True:
    device_state_machine.cycle()
