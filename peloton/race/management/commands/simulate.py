from django.core.management import BaseCommand

from car.models import Car
from race.action import CarState, DecisionMaker, evaluate_next_frame_state, RACE_FRAME_DURATION
from race.models import Race, RaceLog, RaceFrame
from track.models import get_default_track


def get_car():
    car, _ = Car.objects.get_or_create(name='Kir Bolid')
    return car


class Command(BaseCommand):
    def handle(self, *args, **options):
        track = get_default_track()
        car = get_car()
        race, _ = Race.objects.get_or_create(title="Test race")
        RaceLog.objects.filter(race_frame__race=race).delete()
        RaceFrame.objects.filter(race=race).delete()

        car_state = CarState(car=car, track=track)

        race_laps = 2
        race_distance = race_laps * track.length
        frame = 0

        while car_state.distance_from_start < race_distance:
            frame += 1

            new_acceleration = car_state.acceleration

            if DecisionMaker.need_acceleate(car_state):
                new_acceleration = car.max_acc
            elif DecisionMaker.need_brake(car_state):
                new_acceleration = car.min_acc

            race_time = frame * RACE_FRAME_DURATION
            if frame % 10 == 0:
                race_frame = RaceFrame.objects.create(
                    race=race,
                    race_time=race_time,
                )
                RaceLog.objects.create(
                    race_frame=race_frame,
                    car=car,
                    distance_from_start=car_state.distance_from_start,
                    acceleration=car_state.acceleration,
                    speed=car_state.speed,
                )
                print(
                    f"TIME: {race_time:06.02f}s\t"
                    f"DISTANCE: {car_state.distance_from_start:07.2f}m\t"
                    f"SPEED: {car_state.speed_kmh:.2f}"
                )

            car_state = evaluate_next_frame_state(car_state, new_acceleration)
