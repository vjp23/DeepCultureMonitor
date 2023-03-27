from google.cloud import firestore
import subprocess
import logging
import time
import os

LOG_FILENAME = os.environ["LOG_FILENAME"]
UPDATE_IP_EVERY = int(os.environ["UPDATE_IP_EVERY"])

logging.basicConfig(format='%(asctime)s %(message)s', filename=LOG_FILENAME, level=logging.INFO)


def update_ip():
    # Get the router's public IP
    process = subprocess.Popen(['curl', 'http://icanhazip.com'], 
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # Decode the bytes object
    ip = stdout.decode('utf-8').replace('\n', '')

    # Check IP in DB
    db = firestore.Client()
    db_ref = db.collection('dwc_pi_ip').document('dwcpiipaddress')
    ip_in_db = db_ref.get().to_dict()['ip_address']

    # Update if mismatch
    if ip_in_db != ip:
            logging.info('IP changed! Previously was', ip_in_db, 'new IP is', ip)
            db_ref.update({'ip_address': ip})

while True:
    update_ip()
    time.sleep(UPDATE_IP_EVERY)
