from dataclasses import dataclass
from typing import Optional

from django.utils.functional import cached_property

from car.models import Car
from track.models import Track, TrackSector, SectorPosition

RACE_TIME_FRAME = 0.01


@dataclass
class CarState:
    car: Car
    track: Track
    speed: float = 0.0
    acceleration: float = 0.0
    distance_from_start: float = 0.0
    _current_sector_position: SectorPosition = None
    _distance_from_sector_start: float = None

    def _prefetch_current_sector(self):
        self._current_sector_position = self.track.get_sector_position(self.distance_from_start)

    @property
    def current_sector_position(self) -> SectorPosition:
        if self._current_sector_position is None:
            self._prefetch_current_sector()
        return self._current_sector_position

    @property
    def distance_from_sector_start(self) -> float:
        if self._distance_from_sector_start is None:
            self._prefetch_current_sector()
        return self._distance_from_sector_start

    @cached_property
    def next_sector(self) -> TrackSector:
        return self.track.get_next_sector(self.current_sector_position.sector.sector_order)

    @cached_property
    def next_slower_sector(self) -> Optional[TrackSector]:
        current_sector_position = self.current_sector_position
        current_sector = current_sector_position.sector

        _sector = self.track.get_next_sector(current_sector.sector_order)
        while _sector != current_sector:
            if _sector.get_max_speed(self.car.max_speed) < self.speed:
                return _sector
            _sector = self.track.get_next_sector(_sector.sector_order)

    def get_braking_length(self, need_speed: float) -> float:
        if need_speed > self.speed:
            raise ValueError(f"You should not brake to increase spead from `{self.speed}` to `{need_speed}`")
        length = (need_speed ** 2 - self.speed ** 2) / (2 * self.car.min_acc)
        return length

    def get_distance_to_braking_point(self, slower_sector: TrackSector) -> float:
        need_speed = slower_sector.get_max_speed(self.car.max_speed)
        braking_length = self.get_braking_length(need_speed)
        distance_to_slower_sector = self.track.distance_between_sector_positions(
            self.current_sector_position, SectorPosition(slower_sector, 0.0)
        )
        return distance_to_slower_sector - braking_length

    def get_next_frame_distance_to_braking_point(self, slower_sector: TrackSector) -> float:
        one_frame_length = get_frame_riding_length(self.speed, 0)
        return self.get_distance_to_braking_point(slower_sector) - one_frame_length

    @cached_property
    def possible_to_brake(self) -> bool:
        if not self.next_slower_sector:
            return True
        return self.get_distance_to_braking_point(self.next_slower_sector) >= 0


class DecisionMaker:
    @staticmethod
    def need_brake(car_state: CarState) -> bool:
        current_sector = car_state.current_sector_position.sector
        if car_state.speed > current_sector.get_max_speed(car_state.car.max_speed):
            return True

        slower_sector = car_state.next_slower_sector
        if slower_sector:
            # to be the best pilot we should start braking at the last possible moment
            next_frame_distance_to_braking_point = car_state.get_next_frame_distance_to_braking_point(slower_sector)
            if next_frame_distance_to_braking_point <= 0:
                return True

        return False

    @staticmethod
    def need_acceleate(car_state: CarState) -> bool:
        current_sector = car_state.current_sector_position.sector
        if car_state.speed < current_sector.get_max_speed(car_state.car.max_speed):
            # checking wheather it will be possible to stop next frame if we accelerate now
            next_frame_state = evaluate_next_frame_state(car_state, car_state.car.max_acc)
            if next_frame_state.possible_to_brake:
                return True

            return True
        return False


def get_riding_length(speed, acceleration, time_sec: float) -> float:
    return speed * time_sec + (acceleration * (time_sec ** 2)) / 2


def get_frame_riding_length(speed, acceleration) -> float:
    return get_riding_length(speed, acceleration, RACE_TIME_FRAME)


def evaluate_next_frame_state(current_state: CarState, new_acceleration: float) -> CarState:
    next_frame_state = CarState(
        track=current_state.track,
        car=current_state.car,
        speed=current_state.speed + new_acceleration * RACE_TIME_FRAME,
        acceleration=new_acceleration,
        distance_from_start=current_state.distance_from_start + get_frame_riding_length(
            current_state.speed, new_acceleration
        )
    )
    return next_frame_state
