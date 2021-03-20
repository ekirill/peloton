import math
from typing import Sequence

from pydantic import BaseModel, confloat, validator

from peloton.common.math import pull_down


class Sector(BaseModel):
    length: confloat(strict=True, gt=0)
    corner: confloat(strict=True, lt=360.0)

    @validator('corner')
    def curvature_is_possible(cls, v, values, **kwargs):
        if v == 0:
            return v

        if 'length' in values and cls.calculate_curvature(values['length'], v) > 1.0:
            raise ValueError('corner is too big, impossible to drive')
        return v

    @staticmethod
    def calculate_curvature(length: float, corner: float) -> float:
        """
        Assuming full corner (180 degrees) with 5 meter radius (Pi*5 length) is the curviest curvature == 1.0
        The straight line has 0.0 curvature
        """
        if length == 0:
            return 0.0

        k = (5 * math.pi) / 180
        curvature = (abs(corner)/length) * k
        return pull_down(curvature, 1.0)

    @property
    def curvature(self) -> float:
        return self.calculate_curvature(self.length, self.corner)


class Track(BaseModel):
    sectors: Sequence[Sector]

