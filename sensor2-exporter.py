from bluepy import btle

dSensor = {
    'outdoor_entrance':'A4:C1:38:F7:9B:D3',
    'living_room'     :'A4:C1:38:E2:CC:FA',
    'corridor_upstairs':'A4:C1:38:71:9D:D4'
}

from prometheus_client import start_http_server, Gauge, Counter
# Metrics definition
g_temp = Gauge('temperature','temperature',['position'])
g_humidity = Gauge('humidity','humidity',['position'])
g_error = Counter('error','error',['position','kind'])


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
    try:
        p = btle.Peripheral( mac )
        p.withDelegate( MyDelegate(name) )
        print(f'Initialised {name:30} with {mac}')
        return p
    except:
        print(f'Failed to initialise {name}')
        g_error.labels(position=name,kind='initialisation').inc()
        return (name,mac)
    
if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    
    l = [ initSensor(n,m) for n,m in dSensor.items()]

    while True:
        for i,p in enumerate(l):
            #Manage connection issues
            if type(p)==tuple :
                (name,mac)=p
                l[i]=initSensor(name,mac)  # TODO: not elegant
                continue
                
            try:
                if p.waitForNotifications(1.0):
                    continue
            except btle.BTLEDisconnectError:
                print(f'{p.addr} disconnect')
                g_error.labels(position=name,kind='disconnect').inc()
                try:
                    p.connect(p.addr)
                except:
                    g_error.labels(position=name,kind='reconnect').inc()
                    