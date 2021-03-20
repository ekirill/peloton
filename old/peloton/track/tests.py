from peloton.testing.cases import BasicTestCase
from track.const import DIRECTION, CURVE
from track.models import TrackSector, Track


class TrackSectorTestCase(BasicTestCase):
    def test_curve_category(self):
        sector = TrackSector(track=self.track, length=100, curve_radius=None, curve_direction=DIRECTION.LEFT)
        self.assertEqual(0, sector.curve_category)

        sector = TrackSector(track=self.track, length=100, curve_radius=100.0, curve_direction=DIRECTION.LEFT)
        self.assertEqual(1, sector.curve_category)

        sector = TrackSector(track=self.track, length=100, curve_radius=56.0, curve_direction=DIRECTION.LEFT)
        self.assertEqual(4, sector.curve_category)

        sector = TrackSector(track=self.track, length=100, curve_radius=33.0, curve_direction=DIRECTION.LEFT)
        self.assertEqual(5, sector.curve_category)

        sector = TrackSector(track=self.track, length=100, curve_radius=14.0, curve_direction=DIRECTION.LEFT)
        self.assertEqual(CURVE.MAX_CATEGORY, sector.curve_category)

    def test_curve_speed(self):
        MAX_SPEED = 55.0

        sector = TrackSector(track=self.track, length=100, curve_radius=None, curve_direction=DIRECTION.LEFT)
        self.assertEqual(MAX_SPEED, sector.get_max_speed(MAX_SPEED))

        sector = TrackSector(track=self.track, length=100, curve_radius=100.0, curve_direction=DIRECTION.LEFT)
        self.assertTrue(43 <= sector.get_max_speed(MAX_SPEED) <= 46, sector.get_max_speed(MAX_SPEED))

        sector = TrackSector(track=self.track, length=100, curve_radius=56.0, curve_direction=DIRECTION.LEFT)
        self.assertTrue(25 <= sector.get_max_speed(MAX_SPEED) <= 27, sector.get_max_speed(MAX_SPEED))

        sector = TrackSector(track=self.track, length=100, curve_radius=33.0, curve_direction=DIRECTION.LEFT)
        self.assertTrue(17 <= sector.get_max_speed(MAX_SPEED) <= 19, sector.get_max_speed(MAX_SPEED))

        sector = TrackSector(track=self.track, length=100, curve_radius=14.0, curve_direction=DIRECTION.LEFT)
        self.assertTrue(5 <= sector.get_max_speed(MAX_SPEED) <= 7, sector.get_max_speed(MAX_SPEED))


class TrackTestCase(BasicTestCase):
    def setUp(self):
        track = Track.objects.create(name="test_track")
        TrackSector.objects.create(
            track=track, sector_order=0, length=33.2, curve_radius=None, curve_direction=DIRECTION.LEFT
        )
        TrackSector.objects.create(
            track=track, sector_order=1, length=33.2, curve_radius=20.0, curve_direction=DIRECTION.LEFT
        )
        TrackSector.objects.create(
            track=track, sector_order=2, length=12.1, curve_radius=None, curve_direction=DIRECTION.LEFT
        )
        TrackSector.objects.create(
            track=track, sector_order=3, length=15.0, curve_radius=33, curve_direction=DIRECTION.RIGHT
        )

        self.track = Track.objects.get(pk=track.pk)

    def test_get_sector(self):
        self.assertEqual(93.5, self.track.length)
        self.assertEqual(self.track.get_sector_position(0.0).sector.sector_order, 0)
        self.assertEqual(self.track.get_sector_position(0.1).sector.sector_order, 0)
        self.assertEqual(self.track.get_sector_position(33.1).sector.sector_order, 0)
        self.assertEqual(self.track.get_sector_position(33.2).sector.sector_order, 1)
        self.assertEqual(self.track.get_sector_position(40.2).sector.sector_order, 1)
        self.assertEqual(self.track.get_sector_position(67.0).sector.sector_order, 2)
        self.assertEqual(self.track.get_sector_position(90.2).sector.sector_order, 3)
        self.assertEqual(self.track.get_sector_position(93.4999999999).sector.sector_order, 3)

        self.assertEqual(self.track.get_sector_by_order(0).sector_order, 0)
        self.assertEqual(self.track.get_sector_by_order(2).sector_order, 2)

        self.assertEqual(self.track.get_next_sector(0).sector_order, 1)
        self.assertEqual(self.track.get_next_sector(1).sector_order, 2)
        self.assertEqual(self.track.get_next_sector(2).sector_order, 3)
        self.assertEqual(self.track.get_next_sector(3).sector_order, 0)

    def test_get_sector_on_track(self):
        self.assertEqual(0.0, self.track.get_distance_from_start(self.track.get_sector_position(0.0)))
        self.assertEqual(0.1, self.track.get_distance_from_start(self.track.get_sector_position(0.1)))
        self.assertEqual(33.1, self.track.get_distance_from_start(self.track.get_sector_position(33.1)))
        self.assertEqual(90.2, self.track.get_distance_from_start(self.track.get_sector_position(90.2)))

    def test_distance_between_sector_positions(self):
        self.assertEqual(
            0.0,
            self.track.distance_between_sector_positions(
                self.track.get_sector_position(0.0),
                self.track.get_sector_position(0.0)
            )
        )

        self.assertEqual(
            0.1,
            self.track.distance_between_sector_positions(
                self.track.get_sector_position(0.0),
                self.track.get_sector_position(0.1)
            )
        )

        self.assertEqual(
            33.1,
            self.track.distance_between_sector_positions(
                self.track.get_sector_position(0.0),
                self.track.get_sector_position(33.1)
            )
        )

        self.assertEqual(
            12.0,
            self.track.distance_between_sector_positions(
                self.track.get_sector_position(21.1),
                self.track.get_sector_position(33.1)
            )
        )

        self.assertEqual(
            65.6,
            self.track.distance_between_sector_positions(
                self.track.get_sector_position(33.0),
                self.track.get_sector_position(5.1)
            )
        )
