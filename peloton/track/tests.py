from django.test import TestCase

from track.const import DIRECTION, CURVE
from track.models import TrackSector, Track


class TrackSectorTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.track = Track('test_track')

    def test_curve_category(self):
        sector = TrackSector(track=self.track, start=0, end=100, curve_radius=None, curve_direction=DIRECTION.LEFT)
        self.assertEqual(0, sector.curve_category)

        sector = TrackSector(track=self.track, start=0, end=100, curve_radius=100.0, curve_direction=DIRECTION.LEFT)
        self.assertEqual(1, sector.curve_category)

        sector = TrackSector(track=self.track, start=0, end=100, curve_radius=56.0, curve_direction=DIRECTION.LEFT)
        self.assertEqual(4, sector.curve_category)

        sector = TrackSector(track=self.track, start=0, end=100, curve_radius=33.0, curve_direction=DIRECTION.LEFT)
        self.assertEqual(5, sector.curve_category)

        sector = TrackSector(track=self.track, start=0, end=100, curve_radius=14.0, curve_direction=DIRECTION.LEFT)
        self.assertEqual(CURVE.MAX_CATEGORY, sector.curve_category)

    def test_curve_speed(self):
        sector = TrackSector(track=self.track, start=0, end=100, curve_radius=None, curve_direction=DIRECTION.LEFT)
        self.assertEqual(160.0, sector.get_max_speed(160.0))

        sector = TrackSector(track=self.track, start=0, end=100, curve_radius=100.0, curve_direction=DIRECTION.LEFT)
        self.assertTrue(130 <= sector.get_max_speed(160.0) <= 135)

        sector = TrackSector(track=self.track, start=0, end=100, curve_radius=56.0, curve_direction=DIRECTION.LEFT)
        self.assertTrue(75 <= sector.get_max_speed(160.0) <= 80)

        sector = TrackSector(track=self.track, start=0, end=100, curve_radius=33.0, curve_direction=DIRECTION.LEFT)
        self.assertTrue(50 <= sector.get_max_speed(160.0) <= 55)

        sector = TrackSector(track=self.track, start=0, end=100, curve_radius=14.0, curve_direction=DIRECTION.LEFT)
        self.assertTrue(15 <= sector.get_max_speed(160.0) <= 20)
