from django.core.management import BaseCommand

from car.models import Car
from race.action import CarState, DecisionMaker, evaluate_next_frame_state, RACE_FRAME_DURATION
from track.const import CURVE, DIRECTION
from track.models import Track, TrackSector


def get_track():
    track, is_new = Track.objects.get_or_create(name='Track Brakogama')

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


def get_car():
    car, _ = Car.objects.get_or_create(name='Kir Bolid')
    return car


class Command(BaseCommand):
    def handle(self, *args, **options):
        track = get_track()
        car = get_car()

        car_state = CarState(car=car, track=track)

        race_laps = 2
        race_distance = race_laps * track.length
        frame = 0

        while car_state.distance_from_start < race_distance:
            new_acceleration = car_state.acceleration

            if DecisionMaker.need_acceleate(car_state):
                new_acceleration = car.max_acc
            elif DecisionMaker.need_brake(car_state):
                new_acceleration = car.min_acc

            race_time = frame * RACE_FRAME_DURATION
            if race_time % 1.00 == 0:
                print(
                    f"TIME: {race_time:06.02f}s\t"
                    f"DISTANCE: {car_state.distance_from_start:07.2f}m\t"
                    f"SPEED: {car_state.speed_kmh:.2f}"
                )

            car_state = evaluate_next_frame_state(car_state, new_acceleration)

            frame += 1
