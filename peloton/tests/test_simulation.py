from peloton.common.math import is_equal
from peloton.conf.settings import sim_config
from peloton.models.bolid import Car
from peloton.models.simulation import RaceCar
from peloton.models.track import Sector


def test_max_speed_straight(car_all_100: Car, straight_200: Sector):
    race_car = RaceCar(car=car_all_100, speed=0.0)
    assert race_car.max_speed(straight_200) == car_all_100.max_speed


def test_max_speed_for_curvatures(
        car_all_100: Car, low_curve_180: Sector, semi_curve_180: Sector, high_curve_180: Sector, max_curve_180: Sector
):
    race_car = RaceCar(car=car_all_100, speed=0.0)
    assert is_equal(race_car.max_speed(low_curve_180), 72.0)
    assert is_equal(race_car.max_speed(semi_curve_180), 52.0)
    assert is_equal(race_car.max_speed(high_curve_180), 40.0)
    assert is_equal(race_car.max_speed(max_curve_180), sim_config.slowest_curve_speed)
