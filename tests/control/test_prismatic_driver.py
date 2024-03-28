# import pytest
# from .. import source_src
# from RPi import GPIO
# import powerplant.control.prismatic_driver as pd
#
# source_src.source()
#
#
# @pytest.fixture
# def prismatic_driver():
#     driver = pd.PrismaticDriver(
#         2,
#         3,
#         (0, 60),
#         0.3
#     )
#     return driver
#
#
# @pytest.mark.timeout(20)
# def test_get_distance(prismatic_driver):
#     """Check driver reads distance as expected"""
#     assert prismatic_driver.get_distance() == 20
#     GPIO.cleanup()
#
#
# @pytest.mark.timeout(20)
# def test_get_distance_to_target(prismatic_driver):
#     """Check driver calculates the displacement to destination as expected"""
#     assert prismatic_driver.get_distance_to_target() == -20
#     GPIO.cleanup()
#
#
# @pytest.mark.timeout(20)
# def test_close_to_destination(prismatic_driver):
#     """Check driver does not attempt actions when it is close to the destination"""
#     destination = prismatic_driver.destination
#     assert prismatic_driver.set_position(prismatic_driver.get_distance()) == 1
#     prismatic_driver.destination = destination
#     GPIO.cleanup()
#
#
# @pytest.mark.timeout(20)
# def test_timeout(prismatic_driver):
#     """Check driver throws timeout exception, it takes 5 seconds to throw an exception"""
#     with pytest.raises(TimeoutError) as e:
#         assert prismatic_driver.set_position(55) == 0
#     assert str(e.value) == 'The program runs too long'
#     GPIO.cleanup()
#
#
# @pytest.mark.timeout(20)
# def test_invalid_target_max(prismatic_driver):
#     """Check driver not attempt to move to an unreachable destination"""
#     with pytest.raises(ValueError) as e:
#         assert prismatic_driver.set_position(999) == 0
#     assert str(e.value) == 'invalid target position'
#     GPIO.cleanup()
#
#
# @pytest.mark.timeout(20)
# def test_invalid_target_min(prismatic_driver):
#     """Check driver not attempt to move to an unreachable destination """
#     with pytest.raises(ValueError) as e:
#         assert prismatic_driver.set_position(-999) == 0
#     assert str(e.value) == 'invalid target position'
#     GPIO.cleanup()
