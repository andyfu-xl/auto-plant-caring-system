
from .net import getReading, send_signal

READ_SENSOR = '0'
LED_ON = '1'
LED_OFF = '2'

class ArduinoDriver():

    def __init__(self, baudrate, timeout):
        """Initialise the arduino driver including the serial baud rate and listener time out"""
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.moisture_name = 'moisture_driver'
        self.led_name = 'led_driver'
    
    def read_moisture_value(self):
        """Ask the the arduino for moisture value, and returns its response"""
        response = getReading(self.moisture_name)
        return response

    def turn_on_LED(self, section):
        """Turn on the LED with the corresponding section"""
        send_signal(self.led_name, section+1)

    def turn_off_LED(self, section):
        """Turn off the LED with the corresponding section"""
        send_signal(self.led_name, -section-1)

    def turn_on_all_LEDs(self):
        """Turn on all of the LEDs"""
        from robot_controller_base import NUM_SECTIONS
        for i in range(NUM_SECTIONS):
            self.turn_on_LED(i)

    def turn_off_all_LEDs(self):
        """Turn off all of the LEDs"""
        from robot_controller_base import NUM_SECTIONS
        for i in range(NUM_SECTIONS):
            self.turn_off_LED(i)
        