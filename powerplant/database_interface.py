from heapq import merge
import os
import json
import firebase_admin
import threading
from datetime import datetime, timezone
import time
from firebase_admin import credentials
from firebase_admin import firestore


DATA_PATH = os.path.join(os.getcwd(), 'data')#Path to store a local back up of data
LAYER_ONE = 0 # Represent the first layer of shelf
LAYER_TWO = 1 # Represent the second layer of shelf
class DatabaseInterface():
    """Interfaces to let the robot interact with the firestore database"""
    def __init__(self, cred = 'testkey.json', machine_id = None):
        """Initialize a database interface client with a given machine id and a generated credential for each robot"""
        #Use the default credential here to access the database
        self.cred = cred
        #The unique ID of each robot
        self.machine_id = machine_id
        #The threading event for listening realtime updates from the database
        self.callback_done = threading.Event()
        #Initialize the client by the given credential
        certificate = credentials.Certificate(os.path.join(os.getcwd(), 'cred', self.cred))
        firebase_admin.initialize_app(certificate)
        self.db = firestore.client()
        self.changed = False

    # @staticmethod
    # def gen_key():
    #     pass

    # Remote firestore database interfaces
    def initialize_planter_remote(self):
        """Initialize the planter data in the database for the robot with the given unique machine id"""
        if self.db is None:
            raise Exception("Database client not initialised")
        planter_ref = self.db.collection('planters').document(self.machine_id)
        planter_del = planter_ref.delete()
        planter_ref.set({"name": ""})
        time.sleep(10)
        # planter = planter_ref.get()
        # # Initialize the planter data as a dictionary
        # planter = {"id":self.machine_id,
        #             "led_on":False,
        #             "last_measurement":{"slot_1":{'time':None, 'moisture':None}, "slot_2":{'time':None, 'moisture':None},
        #                 "slot_3":{'time':None, 'moisture':None},"slot_4":{'time':None, 'moisture':None},
        #                 "slot_5":{'time':None, 'moisture':None}, "slot_6":{'time':None, 'moisture':None}},
        #             "last_set_at":{"slot_1":None, "slot_2":None, "slot_3":None,
        #                 "slot_4":None, "slot_5":None, "slot_6":None},
        #             "last_watered_at":{"slot_1":None, "slot_2":None, "slot_3":None,
        #                 "slot_4":None, "slot_5":None, "slot_6":None},
        #             "plants":{"slot_1":None, "slot_2":None, "slot_3":None,
        #                 "slot_1":None, "slot_5":None, "slot_6":None},
        #             "soil":{"slot_1":None, "slot_2": None, "slot_3": None,
        #                     "slot_4": None, "slot_5":None, "slot_6":None}}
        # planter_ref.set(planter)

    def usr_plant_change_listener(self, plant_pots, arduino_driver):
        """Start the listener for real time data update from the database and
        write over the local data, if there is change in database, the method
        would see if it is the change of plants. If it is, the plant_pot array
        parameter will be updated by that changed plant pot. The method returns
        a watcher object, if you want to finish the listener process, the
        watcher object has a method "unscubcribe() to
        terminate the process
        """
        if self.db is None:
            raise Exception("Database client not initialised")
        def on_snapshot(col_snapshot, changes, _ ):
            for doc in col_snapshot:
                planter = doc.to_dict()
                # Check whether plants are changed, if changed, update it to the database version
                for key in planter["plants"]:
                    if (key > "slot_6"):
                        continue
                    layer, slot = self.__class__.to_layer_and_slot(key)
                    
                    if plant_pots[layer][slot].plant_type != planter["plants"][key]:
                        if planter["plants"][key] is None:#
                            if layer == 0:
                                arduino_driver.turn_off_LED(slot)
                        else:
                            plant_pots[layer][slot].set_plant(planter["plants"][key])
                            plant_pots[layer][slot].last_watered = None
                            # todo add water volume and interval
                            pot_fields = self.get_plant_params(planter["plants"][key])
                            plant_pots[layer][slot].min_soil_moist = pot_fields['min_moist']
                            plant_pots[layer][slot].max_soil_moist = pot_fields['max_moist']
                            plant_pots[layer][slot].min_light_lux = pot_fields['min_lux']
                            plant_pots[layer][slot].default_water_interval = pot_fields['water_interval']
                            plant_pots[layer][slot].target_water_volume = pot_fields['target_water_volume']
                            plant_pots[layer][slot].soil_type = planter['soil_type'][key]
                            try:
                                if pot_fields['min_lux'] > 2000 and layer == 0:
                                    arduino_driver.turn_on_LED(slot)
                                elif pot_fields['min_lux'] <= 2000 and layer == 0:
                                    arduino_driver.turn_off_LED(slot)
                            except:
                                print("Arduino not connected")
                

                    if (not planter["next_check_moisture"][key] is None) and (not plant_pots[layer][slot].next_water ==  planter["next_check_moisture"][key]):
                        plant_pots[layer][slot].set_next_water(planter["next_check_moisture"][key],False)
                        print(f"Next water time: {plant_pots[layer][slot].next_water}")


                # Wirte to the local database
                jstring = json.dumps(planter, indent=2, default=self.json_serial)
                # file_path = os.path.join(DATA_PATH, "planter.json")
                # with open(file_path, 'w', encoding='utf-8') as file:
                #     file.write(jstring)
                print(f"Robot ID: {doc.id}")
            self.callback_done.set()
        planter_ref = self.db.collection('planters').document(self.machine_id)
        planter_watch = planter_ref.on_snapshot(on_snapshot)
        print("Reach the end")
        return planter_watch

    def get_plant_params(self, plant_name):
        """Given plant name, return the minimum soil moisture and maximum soil moisture from the plants database"""
        plant_ref = self.db.collection('plants').document(plant_name)
        plant = plant_ref.get()
        pot_fields = {}
        if plant.exists:
            pot_fields['min_moist'] = plant.get("parameter")["min_soil_moist"]
            pot_fields['max_moist'] = plant.get("parameter")["max_soil_moist"]
            pot_fields['min_lux'] = plant.get("parameter")["min_light_lux"]
            pot_fields['water_interval'] = plant.get("parameter")["water_interval"]
            pot_fields['target_water_volume'] = plant.get("parameter")["target_water_volume"]
            return pot_fields

    def update_moisture_info_remote(self, layer, slot, last_measured_time, moisture):
        """Method for update most recent moisture info and measurement time to the remote database"""
        if self.db is None:
            raise Exception("Database client not initialised")
        slot_string = self.__class__.to_slot_string(layer, slot)
        last_measured_time = last_measured_time.astimezone(tz=timezone.utc)
        planter_ref = self.db.collection('planters').document(self.machine_id)
        dict = {"timestamp":last_measured_time, "type":"check_moisture", "slot": layer*3+slot+1, "value":moisture}
        planter_ref.update({f"last_event.{slot_string}.check_moisture.at":last_measured_time,
                            f"last_event.{slot_string}.check_moisture.value":moisture,
                            f"completed_events":firestore.ArrayUnion([dict])})

    def update_watered_info_remote(self, layer, slot, last_watered_time):
        """Method for update most recent watering information to the remote database"""
        if self.db is None:
            raise Exception("Database client not initialised")
        slot_string = self.__class__.to_slot_string(layer, slot)
        last_watered_time = last_watered_time.astimezone(tz=timezone.utc)
        planter_ref = self.db.collection('planters').document(self.machine_id)
        dict = {"timestamp":last_watered_time, "type":"watered", "slot": layer*3+slot+1}
        planter_ref.update({f"last_event.{slot_string}.watered.at":last_watered_time,
                            f"completed_events":firestore.ArrayUnion([dict])})

    def update_next_moisture_event(self, layer, section, next_measure_time):
        """Method for updating algorithm-determined measurement event"""
        if self.db is None:
            raise Exception("Database client not initialised")
        slot_string = self.__class__.to_slot_string(layer, section)
        next_measure_time = next_measure_time.astimezone(tz=timezone.utc)
        planter_ref = self.db.collection('planters').document(self.machine_id)
        planter_ref.update({f"next_check_moisture.{slot_string}":next_measure_time})

    def get_next_measure_time(self, layer, slot):
        if self.db is None:
            raise Exception("Database client not initialised")
        slot_string = self.__class__.to_slot_string(layer, slot)
        planter_ref = self.db.collection("planter").document(self.machine_id)
        return planter_ref.get("next_check_moisture")[slot_string]

    # Local database interfaces
    def initialize_planter_local(self):
        """Initialize the local back up data for the robot"""
        planter = {"id":self.machine_id,
                    "led_on":False,
                    "last_measurement":{"slot_one":{'time':None, 'moisture':None}, "slot_two":{'time':None, 'moisture':None},
                    "slot_three":{'time':None, 'moisture':None},"slot_four":{'time':None, 'moisture':None},
                    "slot_five":{'time':None, 'moisture':None}, "slot_six":{'time':None, 'moisture':None}},
                    "last_set_at":{"slot_one":None, "slot_two":None, "slot_three":None,
                        "slot_four":None, "slot_five":None, "slot_six":None},
                    "last_watered_at":{"slot_one":None, "slot_two":None, "slot_three":None,
                        "slot_four":None, "slot_five":None, "slot_six":None},
                    "plants":{"slot_one":None, "slot_two":None, "slot_three":None,
                        "slot_four":None, "slot_five":None, "slot_six":None}}
        file_path = os.path.join(DATA_PATH, 'planter.json')
        with open(file_path, 'w', encoding= 'utf-8') as file:
            file.write(json.dumps(planter, indent=2, default=self.json_serial))

    def update_moisture_info_local(self,layer, slot, last_measured_time, moisture):
        """Update the measurement info (most recent measured time and moisture for the given section)
         to the local back up"""
        # Load the local data
        file_path = os.path.join(DATA_PATH, 'planter.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            layer_string = self.__class__.to_slot_string(layer, slot)
            json_string = file.read()
        planter = json.loads(json_string)
        # Upadate data locally
        planter["last_measurement"][layer_string]["time"] = last_measured_time
        planter["last_measurement"][layer_string]["moisture"] = moisture
        # Overwrite the local data(Update)
        with open(file_path, 'w', encoding = 'utf-8') as file:
            json_string = json.dumps(planter, indent=2, default=self.json_serial)
            file.write(json_string)

    def update_watered_info_local(self, layer,slot, last_watered_time):
        """Update the watering info for the given section to the local backup"""
        # Load the local data
        file_path = os.path.join(DATA_PATH, 'planter.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            layer_string = self.__class__.to_slot_string(layer, slot)
            json_string = file.read()
        planter = json.loads(json_string)
        # Upadate data locally
        planter["last_watered_at"][layer_string] = last_watered_time
        # Overwrite the local data(Update)
        with open(file_path, 'w', encoding = 'utf-8') as file:
            json_string = json.dumps(planter, indent=2, default=self.json_serial)
            file.write(json_string)
    

    def json_serial(self,obj):
        """JSON serializer for datetime object"""
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S.%f') + 'Z'
        if not obj:
            return None
        else:
            raise TypeError(f"Type {type(obj)} is not serializable")

    @staticmethod
    def to_slot_string(layer, slot):
        """Convert the layer and slot number into corresponding query string when finding slots in the database"""
        if layer == LAYER_ONE:
            if slot == 0:
                slot_string = 'slot_1'
            elif slot == 1:
                slot_string = 'slot_2'
            elif slot == 2:
                slot_string = 'slot_3'
            else:
                raise ValueError("Invalid slot input.")
        elif layer == LAYER_TWO:
            if slot == 0:
                slot_string = 'slot_4'
            elif slot == 1:
                slot_string = 'slot_5'
            elif slot == 2:
                slot_string = 'slot_6'
            else:
                raise ValueError("Invalid slot input.")
        else:
            raise ValueError("Invalid layer input.")
        return slot_string

    @staticmethod
    def to_layer_and_slot(lay_string):
        """Convert a layer string to its corresponding layer and slot index"""
        if lay_string == 'slot_1':
            location = (0,0)
        elif lay_string == 'slot_2':
            location = (0,1)
        elif lay_string == 'slot_3':
            location = (0,2)
        elif lay_string == 'slot_4':
            location = (1,0)
        elif lay_string == 'slot_5':
            location = (1,1)
        elif lay_string == 'slot_6':
            location = (1,2)
        else:
            raise ValueError("Invalid slot input")
        return location
