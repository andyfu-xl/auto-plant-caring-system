import pytest

import powerplant.Manager.robot_manager as rm
import powerplant.state.robot_state as rs

#Test RobotManager functionality

@pytest.fixture
def inited_manager():
    """New initilised RobotManager"""
    state = rs.RobotState()
    manager = rm.RobotManager(state)
    return manager

def test_inits_stopped(inited_manager):
    """Check manager initilises stopped"""
    assert inited_manager.stop() == 0

@pytest.mark.timeout(3000)
def test_starts_after_init(inited_manager):
    """Check manager can start"""
    start_result = inited_manager.start()
    inited_manager.stop()
    assert start_result == 1

@pytest.mark.timeout(3000)
def test_stops_after_start(inited_manager):
    """Check managaer can stop"""
    inited_manager.start()
    assert inited_manager.stop() == 1

#Test multithreading for RobotManagerThread

@pytest.fixture
def manager_thread():
    """Create a RobotManagerThread"""
    state = rs.RobotState()
    manager_thread = rm.RobotManagerThread(state)
    return manager_thread

@pytest.mark.timeout(3000)
def test_robot_manager_thread_starts(manager_thread):
    """Check that thread starts"""
    manager_thread.start()
    assert manager_thread.is_alive()
    manager_thread.stop()
    manager_thread.join()

@pytest.mark.timeout(3000)
def test_robot_manager_stops(manager_thread):
    """Check that thread stops gracefully"""
    manager_thread.start()
    manager_thread.stop()
    manager_thread.join()
    assert not manager_thread.is_alive()
