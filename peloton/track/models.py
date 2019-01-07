import math
from typing import Dict, Tuple

from django.db import models
from django.utils.functional import cached_property

from track.const import CURVE


class Track(models.Model):
    name = models.CharField(max_length=512)

    _sectors_index: Dict[float, 'TrackSector'] = None
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
    def length(self) -> float:
        if self._length is None:
            self._prefetch_sectors()
        return self._length

    def _prefetch_sectors(self):
        self._length = 0.0
        self._sectors_index = {}

        order_id = 0
        for sector in self.sectors.all():
            self._sectors_index[self._length] = sector
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

    def get_sector(self, distance_from_start: float) -> Tuple['TrackSector', float]:
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

        return sector, distance_from_sector_start

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
