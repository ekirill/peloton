from dataclasses import dataclass

from django.utils.functional import cached_property

from track.models import Track, TrackSector


RACE_TIME_FRAME = 0.01


@dataclass
class CarState:
    track: Track
    speed: float = 0.0
    acceleration: float = 0.0
    distance_from_start: float = 0.0
    _current_sector: TrackSector = None
    _distance_from_sector_start: float = None

    def _prefetch_current_sector(self):
        self._current_sector, self._distance_from_sector_start = self.track.get_sector(self.distance_from_start)

    @property
    def current_sector(self) -> TrackSector:
        if self._current_sector is None:
            self._prefetch_current_sector()
        return self._current_sector

    @property
    def distance_from_sector_start(self) -> float:
        if self._distance_from_sector_start is None:
            self._prefetch_current_sector()
        return self._distance_from_sector_start

    @cached_property
    def next_sector(self) -> TrackSector:
        return self.track.get_next_sector(self.current_sector.sector_order)


def get_riding_length(speed, acceleration, time_sec: float) -> float:
    return speed * time_sec + (acceleration * (time_sec ** 2)) / 2

def get_frame_riding_length(speed, acceleration) -> float:
    return get_riding_length(speed, acceleration, RACE_TIME_FRAME)


def evaluate_next_frame_state(current_state, new_acceleration):
    next_frame_state = CarState(
        track=current_state.track,
        speed=current_state.speed + new_acceleration * RACE_TIME_FRAME,
        acceleration=new_acceleration,
        distance_from_start=current_state.distance_from_start + get_frame_riding_length(
            current_state.speed, new_acceleration
        )
    )
    return next_frame_state
