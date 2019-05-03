import math
from typing import Dict, Tuple, NamedTuple

from django.db import models
from django.utils.functional import cached_property

from track.const import CURVE, DIRECTION


class Track(models.Model):
    name = models.CharField(max_length=512)

    _sectors_index: Dict[float, 'TrackSector'] = None
    _sectors_at_track_index: Dict[int, float] = None
    _sectors_index_keys: tuple = None
    _length: float = None

    @property
    def sectors_index(self) -> Dict[float, 'TrackSector']:
        if self._sectors_index is None:
            self._prefetch_sectors()
        return self._sectors_index

    @property
    def sectors_index_keys(self) -> tuple:
        if self._sectors_index_keys is None:
            self._sectors_index_keys = sorted(self.sectors_index.keys())
        return self._sectors_index_keys

    @property
    def sectors_at_track_index(self) -> Dict[int, float]:
        if self._sectors_at_track_index is None:
            self._prefetch_sectors()
        return self._sectors_at_track_index

    @property
    def length(self) -> float:
        if self._length is None:
            self._prefetch_sectors()
        return self._length

    def _prefetch_sectors(self):
        self._length = 0.0
        self._sectors_index = {}
        self._sectors_at_track_index = {}

        order_id = 0
        for sector in self.sectors.all():
            self._sectors_index[self._length] = sector
            self._sectors_at_track_index[sector.sector_order] = self._length
            if sector.sector_order != order_id:
                raise RuntimeError(
                    f"Track is invalid, sector must have order_id {order_id}, "
                    f"but has `{sector.sector_order}`"
                )
            self._length += sector.length

            order_id += 1

    @property
    def last_sector(self) -> 'TrackSector':
        if not self.sectors_index_keys:
            raise RuntimeError('This track does not have any sectors')

        return self.sectors_index[self.sectors_index_keys[-1]]

    def get_sector_position(self, distance_from_start: float) -> 'SectorPosition':
        sector = None
        distance_from_sector_start = 0.0

        lap_distance_from_start = distance_from_start % self.length
        for sector_distance_from_start in self.sectors_index_keys:
            _sector = self.sectors_index[sector_distance_from_start]
            if sector_distance_from_start <= lap_distance_from_start < sector_distance_from_start + _sector.length:
                sector = _sector
                distance_from_sector_start = lap_distance_from_start - sector_distance_from_start

        if not sector:
            sector = self.last_sector
            sector_distance_from_start = self.sectors_index_keys[-1]
            distance_from_sector_start = lap_distance_from_start - sector_distance_from_start

        return SectorPosition(sector, distance_from_sector_start)

    def get_distance_from_start(self, sector_position: 'SectorPosition') -> float:
        if sector_position.sector.track_id != self.pk:
            raise ValueError('Current sector does not belong to this track')
        if sector_position.sector.sector_order not in self.sectors_at_track_index:
            raise ValueError(f'Can not find track with order `{sector_position.sector.sector_order}` at track')
        sector_start_on_track = self.sectors_at_track_index[sector_position.sector.sector_order]
        return sector_start_on_track + sector_position.distance_from_sector_start

    def distance_between_sector_positions(self, pos1, pos2: 'SectorPosition') -> float:
        """
        Distance to ride from pos1 to pos2
        """
        dist_from_start_1 = self.get_distance_from_start(pos1)
        dist_from_start_2 = self.get_distance_from_start(pos2)
        if dist_from_start_2 >= dist_from_start_1:
            return dist_from_start_2 - dist_from_start_1
        else:
            return self.length - dist_from_start_1 + dist_from_start_2

    def get_sector_by_order(self, order_id: int) -> 'TrackSector':
        if order_id >= len(self.sectors_index_keys):
            raise RuntimeError(f"This track has no sector with order_id `{order_id}`")

        return self.sectors_index[self.sectors_index_keys[order_id]]

    def get_next_sector(self, order_id: int) -> 'TrackSector':
        if order_id >= len(self.sectors_index_keys):
            raise RuntimeError(f"This track has no sector with order_id `{order_id}`")

        next_order_id = order_id + 1
        if next_order_id >= len(self.sectors_index_keys):
            next_order_id = 0

        return self.get_sector_by_order(next_order_id)

    def __str__(self):
        return f'Track "{self.name}" ({self.length}m)'


