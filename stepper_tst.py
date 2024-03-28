from powerplant.control.stepper_driver import StepperDriver

from gpiozero import Device
from gpiozero.pins.pigpio import PiGPIOFactory

Device.pin_factory = PiGPIOFactory()

motor = StepperDriver((17,27,22,19))
motor.turn(16)
motor.turn(-16)