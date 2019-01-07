from car.models import Car
from peloton.testing.cases import BasicTestCase
from race.action import CarState
from track.const import DIRECTION
from track.models import TrackSector, Track


class CarDecisionTestCase(BasicTestCase):
    def test_actions(self):
        TrackSector.objects.create(track=self.track, length=1000, curve_radius=None, sector_order=0)
        TrackSector.objects.create(
            track=self.track, length=20, sector_order=1, curve_radius=20, curve_direction=DIRECTION.LEFT
        )
        TrackSector.objects.create(
            track=self.track, length=20, sector_order=2, curve_radius=40, curve_direction=DIRECTION.LEFT
        )

        track = Track.objects.get(pk=self.track.pk)

        car = Car(name="test_car")

        state = CarState(track=track, speed=0, acceleration=0, distance_from_start=0)
        self.assertFalse(car.need_brake(state))
        self.assertTrue(car.need_acceleate(state))

        state = CarState(track=track, speed=car.max_speed - 10, acceleration=0, distance_from_start=10.0)
        self.assertFalse(car.need_brake(state))
        self.assertTrue(car.need_acceleate(state))

        state = CarState(track=track, speed=car.max_speed, acceleration=0, distance_from_start=10.0)
        self.assertFalse(car.need_brake(state))
        self.assertFalse(car.need_acceleate(state))

        state = CarState(track=track, speed=car.max_speed, acceleration=0, distance_from_start=820.0)
        self.assertFalse(car.need_brake(state))
        self.assertFalse(car.need_acceleate(state))

        state = CarState(track=track, speed=car.max_speed, acceleration=0, distance_from_start=870.0)
        self.assertTrue(car.need_brake(state))
        self.assertFalse(car.need_acceleate(state))

        state = CarState(track=track, speed=11, acceleration=0, distance_from_start=1001.0)
        self.assertFalse(car.need_brake(state))
        self.assertTrue(car.need_acceleate(state))

        state = CarState(track=track, speed=11.6, acceleration=0, distance_from_start=1001.0)
        self.assertFalse(car.need_brake(state))
        self.assertFalse(car.need_acceleate(state))

        state = CarState(track=track, speed=11.6, acceleration=0, distance_from_start=1020.0)
        self.assertFalse(car.need_brake(state))
        self.assertTrue(car.need_acceleate(state))

        state = CarState(track=track, speed=18.53, acceleration=0, distance_from_start=1020.0)
        self.assertFalse(car.need_brake(state))
        self.assertFalse(car.need_acceleate(state))

        state = CarState(track=track, speed=18.53, acceleration=0, distance_from_start=1041.0)
        self.assertFalse(car.need_brake(state))
        self.assertTrue(car.need_acceleate(state))
