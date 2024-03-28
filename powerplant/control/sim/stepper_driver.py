from .net import send_signal
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
    def __init__(self,pins,sleep_time=0.01):
        self.device_name = "a3"
        self.sleep_time = sleep_time
    def turn(self,num_steps):
        '''
        Turn the motor the requested number of sub_steps.
        '''
        if num_steps == 0:
            return
        step = math.copysign(1,num_steps)
        for _ in range(abs(num_steps)):
            send_signal(self.device_name,step)
            sleep(self.sleep_time)
    def close(self):
        """Clean up IO"""
