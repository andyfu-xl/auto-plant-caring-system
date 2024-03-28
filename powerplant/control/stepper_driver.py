from gpiozero import OutputDevice
from time import sleep
import math

class StepperDriver:
    '''Drive a Stepper motor'''
    clockwise_seq = [
        (1,0,0,1),
        (0,1,0,1),
        (0,1,1,0),
        (1,0,1,0)
    ]
    def __init__(self,pins,sleep_time=0.02):
        self.pins = tuple(OutputDevice(pin) for pin in pins)
        self.sleep_time = sleep_time
        self.current_step = 0
        self.set_output()
    def set_output(self):
        '''Set output pins to match current internal state'''
        current_output = StepperDriver.clockwise_seq[self.current_step ]
        for index, value in enumerate(current_output):
            self.pins[index].value = value
    def turn(self,num_steps):
        '''
        Turn the motor the requested number of sub_steps.
        '''
        if num_steps == 0:
            return
        step = math.copysign(1,num_steps)
        for _ in range(abs(num_steps)):
            self.current_step = int(self.current_step + step) % len(StepperDriver.clockwise_seq)
            self.set_output()
            sleep(self.sleep_time)
    def close(self):
        """Clean up IO"""
        for pin in self.pins:
            pin.close()
