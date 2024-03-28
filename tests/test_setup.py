import sys
import os

from gpiozero import Device
from gpiozero.pins.mock import MockFactory, MockPWMPin


#Source the powerplant module
#This is a hack but simpler that setting up virtual environments just for testing.
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../powerplant")

#Setup test pin environment
Device.pin_factory = MockFactory(pin_class=MockPWMPin)