class TrackSector(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='sectors')
    sector_order = models.IntegerField()
    length = models.FloatField()
    curve_radius = models.FloatField(null=True)
    curve_direction = models.CharField(max_length=5, null=True)

    @cached_property
    def curve_category(self) -> int:
        if self.curve_radius is None or self.curve_radius > CURVE.MAX_RADIUS:
            return 0

        step = (CURVE.MAX_RADIUS - CURVE.MIN_RADIUS) / (CURVE.MAX_CATEGORY - 1)

        for i in range(1, CURVE.MAX_CATEGORY):
            radius = (CURVE.MAX_CATEGORY - 1 - i) * step + CURVE.MIN_RADIUS
            if self.curve_radius > radius:
                return i

        return CURVE.MAX_CATEGORY

    def get_max_speed(self, max_speed: float) -> float:
        if self.curve_category == 0:
            return max_speed

        divider = 1.1 + (math.e ** (self.curve_category / 1.5)) / 15
        return round(max_speed / divider, 2)

    class Meta:
        ordering = ["sector_order"]


class SectorPosition(NamedTuple):
    sector: TrackSector
    distance_from_sector_start: float


def get_default_track():
    track, is_new = Track.objects.get_or_create(name='Track Default')

    if not is_new:
        return track

    sectors = [
        TrackSector(track=track, length=150.0, curve_radius=None, curve_direction=None),
        TrackSector(track=track, length=15.0, curve_radius=15.0, curve_direction=DIRECTION.RIGHT),
        TrackSector(track=track, length=15.0, curve_radius=15.0, curve_direction=DIRECTION.LEFT),
        TrackSector(track=track, length=25.0, curve_radius=15.0, curve_direction=DIRECTION.RIGHT),
        TrackSector(track=track, length=44.0, curve_radius=None, curve_direction=None),
        TrackSector(track=track, length=50.0, curve_radius=45.0, curve_direction=DIRECTION.LEFT),
        TrackSector(track=track, length=20.0, curve_radius=None, curve_direction=None),
        TrackSector(track=track, length=100.0, curve_radius=200.0, curve_direction=DIRECTION.RIGHT),
        TrackSector(track=track, length=50.0, curve_radius=50.0, curve_direction=DIRECTION.RIGHT),
        TrackSector(track=track, length=70.0, curve_radius=30.0, curve_direction=DIRECTION.RIGHT),
        TrackSector(track=track, length=140.0, curve_radius=150.0, curve_direction=DIRECTION.LEFT),
        TrackSector(track=track, length=200.0, curve_radius=None, curve_direction=None),
        TrackSector(track=track, length=30.0, curve_radius=43.0, curve_direction=DIRECTION.LEFT),
        TrackSector(track=track, length=120.0, curve_radius=None, curve_direction=None),
        TrackSector(track=track, length=50.0, curve_radius=23.0, curve_direction=DIRECTION.RIGHT),
        TrackSector(track=track, length=120.0, curve_radius=None, curve_direction=None),
        TrackSector(track=track, length=185.0, curve_radius=65.89, curve_direction=DIRECTION.RIGHT),
        TrackSector(track=track, length=68.6, curve_radius=28.1, curve_direction=DIRECTION.LEFT),
        TrackSector(track=track, length=14.5, curve_radius=15.0, curve_direction=DIRECTION.RIGHT),
    ]
    for idx, sector in enumerate(sectors):
        sector.sector_order = idx
    TrackSector.objects.bulk_create(sectors)

    return track
