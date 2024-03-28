import serial

READ_SENSOR = '0'
LED_ON = '1'
LED_OFF = '2'

class ArduinoDriver():

    def __init__(self, baudrate, timeout):
        """Initialise the arduino driver including the serial baud rate and listener time out"""
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
    
    def init_serial(self):
        """Initialise the serial to build up communication between raspberry pi and arduino with a reasonable listener timeout"""
        acm0_connected = False
        acm1_connected = False
        # Try to connect arduino through ttyACM0
        try:
            self.ser = serial.Serial('/dev/ttyACM0', baudrate=self.baudrate, timeout=self.timeout)
            acm0_connected = True
            connected_port = '/dev/ttyACM0'
        except(Exception):
            acm0_connected = False
        
        # If first try failed, try to connect through ttyACM1
        if not acm0_connected:
            try:
                self.ser = serial.Serial('/dev/ttyACM1', baudrate=self.baudrate, timeout=self.timeout)
                acm1_connected = True
                connected_port = '/dev/ttyACM0'
            except(Exception):
                acm1_connected = False
                raise Exception("Serial communication establishment failed, Arduino device not connected!")

        # Clear input buffer
        self.ser.reset_input_buffer()
        
        if acm0_connected or acm1_connected:
            print(f"Serial communication established successfully through {connected_port}.")

    def read_moisture_value(self):
        """Ask the the arduino for moisture value, and returns its response"""
        if self.ser is None:
            raise Exception("Serial Communication not established!")
        self.ser.write(READ_SENSOR.encode('utf-8'))
        response = self.ser.readline().decode('utf-8').rstrip()
        return response

    def turn_on_LED(self, section):
        """Turn on the LED with the corresponding section"""
        if self.ser is None:
            raise Exception("Serial Communication not established!")
        command = str(section) + "_" + LED_ON
        self.ser.write(command.encode('utf-8'))

    def turn_off_LED(self, section):
        """Turn off the LED with teh corresponding section"""
        if self.ser is None:
            raise Exception("Serial Communication not established!")
        command = str(section) +"_" +  LED_OFF
        self.ser.write(command.encode('utf-8'))

    def turn_on_all_LEDs(self):
        """Turn on all of the LEDs"""
        if self.ser is None:
            raise Exception("Serial Communication not established!")
        command = LED_ON
        self.ser.write(command.encode('utf-8'))

    def turn_off_all_LEDs(self):
        """Turn off all of the LEDs"""
        if self.ser is None:
            raise Exception("Serial Communication not established!")
        command = LED_OFF
        self.ser.write(command.encode('utf-8'))