import time
from rpi_ws281x import Color
from grove.grove_ws2813_rgb_led_strip import GroveWS2813RgbStrip

class StripControl:
    
    def __init__ (self, control_pin, count):
        #self.control_pin = control_pin
        #self.count = count
        self.count = count
        self.strip = GroveWS2813RgbStrip(control_pin, count)
    
    def clearStrip (self):
        for i in range (self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(0,0,0))
        self.strip.show()
       
       
        
    def watering (self,watering_time, stream_size = 5):
        end = time.time() + watering_time
        i = 0
        reached_end = False
        while time.time() < end:

            if i > self.count:
                reached_end = True
                i = 0
                
            self.strip.setPixelColor(i, Color(0,0,255))
            if reached_end:
                self.strip.setPixelColor(self.count - stream_size + i, Color(0,0,0))
            
            if i > stream_size:
                reached_end = False
                self.strip.setPixelColor(i-stream_size, Color(0,0,0))
            
            self.strip.show()
            time.sleep(0.1)
            
                #print (self.strip.getPixelColor(0))
            i +=1
            
        self.clearStrip()
        #self.strip.setPixelColor(0, Color(0,0,0))
        #print (self.strip.getPixelColor(0))

            

