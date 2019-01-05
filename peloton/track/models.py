import math

from django.db import models
from django.utils.functional import cached_property

from track.const import CURVE


class Track(models.Model):
    name = models.CharField(max_length=512)


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
        return max_speed / divider
