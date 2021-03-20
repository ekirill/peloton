from typing import Sequence

from pydantic import BaseModel, confloat


class Car(BaseModel):
    caption: str
    max_acceleration: confloat(strict=True, gt=0.0)
    max_braking: confloat(strict=True, gt=0.0)
    max_speed: confloat(strict=True, gt=0.0)


class Peloton(BaseModel):
    cars: Sequence[Car]
