import time
from math import floor
from .net import getReading
from .stepper_driver import StepperDriver

# Disallow servo movements taking more than 5 seconds
MAX_MOTOR_MOVE_TIME = 15
# Assume the robot arm is at the base initially
INITIAL_POSITION = 0
# Acceptable distance between the robot arm and the target in meters
TOLERANCE = 0.02
# Maximum distance that a distance sensor could read reliably is 400 cm
MAX_SENSOR_DISTANCE = 400
# Minimum distance that a distance sensor could read reliably is 0 cm
MIN_SENSOR_DISTANCE = 0
# Height of the system
SYSTEM_HEIGHT = 60
# estimated distance moved with one steppermotor step
STEP_DIST = 1

class PrismaticDriver:
    """Driver for stepper motor prismatic joint."""
    def __init__(self, motor_pins, sensor_pins, position_range):
        # Range information
        self.lowest_position, self.highest_position = position_range
        if self.highest_position > MAX_SENSOR_DISTANCE or self.lowest_position < MIN_SENSOR_DISTANCE:
            raise ValueError(
                "The position range should be within sensor range: "
                f"[{MIN_SENSOR_DISTANCE}cm-{MAX_SENSOR_DISTANCE}cm]"
                )
        # Motor IO
        self.motor = StepperDriver(motor_pins)
        # Distance sensor IO
        self.distance_sensor_name = "dist"
    def set_position(self, target_position, timeout=MAX_MOTOR_MOVE_TIME):
        """Set the position of the joint end."""
        if self.lowest_position > target_position or self.highest_position < target_position:
            raise ValueError(
                f"Invalid target position {target_position}cm. "
                f"Must be in range [{self.lowest_position}cm-{self.highest_position}cm]"
                )
        start_time = time.time()
        distance_to_target = self.get_distance_to_target(target_position)
        self.motor.turn(floor(distance_to_target/STEP_DIST))
        while abs(distance_to_target) > TOLERANCE:
            self.motor.turn(1 if distance_to_target > 0 else -1)
            distance_to_target = self.get_distance_to_target(target_position)
            #Check for timeout
            current_time = time.time()
            if current_time - start_time > timeout:
                raise TimeoutError(
                    f"Prismatic joint took over {timeout}s to complete move "
                    f"to {target_position}cm and timed out."
                )
        return 1
    def get_distance_to_target(self, target):
        """Get distance from current position to a target position."""
        reading = getReading(self.distance_sensor_name)
        return target - reading #TODO: Fine tune this conversion
    def close(self):
        """Clean up IO"""

class DummyDriver:
    def set_position(self,_):
        time.sleep(1)
    def close(self):
        pass