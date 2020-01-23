from bluepy import btle
import sys, traceback

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
        
        
class PeripheralWrapper(btle.Peripheral):
    def __init__(self,name,mac):
        self.mac = mac
        self.name= name
        self.init()
        
    def init(self):
        try:
            super().__init__(self.mac)
            self.withDelegate( MyDelegate(self.name) )
            print(f'Initialised {self.name:30} with {self.mac}')
        except:
            print(f'Failed to initialise {self.name}')
            traceback.print_exc(file=sys.stdout)
            g_error.labels(position=self.name,kind='initialisation').inc()
            
    def consumeNotification(self):
        if not hasattr(self._helper,'poll'):
            self.disconnect()
            self.init()
        else:
            try:
                self.waitForNotifications(1.0)
            except:
                traceback.print_exc(file=sys.stdout)
                g_error.labels(position=self.name,kind='waitForNotif').inc()
                self.disconnect()
                

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    
    l = [ PeripheralWrapper(n,m) for n,m in dSensor.items()]

    while True:
        for i in l:
            i.consumeNotification()
                    