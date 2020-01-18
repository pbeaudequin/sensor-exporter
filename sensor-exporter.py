from btlewrap import BluepyBackend
from mitemp_bt.mitemp_bt_poller import MiTempBtPoller, \
    MI_TEMPERATURE, MI_HUMIDITY, MI_BATTERY
import bluepy, time

from prometheus_client import start_http_server, Gauge, Counter
g_temp = Gauge('temperature','temperature',['position'])
g_humidity = Gauge('humidity','humidity',['position'])
g_battery = Gauge('battery','battery',['position'])
c_error = Counter('error_counter','error counter',['position'])

def pollData(position,mac):
    try:
        poller = MiTempBtPoller(mac,BluepyBackend)
        t = poller.parameter_value(MI_TEMPERATURE)
        h = poller.parameter_value(MI_HUMIDITY)
        b = poller.parameter_value(MI_BATTERY)
        print(f'Temperature {t} | Humidity {h}')
        g_temp.labels(position).set(t)
        g_humidity.labels(position).set(h)
        g_battery.labels(position).set(b)
    except:
        print('Unable to read data')
        c_error.labels(position).inc(1)
        

if __name__ == '__main__':
    dMAC={
        'salon':'4c:65:a8:d0:5e:c3'
    }
    # Start up the server to expose the metrics.
    start_http_server(8000)
    # Generate some requests.
    while True:
        for position,mac in dMAC.items():
            pollData(position,mac)
            
        time.sleep(25)
        