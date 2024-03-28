import pytest
from datetime import datetime, timedelta
from .. import test_setup

import powerplant.state.plant_pot as pp

plant_type = {
        "id":49,
        "water_interval": timedelta(hours=1),
        "water_amount":10
    }

@pytest.fixture
def pot():
    """New pot with the example plant type"""
    pot = pp.PlantPot()
    pot.set_plant(plant_type)
    return pot

def test_set_plant_sets(pot):
    """Check that setting a new plant stores the infor for that plant"""
    assert pot.plant_type == plant_type

#TODO: How this should be handled needs to be disscussed
def test_set_plant_last_watered():
    """Check that setting a new plant modifies the last watered property correctly"""

@pytest.fixture
def watered_pot(pot):
    """New pot that was watered on 8/2/22 at 10am"""
    last_watered = datetime(2022,2,8,10,00,0)
    pot.mark_watered(last_watered)
    return pot

def test_mark_watered(watered_pot):
    """Check that marking the pot as watered records the current time of watering"""
    assert watered_pot.last_watered == datetime(2022,2,8,10,00,0)

def test_needs_watering_early(watered_pot):
    """Check that pot does not report as needing watering before watering interval has elapsed"""
    now = datetime(2022,2,8,10,45,30)
    assert not watered_pot.needs_watering(now)

def test_needs_watering_later(watered_pot):
    """Check that pot does not report as needing watering before watering interval has elapsed"""
    now = datetime(2022,2,8,11,15,30)
    assert watered_pot.needs_watering(now)
