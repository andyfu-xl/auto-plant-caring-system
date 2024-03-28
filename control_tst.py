from powerplant.control.servo_driver import ServoDriver

from gpiozero import Device
from gpiozero.pins.pigpio import PiGPIOFactory

Device.pin_factory = PiGPIOFactory()

def main():
    """Entry point function for robot software"""
    speed_mod = 10 # >= 1
    pin2 = ServoDriver(2,(0,201),(554/1000000,2500/1000000))
    pin2.set_angle(0,500)
    pin3 = ServoDriver(3,(0,201),(554/1000000,2500/1000000))
    pin3.set_angle(0,500)
    pin2.wait_to_complete()
    pin3.wait_to_complete()
    pin2.set_angle(180,500*speed_mod)
    pin2.wait_to_complete()
    pin3.set_angle(180,500*speed_mod)
    pin3.wait_to_complete()
    pin2.set_angle(0,1000*speed_mod)
    pin3.set_angle(201,500*speed_mod)
    pin3.set_angle(0,500*speed_mod)
    pin2.wait_to_complete()
    pin3.wait_to_complete()

if __name__ == "__main__":
    main()
