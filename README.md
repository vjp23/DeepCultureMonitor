# DeepCultureMonitor
A Raspberry Pi-based monitoring and control system for deep water culture (DWC) hydroponics.

Supports pH, EC, temperature, and water level monitoring as well as adjustments via solenoid and pump control.

Currently supports up to six peristaltic pumps. These can be used, for example, for pH Up, pH Down, and four nutrient or additive solutions.

## Modules

This project comprises three modules, each implemented within its own Docker container:
- *Devices* Found in `build/` and `src/` and launched via `start_budbucket_devices.sh`. Uses a state machine pattern to read data from sensors and write it to a SQLite database in a loop.
- *Server* Found in `server-build/` and `server-src/` and launched via `start_budbucket_server.sh`. Runs a very simple Flask server that reads sensor data from the SQLite database and populates zoomable charts created using [Chart.js](https://www.chartjs.org/).

## Roadmap
- Documentation of hardware configuration
- Orchestration via docker-compose
- Light level monitoring (on/off, and then lux measurement)
- Support max/min limits for water level, pH, and EC with automated fertigation/water level adjustments
- Control using P(I)D control
- Full grow lifecycle automation
- Configurable alerts via email and/or SMS
