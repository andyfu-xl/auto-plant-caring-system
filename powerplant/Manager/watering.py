from os import statvfs_result
from datetime import datetime, timedelta
from random import randrange

from ..control.robot_controller_base import NUM_SECTIONS
#from ..state import plant_pot

WATER_FLOW_RATE = 15 # ml/s

MOISTURE_DISPERSAL_TIME = 3

TOP_MOISTURE = 250

SECTOR_VOLUME = 14646 # Unit: ml

SOIL_INFO = {
    'sandy_chalky' : {
        'reading' : [353, 324, 301, 276, 266, 263],
        'threshold' : [379, 262]
    },
    'houseplants' : {
        'reading' : [350, 333, 332, 328, 325, 320],
        'threshold': [370, 319]
    },
    'ericaceous' : {
        'reading' : [350, 310, 292, 273, 260, 260],
        'threshold': [378, 259]
    },
    'multi_purpose': {
        'reading': [342, 322, 300, 278, 265, 263],
        'threshold': [375, 262]
    }
}


class Watering:
    def __init__(self, controller, state):
        self.controller = controller
        self.state = statvfs_result
    # soil_type: String, name of the soil
    # current: the reading of moisture sensor, in Ohm (volume of water / volume of soil)
    # target: target moisture level, in ml (volume of water / volume of soil)
    def amount_to_water(self,soil_type, current, target):
        readings = SOIL_INFO[soil_type]['reading']
        percentage = -1
        # we don't drown plants when the soil is extremely dry, just water a regular amount
        if current >= readings[0]:
            return target
        for i in range(1, len(readings)):
            if readings[i-1] > current > readings[i]:
                # 0.025 is the bucket, 4ml/160ml, due to lack of container in my room, 160ml of soil, 4ml of water.
                # assume reading vs. volume is linear in each bucket (two readings), this is similar as linear regression.
                # for example, 4ml -> 370, 8ml -> 350, then a reading of 360 is 6ml
                percentage = 0.025 * (i  + ((readings[i-1] - current) / (readings[i-1] - readings[i])))
                percentage -= target/100
        # soil is saturated, we don't water it anymore.
        if percentage <= 0:
            return 0
        else:
            sector_volume = SECTOR_VOLUME
            return  sector_volume * percentage

    def attempt_water_pot(self,pot):
        layer = pot.layer
        section = pot.section
        angle_offset =  randrange(-5,5)
        soil_saturation = self.controller.measure_at(pot.layer, pot.section, angle_offset)
        pot.update_moisture(soil_saturation)
        threshold = SOIL_INFO[pot.soil_type]['threshold']
        # TODO set soil in the interface
        # TOP_MOISTURE is resistance, smaller means more wet.
        volume = self.amount_to_water(pot.soil_type ,soil_saturation, pot.target_water_volume)*20
        if soil_saturation <= threshold[1]:
            pot.set_water_interval(interval=MOISTURE_DISPERSAL_TIME)
        elif soil_saturation <= threshold[0]:
            self.controller.water_at( layer, section, volume/WATER_FLOW_RATE, angle_offset)
            pot.set_water_interval()
        else:
            self.controller.water_at(layer, section, volume/WATER_FLOW_RATE, angle_offset)
            pot.set_water_interval(interval=MOISTURE_DISPERSAL_TIME)
        pot.mark_watered()

    def check_for_actions(self, pots):
        now = datetime.now()
        for each_pot in [p_ for p in pots for p_ in p]:
            if each_pot.needs_watering(now):
                print("Attempting watering")
                self.attempt_water_pot(each_pot)
        self.controller.reset()
