from pydantic import BaseModel

from peloton.conf.settings import sim_config
from peloton.models.bolid import Car
from peloton.models.track import Sector


class RaceCar(BaseModel):
    car: Car
    speed: float

    def max_speed(self, sector: Sector) -> float:
        speed_delta = self.car.max_speed - sim_config.slowest_curve_speed
        speed_k = (1.0 - sector.curvature)**2
        return speed_delta * speed_k + sim_config.slowest_curve_speed
