from pydantic import BaseModel

from peloton.helpers.conversions import kmh


class SimConfig(BaseModel):
    float_precision: float
    slowest_curve_speed: float


sim_config = SimConfig(
    float_precision=0.001,
    slowest_curve_speed=kmh(10.0),
)
