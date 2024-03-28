import datetime

class PlantPot:
    """Data for segment of robot containing one speciese of plant"""
    def __init__(self, layer, section, database_interface):
        self.database_interface = database_interface
        self.layer = layer
        self.section = section
        self.plant_type = None
        self.soil_type = None
        self.default_water_interval = None
        self.water_interval = None
        self.target_water_volume = None
        self.min_soil_moist = None
        self.max_soil_moist = None
        self.min_light_lux = None
        self.last_moisture = None
        self.next_water = None
    def set_plant(self,plant_type):
        """Mark that a new plant is in the pot"""
        self.plant_type = plant_type
        self.soil_type = None
    def set_water_interval(self,interval=None):
        """Set the water interval for the pot"""
        if interval is None:
            self.water_interval = self.default_water_interval
        else:
            self.water_interval = interval
        self.set_next_water(datetime.datetime.now() + datetime.timedelta(hours=self.water_interval))
        self.database_interface.update_next_moisture_event(self.layer,self.section,self.next_water)
    def mark_watered(self):
        """Mark that the pot has been watered"""
        now = datetime.datetime.now()
        self.last_watered = now
        self.database_interface.update_watered_info_remote(self.layer,self.section,now)
    def update_moisture(self,moisture):
        """Update the moisture level of the pot"""
        self.last_moisture = moisture
        self.database_interface.update_moisture_info_remote(self.layer,self.section,datetime.datetime.now(),moisture)
    def set_next_water(self,next_water_time, update_database=True):
        """Set the next watering time"""    
        self.next_water = datetime.datetime.fromtimestamp(next_water_time.timestamp())
        if update_database:
            self.database_interface.update_next_moisture_event(self.layer,self.section,self.next_water)
    def needs_watering(self, time):
        """Get if the plant is due watering"""
        if (not self.plant_type) or (not self.next_water):
            return False
        #print(f"Time now: {time}, Next watering: {self.next_water}")
        return time >= self.next_water
        
