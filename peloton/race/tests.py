from django.test import TestCase

from car.models import Car
from peloton.testing.cases import BasicTestCase
from race.action import CarState, DecisionMaker
from track.const import DIRECTION
from track.models import Track, TrackSector


class RaceTestCase(BasicTestCase):
    def setUp(self):
        super().setUp()

        self.sector_1 = TrackSector.objects.create(
            track=self.track, sector_order=0, length=33.2, curve_radius=None, curve_direction=DIRECTION.LEFT
        )
        self.sector_2 =TrackSector.objects.create(
            track=self.track, sector_order=1, length=33.2, curve_radius=20.0, curve_direction=DIRECTION.LEFT
        )
        self.sector_3 =TrackSector.objects.create(
            track=self.track, sector_order=2, length=12.1, curve_radius=None, curve_direction=DIRECTION.LEFT
        )
        self.sector_4 =TrackSector.objects.create(
            track=self.track, sector_order=3, length=15.0, curve_radius=33, curve_direction=DIRECTION.RIGHT
        )

        self.track = Track.objects.get(pk=self.track.pk)
        self.car = Car(name='test_car')
        self.car.max_speed = 10.0


class TestCarState(RaceTestCase):
    def test_get_slower_sector(self):
        car_state = CarState(
            car=self.car, track=self.track, speed=9.0, acceleration=0.0, distance_from_start=30,
        )
        self.assertEqual(1, car_state.next_slower_sector.sector_order)

        car_state = CarState(
            car=self.car, track=self.track, speed=2.0, acceleration=0.0, distance_from_start=35,
        )
        self.assertEqual(None, car_state.next_slower_sector)

        car_state = CarState(
            car=self.car, track=self.track, speed=9.0, acceleration=0.0, distance_from_start=35,
        )
        self.assertEqual(3, car_state.next_slower_sector.sector_order)

        car_state = CarState(
            car=self.car, track=self.track, speed=9.0, acceleration=0.0,
            distance_from_start=self.track.length - 0.1,
        )
        self.assertEqual(1, car_state.next_slower_sector.sector_order)


class DecisionTestCase(RaceTestCase):
    def test_actions(self):
        car_state = CarState(
            car=self.car, track=self.track, speed=0.0, acceleration=0.0, distance_from_start=0.0,
        )
        self.assertFalse(DecisionMaker.need_brake(car_state))
        self.assertTrue(DecisionMaker.need_acceleate(car_state))

        car_state = CarState(
            car=self.car, track=self.track,
            speed=self.sector_1.get_max_speed(self.car.max_speed),
            acceleration=0.0,
            distance_from_start=1.0,
        )
        self.assertFalse(DecisionMaker.need_brake(car_state))
        self.assertFalse(DecisionMaker.need_acceleate(car_state))

        car_state = CarState(
            car=self.car, track=self.track,
            speed=self.sector_1.get_max_speed(self.car.max_speed),
            acceleration=0.0,
            distance_from_start=self.sector_1.length - 1.0,
        )
        self.assertTrue(DecisionMaker.need_brake(car_state))
        self.assertFalse(DecisionMaker.need_acceleate(car_state))
