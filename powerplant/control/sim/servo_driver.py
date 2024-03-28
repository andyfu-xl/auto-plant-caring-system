from datetime import datetime, timedelta
import time
import threading
from .net import send_signal

#TODO: Likely to need modification once specific servo to be used has been selected
class ServoDriver:
    """Simple servo driver based off of specs for simple three pin servo"""
    def __init__(self,control_pin, angle_range, signal_range, max_speed=100):
        """Maxspeed is in milliseconds per degree"""
        #Set up IO
        self.device_name = str(control_pin)
        #Range information
        self.min_angle, self.max_angle = angle_range
        self.max_speed = max_speed
        #Head of action queue
        self.latest_action = None
        self.latest_angle = angle_range[0]
    def set_angle(self, angle, time=None, wait=False):
        """
        Set the angle of the servo taking a given number of milliseconds
        Returns:
            0 = failed
            1 = action queued
        """
        #Validate angle
        if (angle < self.min_angle) or (angle > self.max_angle):
            print(
                f"Servo on pin {self.device_name} could not set angle to {angle}°."+
                f" Max range [{self.min_angle}°-{self.max_angle}°]"
                )
            return 0
        #Validate time
        fastest_time = 0.001 + abs(angle - self.latest_angle)*self.max_speed
        if time is None:
            time = fastest_time
        elif not time>=fastest_time:
            print(
                f"Servo on pin {self.device_name} could not set angle to {angle}° in {time}ms."+
                f" {fastest_time}ms min time frame."
                )
            return 0
        #Enqueue action
        angle_range = (self.latest_angle, angle)
        self.latest_action = ServoAction(
            self.device_name,
            time,
            angle_range,
            self.latest_action
        )
        self.latest_angle = angle
        self.latest_action.start()
        if wait:
            self.wait_to_complete()
        return 1
    def wait_to_complete(self):
        """Wait for all actions in servo action queue to complete"""
        if self.latest_action:
            self.latest_action.join()
    def is_stationary(self):
        """Report if the servo still has actions yet to complete"""
        return (self.latest_action is None) or (not self.latest_action.is_alive())
    def close(self):
        """Clean up IO"""
        self.wait_to_complete()

class ServoAction(threading.Thread):
    """Carry out servo action in seperate thread"""
    def __init__(self, device_name, target_duration, angle_range, prev_action):
        super().__init__()
        self.prev_action = prev_action
        self.target_duration = target_duration
        self.device_name = device_name
        self.start_angle, self.end_angle = angle_range
    def run(self):
        #Wait for previous action to complete
        if self.prev_action:
            self.prev_action.join()
        self.prev_action = None
        #Initilise times
        start = datetime.now()
        end = start + timedelta(microseconds=self.target_duration*1000)
        total = end-start
        #Manage pin output over course of action
        while not datetime.now() > end:
            progress = (datetime.now()-start)/total
            out_angle = self.start_angle + progress*(self.end_angle-self.start_angle)
            send_signal(self.device_name, out_angle)
            time.sleep(0.01) ##Wait a centisecond. Eliminates unneccissary processing
        send_signal(self.device_name, self.end_angle)
