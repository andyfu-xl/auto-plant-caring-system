import threading

import time
from ..database_interface import DatabaseInterface
from ..control.robot_controller import RobotController
from ..state.robot_state import RobotState
from .watering import Watering

class RobotManager:
    """
    Class to coorled_strip_controldinate robots actions and state
    Takes internal state as initilisation argument
    This internal state should not be shared with any other process!!
    """
    def __init__(self):
        self.thread = None
    def start(self):
        """
        Begin running of robot
        Return:
            0 = couldn't start
            1 = started
        """
        if self.thread and self.thread.is_alive():
            print("RobotManager already running")
            return 0
        self.thread = RobotManagerThread()
        self.thread.start()
        return 1
    def stop(self):
        """
        Gracefully stop running robot
        Return:
           0 = couldn't stop
           1 = stopped
        """
        if not self.thread:
            print("RobotManager never started")
            return 0
        if not self.thread.is_alive():
            print("RobotManager already stopped")
            return 0#
        print("Stopping RobotManager...")
        self.thread.stop()
        self.thread.join()
        return 1

class RobotManagerThread(threading.Thread):
    """Runs robot manager services asyncronously"""
    def __init__(self):
        super().__init__()
        self.stop_event = threading.Event()
    def stop(self):
        """Mark thread as needing to stop"""
        self.stop_event.set()
    def run(self):
        robot_controller = RobotController()
        print("RobotContoller started")
        database_interface = DatabaseInterface(machine_id="robot")
        database_interface.initialize_planter_remote()
        state = RobotState(database_interface, robot_controller.arduino)
        watering_manager = Watering(robot_controller, state)
        while not self.stop_event.is_set():
            watering_manager.check_for_actions(state.pots)
            time.sleep(0.1)

