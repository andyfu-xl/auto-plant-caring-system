import time
from .net import getReading, send_signal


class StripControl:
    
    def __init__ (self, control_pin, count):
        #self.control_pin = control_pin
        #self.count = count
        self.count = count
        self.strip = None
        self.device_name = 'led_strip_control'
       
        
    def watering (self,watering_time):
        send_signal(self.device_name, 1)
        time.sleep(watering_time)
        send_signal(self.device_name, -1)

            

