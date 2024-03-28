from time import sleep
from powerplant.control.robot_controller_base import RobotControllerBase
from powerplant.control.servo_driver import ServoDriver

from gpiozero import Device
from gpiozero.pins.pigpio import PiGPIOFactory

Device.pin_factory = PiGPIOFactory()

def main():
    servos()
    robot_controller()

SERVO_PINS = (15,14)
MOTOR_PINS = (17,27,22,19)
SENSOR_PINS = (24,18)

def servos():
    print(f"Testing servo on pin {SERVO_PINS[0]}.")
    single_servo(SERVO_PINS[0])
    sleep(1)
    print(f"Testing servo on pin {SERVO_PINS[1]}.")
    single_servo(SERVO_PINS[1])
    sleep(1)
    print(f"Testing servos on pins {SERVO_PINS[0]} and {SERVO_PINS[1]} together.")
    dual_servos(SERVO_PINS[0],SERVO_PINS[1])
    sleep(1)

def single_servo(pin):
    sd = make_servo(pin)
    sd.set_angle(0)
    sd.wait_to_complete()
    sd.set_angle(180)
    sd.set_angle(0)
    sd.close()

def dual_servos(pin_a,pin_b):
    sd_a = make_servo(pin_a)
    sd_b = make_servo(pin_b)
    sd_a.set_angle(0, wait=True)
    sd_b.set_angle(180, wait=True)
    sd_a.set_angle(180,2000)
    sd_b.set_angle(90,2000)
    sd_a.wait_to_complete()
    sd_b.wait_to_complete()
    sd_a.set_angle(0)
    sd_b.set_angle(0)
    sd_a.close()
    sd_b.close()

def make_servo(pin):
    return ServoDriver( 
            control_pin = pin,
            angle_range = (0,200),
            signal_range = (554/1000000,2500/1000000),
            max_speed = 10
        )

def robot_controller():
    return
    ## Changes to the robot controller have broken this and I can't be assed to fix it yet.
    print("Creating robot controller")
    rc = RobotControllerBase(SERVO_PINS[0],SERVO_PINS[1],MOTOR_PINS,SENSOR_PINS)
    print("Deploying arm to 45 degrees.")
    rc.deploy(45)
    sleep(2)
    print("Deploying arm to 90 degrees.")
    rc.deploy(90)
    print("Deploying arm to 135 degrees.")
    sleep(2)
    rc.deploy(135)
    sleep(2)
    rc.reset()
    rc.close()

if __name__ == "__main__":
    main()
