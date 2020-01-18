from bluepy import btle

dSensor = {
    'outdoor_entrance':'A4:C1:38:F7:9B:D3',
    'living_room'     :'A4:C1:38:E2:CC:FA',
    'corridor_upstairs':'A4:C1:38:71:9D:D4'
}

from prometheus_client import start_http_server, Gauge, Counter
g_temp = Gauge('temperature','temperature',['position'])
g_humidity = Gauge('humidity','humidity',['position'])


class MyDelegate(btle.DefaultDelegate):
    def __init__(self, name):
        btle.DefaultDelegate.__init__(self)
        self.name = name

    def handleNotification(self, cHandle, data):
        temp=int.from_bytes(data[:2],byteorder='little')/100
        humidity=int.from_bytes(data[2:3],byteorder='little')
        print(f'{self.name:25} | Temp {temp:2.2f} | Humidity {humidity:2.0f}')
        g_temp.labels(self.name).set(temp)
        g_humidity.labels(self.name).set(humidity)

def initSensor(name,mac):
    p = btle.Peripheral( mac )
    p.setDelegate( MyDelegate(name) )
    print(f'Initialised {name:30} with {mac}')
    return p

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    
    l = [ initSensor(n,m) for n,m in dSensor.items()]

    while True:
        for p in l:
            if p.waitForNotifications(1.0):
                continue
