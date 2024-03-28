from .plant_pot import PlantPot

NUM_LAYERS = 2 #TODO: confirm this value (const should possibly be refactored to be stored elswhere)
NUM_SECTIONS = 3 #TODO: confirm this value (const should possibly be refactored to be stored elswhere)

class RobotState:
    """Internal state of robot"""
    def __init__(self, database_interface, driver):
        self.database_interface = database_interface
        self.pots = [[PlantPot(layer,section, database_interface) for section in range(NUM_SECTIONS)]for layer in range(NUM_LAYERS)]
        self.database_interface.usr_plant_change_listener(self.pots, driver)
    def get_pot(self,layer,section):
        """Get the plant pot at the given layer and layer subsection"""
        return self.pots[layer,section]
