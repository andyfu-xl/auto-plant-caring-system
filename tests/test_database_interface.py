from datetime import datetime
import time
from . import test_setup
import powerplant.database_interface as di
from powerplant.state.plant_pot import PlantPot
from powerplant.control.arduino_driver import ArduinoDriver
# Use known example data in the database to make tests

example_plant = {"id":2, "name":"Lily", "waterInterval":2000}
example_slot = {"id":1, "plant":{"name":"Fern"}, "assignedAt":"2022-02-14T16:59:30.147Z", "lastWateredAt": None}
initialized_di = di.DatabaseInterface(machine_id='test2planter')

def test_get_plant_params():
    """Check if get plant request to the database returns correct moist value"""
    plant_name = "anthurium_andraeanum_amis"
    pot_fields = initialized_di.get_plant_params(plant_name)
    assert pot_fields['min_moist'] == 15
    assert pot_fields['max_moist'] == 65
    assert pot_fields['min_lux'] == 1500
    assert pot_fields['target_water_volume'] == 12
    assert pot_fields['water_interval'] == 48

def test_litener_update():
    """check if local plant pot array update every time the plants field of planter data changes in database"""
    initialized_di.initialize_planter_remote()
    time.sleep(6)
    try:
        arduino_driver = ArduinoDriver(baudrate = 9600, timeout=1)
        arduino_driver.init_serial()
    except(Exception):
        print("Error to connect to arduino")
    plant_pots = [[PlantPot(i,j,initialized_di) for j in range(3)]for i in range(2)]
    watcher = initialized_di.usr_plant_change_listener(plant_pots,arduino_driver)
    start = time.time()
    
    while (time.time()-start <= 4):
        if time.time()-start == 1:
            planter_ref = initialized_di.db.collection("planters").document(initialized_di.machine_id)
            planter_ref.update({"plants.slot_1": "anthurium_andraeanum_amis",
                                "plants.slot_5": "anthurium_andraeanum_aramon"})
    watcher.unsubscribe()

    assert plant_pots[0][0].plant_type == "anthurium_andraeanum_amis"
    assert plant_pots[1][1].plant_type == "anthurium_andraeanum_aramon"
    assert plant_pots[0][0].max_soil_moist == 65
    assert plant_pots[0][0].min_soil_moist == 15
    assert plant_pots[0][0].min_light_lux == 1500
    assert plant_pots[0][0].default_water_interval == 48
    assert plant_pots[1][1].max_soil_moist == 65
    assert plant_pots[1][1].min_soil_moist == 15
    assert plant_pots[1][1].min_light_lux == 1500
    assert plant_pots[1][1].target_water_volume == 7

def test_update_moisture_info():
    """Check if the updated measurement info is correctly updated to the database"""
    now = datetime.now()
    initialized_di.update_moisture_info_remote(1,1, now,45)
    planter_ref = initialized_di.db.collection("planters").document(initialized_di.machine_id).get()
    measure_time = planter_ref.get("last_event")["slot_5"]["check_moisture"]["at"]
    moist = planter_ref.get("last_event")["slot_5"]["check_moisture"]["value"]
    assert datetime.fromtimestamp(measure_time.timestamp()) == now
    assert moist == 45

def test_update_water_info():
    """Check if updated watered info for a given slot is correctly updated to the database"""
    now = datetime.now()
    initialized_di.update_watered_info_remote(1,2, now)
    planter_ref = initialized_di.db.collection("planters").document(initialized_di.machine_id).get()
    watered_time = planter_ref.get("last_event")["slot_6"]["watered"]["at"]
    assert datetime.fromtimestamp(watered_time.timestamp()) == now


def test_next_measure_info():
    """Check if the decision of next measurement itme has been updated to the databse"""
    now = datetime.now()
    initialized_di.update_next_moisture_event(1,2, now)
    planter_ref = initialized_di.db.collection("planters").document(initialized_di.machine_id).get()
    next_time = planter_ref.get("next_check_moisture")["slot_6"]
    assert datetime.fromtimestamp(next_time.timestamp()) == now


def test_json_serial():
    """Check if the time string is converted to correct format YYYY-MM-DDTH:Min:Sec:Millisec"""
    correct = "2011-12-25T23:22:34.104567Z"
    to_be_tested_time = datetime(2011, 12, 25, 23, 22, 34, 104567)
    assert initialized_di.json_serial(to_be_tested_time) == correct
