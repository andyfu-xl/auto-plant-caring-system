
from .robot_controller_base import RobotControllerBase, NUM_SECTIONS

class RobotController(RobotControllerBase):
    def target_pos(self,layer,section, offset):
        self.set_target_layer(layer)
        angle = (section +0.5) * 180/NUM_SECTIONS + offset
        self.set_target_angle(angle)
    def water_at(self,layer,section, water_amount, offset=0):
        self.target_pos(layer,section, offset)
        self.water(water_amount)
    def measure_at(self,layer,section, offset=0):
        self.target_pos(layer,section, offset)
        return self.measure()
