# DeepCultureMonitor
A Raspberry Pi-based monitoring and control system for deep water culture (DWC) hydroponics.

Supports pH, EC, temperature, and water level monitoring and water level adjustments via solenoid control.

## Modules

This project comprises three modules, each implemented within its own Docker container:
- *Devices* Found in `build/` and `src/` and launched via `start_budbucket_devices.sh`. Uses a state machine pattern to read data from sensors and write it to a SQLite database in a loop.
- *Server* Found in `server-build/` and `server-src/` and launched via `start_budbucket_server.sh`. Runs a very simple Flask server that reads sensor data from the SQLite database and populates zoomable charts created using [Chart.js](https://www.chartjs.org/).
- *IP* Found in `ip-build/` and `sip-src/` and launched via `start_budbucket_ip_loop.sh`. This is a workaround to emulate a static IP. Each 30 seconds, checks the device's public IP and then compares against a record in Google Cloud's Firestore. A domain record is pointed to a Google Cloud Function, which reads the device's public IP from Firestore and redirects the request to the Raspberry Pi. This is set for replacement via Cloudflare.

## Roadmap:
- Documentation of hardware configuration
- Replacement of GCP-based IP tracking with Cloudflare DDNS
- Orchestration via docker-compose
- Light level monitoring (on/off, and then lux measurement)
- Relay control for switching reservoir drain pump, top feed pump, and lighting
- Support peristaltic pump control
- Support max/min limits for water level, pH, and EC with automated fertigation/water level adjustments
- Control using P(I)D control
- Full grow lifecycle automation
- Configurable alerts via email and/or SMS
