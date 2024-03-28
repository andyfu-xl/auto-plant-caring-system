import pytest
from .. import test_setup

from powerplant.control.robot_controller_base import RobotControllerBase, UNKNOWN, RESTING, FULLY_RETRACTED, PARTIALLY_RETRACTED, DEPLOYED
import powerplant.control.prismatic_driver as pd

@pytest.fixture
def controller():
    controller = RobotControllerBase(
        15,
        14,
        (17,27,22,19),
        (24,18),
        test = True
    )
    return controller

@pytest.mark.timeout(10)
def test_initial_state(controller):
    """Check that the initial state is resting"""
    controller.close()
    assert controller.state == RESTING
    assert len(controller.log) == 1
    assert controller.log[0] == RESTING

@pytest.mark.timeout(10)
def test_initial_position(controller):
    """Check that the initial position is 0"""
    controller.close()
    assert controller.targeted_angle == 0
    assert controller.targeted_layer == 0

# Move layer

@pytest.mark.timeout(10)
def test_initial_move_layer(controller):
    """Check move_layer can align from resting"""
    controller.move_layer()
    controller.close()
    assert controller.state == FULLY_RETRACTED
    assert len(controller.log) == 2
    assert controller.log == [RESTING, FULLY_RETRACTED]

@pytest.mark.timeout(10)
def test_move_up_layer(controller):
    """Check move_layer can move up a layer"""
    controller.set_target_layer(1)
    controller.move_layer()
    controller.close()
    assert controller.state == FULLY_RETRACTED
    assert len(controller.log) == 2
    assert controller.log == [RESTING, FULLY_RETRACTED]

@pytest.mark.timeout(10)
def test_move_down_layer(controller):
    """Check move_layer can move down a layer"""
    controller.set_target_layer(1)
    controller.move_layer()
    controller.set_target_layer(0)
    controller.move_layer()
    controller.close()
    assert controller.state == FULLY_RETRACTED
    assert len(controller.log) == 3
    assert controller.log == [RESTING, FULLY_RETRACTED, FULLY_RETRACTED]

@pytest.mark.timeout(10)
def test_move_layer_from_unknown(controller):
    """Check move_layer can move from unknown state"""
    controller.state = UNKNOWN
    controller.log = []
    controller.set_target_layer(1)
    controller.move_layer()
    controller.close()
    assert controller.state == FULLY_RETRACTED
    assert len(controller.log) == 2
    assert controller.log == [RESTING, FULLY_RETRACTED]

@pytest.mark.timeout(20)
def test_move_layer_from_deployed(controller):
    """Check move_layer can move from deployed state"""
    controller.deploy()
    controller.log = []
    controller.set_target_layer(1)
    controller.move_layer()
    controller.close()
    assert controller.state == FULLY_RETRACTED
    assert len(controller.log) == 3
    assert controller.log == [PARTIALLY_RETRACTED, FULLY_RETRACTED, FULLY_RETRACTED]
