import math

from pytest import fixture

from peloton.models.bolid import Car
from peloton.models.track import Sector


@fixture()
def car_all_100():
    return Car(caption='100 car', max_acceleration=100.0, max_braking=100.0, max_speed=100.0)


@fixture()
def straight_200():
    return Sector(length=200.0, corner=0.0)


@fixture()
def max_curve_180():
    return Sector(length=5*math.pi, corner=180.0)


@fixture()
def max_curve_90():
    return Sector(length=(5/2)*math.pi, corner=90.0)


@fixture()
def max_curve_60():
    return Sector(length=(5/3)*math.pi, corner=60.0)


@fixture()
def semi_curve_180():
    return Sector(length=5*2*math.pi, corner=180.0)


@fixture()
def semi_curve_90():
    return Sector(length=5*math.pi, corner=90.0)


@fixture()
def semi_curve_30():
    return Sector(length=(5*2/6)*math.pi, corner=30.0)


@fixture()
def low_curve_180():
    return Sector(length=5*4*math.pi, corner=180.0)


@fixture()
def high_curve_180():
    return Sector(length=5*1.33333*math.pi, corner=180.0)
