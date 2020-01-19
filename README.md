# sensor-exporter
Prometheus exporter for Xiaomi temperature and humidity sensor LYWSD03MMC

## Abstract
The prometheus exporter will spawn an HTTP server to be scrapped by Prometheus.
To grab data, the process will connect to the listed low energy bluetooth device and will update the prometheus metrics *upon bluetooth notifications*.

## Installation

1. `apt install libglib2.0-dev`
2. `pip install -r requirements.txt`
3. In a screen : `python sensor2-exporter.py`
4. Install Prometheus and scrape port 8000

## TODOs

- Gracefull exit on Ctrl+C (cf : https://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python
)
- manage bluepy.btle.BTLEDisconnectError: Device disconnected | First attempt done
- Publish Grafana dashboard on grafana.com
- Manage configuration properly in a separate YAML file

## Grafana dashboard

One can operate grafana as a docker image.
A dashboard json file is available : `grafana_dashboard.json`

## Devices

Extracted with `sudo hcitool lescan`.

- 4C:65:A8:D0:5E:C3 MJ_HT_V1   --> living_room (old sensor version)
- A4:C1:38:F7:9B:D3 LYWSD03MMC --> Outside entrance
- A4:C1:38:E2:CC:FA LYWSD03MMC --> living_room (new sensor)
- A4:C1:38:71:9D:D4 LYWSD03MMC --> bathroom