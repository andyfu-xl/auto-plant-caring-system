from .sim.servo_driver import ServoDriver
from .sim.prismatic_driver import PrismaticDriver, DummyDriver
from .sim.arduino_driver import ArduinoDriver
from .sim.led_strip_control import StripControl

from math import acos, pi
import time

# Layout
NUM_LAYERS = 2
NUM_SECTIONS = 3
# Dimensions
INTER_LAYER_HEIGHT = 30
FIRST_LAYER_HEIGHT = 15
UPPER_ALLOWANCE = 8
BRUSH_ANGLE = 5
BRUSH_SIZE = 3
BRUSH_HEIGHT = 7
SENSOR_LENGTH = 6.5
UPPER_ARM_LENGTH = 25
LOWER_ARM_LENGTH = 19
SWEEP_ZONE_LENGTH = 35
#Pre-calculate
A_1_REST_ANGLE = acos(LOWER_ARM_LENGTH/(2*UPPER_ARM_LENGTH)) * (180/pi)
A_1_PREDEPLOY_ANGLE = acos(
    (UPPER_ARM_LENGTH*UPPER_ARM_LENGTH+LOWER_ARM_LENGTH*LOWER_ARM_LENGTH-SWEEP_ZONE_LENGTH*SWEEP_ZONE_LENGTH)/
    (2*UPPER_ARM_LENGTH*LOWER_ARM_LENGTH)
    )* (180/pi)
#Acctuation     
A_1_RANGE = 185
A_1_OFFSET = A_1_REST_ANGLE
A_3_REST_HEIGHT = 5
# Pre-calculate angle values
A_2_MIN_REST_ANGLE = 180 - 2 * A_1_REST_ANGLE
if A_1_OFFSET > A_1_REST_ANGLE:
    print(
        f"RobotController Warning: Rest angle {A_1_REST_ANGLE} degrees cannot be reached "
        f"by joint offset by {A_1_OFFSET} degrees. RobotControllers may fail."
    )
if ((360 - A_1_PREDEPLOY_ANGLE) - A_1_OFFSET) > A_1_RANGE:
    print(
        "RobotController Warning: Current a1 setup does not allow prepairing to deploy "
        "to the right. RobotControllers may fail."
    )
#Define States
UNKNOWN = 0
RESTING = 1
FULLY_RETRACTED = 2
PARTIALLY_RETRACTED = 3
DEPLOYED = 4

#Max size of log list
MAX_LOG_SIZE = 20


class RobotControllerBase:
    """Interface for interacting with robot pheripherals"""
    def __init__(self, a_1_pin=15, a_2_pin=14, a_3_motor_pins=(17, 27, 22, 19), a_3_sensor_pins=(23, 24), test = False):
        #Setup IO
        self.a_1 = ServoDriver( #Acctuation for rotational joint extending end effector to pot
            control_pin = a_1_pin,
            angle_range = (A_1_REST_ANGLE,A_1_REST_ANGLE+A_1_RANGE),
            signal_range = (0.00038, 0.00216),
            max_speed = 10
        )
        self.a_2 = ServoDriver( #Acctuation for rotational joint pointing end effector towards section
            control_pin = a_2_pin,
            angle_range = (0,200),
            signal_range = (554/1000000,2500/1000000),
            max_speed = 10
        )
        if test:
            self.a_3 = DummyDriver()
        else:
            self.a_3 = PrismaticDriver( ##Acctuation for prismatic joint controling end effector elivation
                motor_pins = a_3_motor_pins,
                sensor_pins = a_3_sensor_pins,
                position_range = (A_3_REST_HEIGHT,UPPER_ALLOWANCE+FIRST_LAYER_HEIGHT+INTER_LAYER_HEIGHT*(NUM_LAYERS-1))
            )
        self.arduino = ArduinoDriver(9600,2)
        self.led_controller = StripControl(3,3)
        self.targeted_angle = 0
        self.targeted_layer = 0
        self.last_deploy = 0
        self.last_layer = 0
        self.state = UNKNOWN
        self.log = []
        self.reset()
    def add_to_log(self):
        self.log.append(self.state)
        if len(self.log) > MAX_LOG_SIZE:
            self.log = self.log[1:]
    def reset(self):
        if self.state == UNKNOWN:
            self.a_2.set_angle(180)
            self.a_1.set_angle(A_1_REST_ANGLE)
            self.a_2.wait_to_complete()
            self.a_1.wait_to_complete()
        elif self.state not in [RESTING, FULLY_RETRACTED]:
            self.fully_retract()
        self.a_3.set_position(A_3_REST_HEIGHT)
        self.last_layer = -1
        self.state = RESTING
        self.add_to_log()
    def move_layer(self):
        if self.last_layer == self.targeted_layer:
            return
        if self.state == UNKNOWN:
            self.reset()
        if self.state not in [RESTING, FULLY_RETRACTED]:
            self.fully_retract()
        
        self.a_3.set_position(self.layer_height())

        self.last_layer = self.targeted_layer
        self.state = FULLY_RETRACTED
        self.add_to_log()
    def target_angle(self, angle=None):
        self.move_layer()
        if angle is None:
            angle = self.targeted_angle

        if self.state == DEPLOYED:
            self.partially_retract()
        elif self.state not in [PARTIALLY_RETRACTED, FULLY_RETRACTED]:
            self.move_layer()

        a_1_angle, a_2_angle = get_targeting_angles(angle)
        self.a_1.set_angle(a_1_angle)
        self.a_2.set_angle(a_2_angle)
        self.a_1.wait_to_complete()
        self.a_2.wait_to_complete()

        self.state = PARTIALLY_RETRACTED
        self.add_to_log()
    def deploy(self):
        if self.state == DEPLOYED and self.a_2.latest_angle == self.targeted_angle and self.last_layer == self.targeted_layer:
            print("skipped")
            return
        self.target_angle()

        self.a_1.set_angle(180,2000)
        self.a_2.set_angle(self.targeted_angle,2000)
        self.a_1.wait_to_complete()
        self.a_2.wait_to_complete()
        self.last_deploy = self.targeted_angle
        self.state = DEPLOYED
        self.add_to_log()
    def water(self, amount=0):
        self.deploy()
        self.led_controller.watering(amount)
        self.add_to_log()
        #TODO: add code to water plants here
    def brush(self, section):
        angle = ((section-0.3)*180/NUM_SECTIONS) + BRUSH_ANGLE
        self.set_target_angle(angle+(BRUSH_SIZE-1))
        self.target_angle()
        self.a_3.set_position(FIRST_LAYER_HEIGHT + INTER_LAYER_HEIGHT * self.last_layer + BRUSH_HEIGHT)
        self.deploy()
        self.a_3.set_position(FIRST_LAYER_HEIGHT + INTER_LAYER_HEIGHT * self.last_layer)
        self.a_2.set_angle(angle-(BRUSH_SIZE+1),500)
        self.a_2.wait_to_complete()
        self.a_3.set_position(FIRST_LAYER_HEIGHT + INTER_LAYER_HEIGHT * self.last_layer + BRUSH_HEIGHT)
        self.a_2.set_angle(angle-(BRUSH_SIZE-1),500)
        self.a_2.wait_to_complete()
        self.a_3.set_position(FIRST_LAYER_HEIGHT + INTER_LAYER_HEIGHT * self.last_layer)
        self.partially_retract()
    def target_brush(self, layer, section, brush=0):
        self.targeted_layer = layer
        # Position of watering
        if brush==0:
            self.set_target_angle((section + 1) * (180/NUM_SECTIONS) - BRUSH_ANGLE)
        elif brush==1:
            self.set_target_angle((section + 1) * (180/NUM_SECTIONS) - BRUSH_ANGLE - BRUSH_SIZE)
        self.deploy()
    def measure(self):
        self.deploy()
        self.a_3.set_position(self.layer_height() - SENSOR_LENGTH)
        time.sleep(10)
        #Get result somehow
        result = self.arduino.read_moisture_value()
        self.a_3.set_position(self.layer_height())
        time.sleep(5)
        after_moisture = self.arduino.read_moisture_value()
        if after_moisture < 350:
            self.brush(1)
        self.add_to_log()
        return result

    def partially_retract (self):
        if self.state == PARTIALLY_RETRACTED:
            return
        if self.state != DEPLOYED:
            print(
                "RobotController Warning: You probably don't want to be calling "
                "partially_retract from any state other than deployed."
                )
            self.deploy()
        a_1_angle, a_2_angle = get_targeting_angles(self.last_deploy)
        self.a_1.set_angle(a_1_angle,2000)
        self.a_2.set_angle(a_2_angle,2000)
        self.a_1.wait_to_complete()
        self.a_2.wait_to_complete()

        self.state = PARTIALLY_RETRACTED
        self.add_to_log()
    def fully_retract(self):
        if self.state == FULLY_RETRACTED:
            return
        if self.state == DEPLOYED:
            self.partially_retract()
        elif self.state != PARTIALLY_RETRACTED:
            print(
                "RobotController Warning: You probably don't want to be calling "
                "fully_retract from the resting or unknown state."
                )
            self.target_angle()

        if self.a_2.latest_angle < A_2_MIN_REST_ANGLE:
            self.a_2.set_angle(A_2_MIN_REST_ANGLE, wait=True)

        self.a_1.set_angle(A_1_REST_ANGLE, wait=True)

        self.state = FULLY_RETRACTED
        self.add_to_log()
    def power_down(self):
        if self.state != RESTING:
            self.reset()
        self.add_to_log()
        #TODO: Implement powering down servos
    def set_target_angle(self, angle):
        self.targeted_angle = angle
    def set_target_layer(self, layer):
        self.targeted_layer = layer
    def layer_height(self):
        return FIRST_LAYER_HEIGHT + INTER_LAYER_HEIGHT * self.targeted_layer
    def close(self):
        """Safely terminate IO"""
        self.a_1.close()
        self.a_2.close()
        self.a_3.close()




def get_targeting_angles(target):
    if target <= 180:
        a_1_angle = A_1_PREDEPLOY_ANGLE
        a_2_angle = target + A_2_MIN_REST_ANGLE
    else:
        a_1_angle = 360 - A_1_PREDEPLOY_ANGLE
        a_2_angle = target - A_2_MIN_REST_ANGLE
    return a_1_angle, a_2_angle
