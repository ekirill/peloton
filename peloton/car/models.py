from django.db import models

from race.action import CarState, evaluate_next_frame_state, get_frame_riding_length


class Car(models.Model):
    name = models.CharField(max_length=64)

    max_speed = 55.0  # m/s ~ 200 km/h
    max_acc = 3.5  # m/s
    min_acc = -9.8  # m/s

    def get_braking_length(self, current_speed, need_speed: float) -> float:
        if need_speed > current_speed:
            raise ValueError(f"You should not brake to increase spead from `{current_speed}` to `{need_speed}`")
        length = (need_speed ** 2 - current_speed ** 2) / (2 * self.min_acc)
        return length

    def possible_to_brake(self, car_state: CarState) -> bool:
        next_sector = car_state.next_sector
        need_speed = next_sector.get_max_speed(self.max_speed)
        if need_speed >= car_state.speed:
            return True

        # need to brake before curve
        braking_length = self.get_braking_length(car_state.speed, need_speed)
        one_frame_length = get_frame_riding_length(car_state.speed, 0)
        current_sector = car_state.current_sector
        length_to_next_sector = current_sector.length - car_state.distance_from_sector_start
        # adding one frame for being sure next frame will not be too late
        if length_to_next_sector >= (one_frame_length + braking_length):
            return True

        return False

    def need_brake(self, car_state: CarState) -> bool:
        current_sector = car_state.current_sector
        if car_state.speed > current_sector.get_max_speed(self.max_speed):
            return True

        next_sector = car_state.next_sector
        need_speed = next_sector.get_max_speed(self.max_speed)
        if need_speed < car_state.speed:
            # need to brake before curve
            braking_length = self.get_braking_length(car_state.speed, need_speed)
            one_frame_length = get_frame_riding_length(car_state.speed, 0)
            length_to_next_sector = current_sector.length - car_state.distance_from_sector_start
            # adding one frame for being sure next frame will not be too late
            if length_to_next_sector <= (one_frame_length + braking_length):
                return True

        return False

    def need_acceleate(self, car_state: CarState) -> bool:
        current_sector = car_state.current_sector
        if car_state.speed < current_sector.get_max_speed(self.max_speed):
            # checking wheather it will be possible to stop next frame if we accelerate now
            next_frame_state = evaluate_next_frame_state(car_state, self.max_acc)
            if self.possible_to_brake(next_frame_state):
                return True

            return True
        return False

    def __str__(self):
        return f"Car: {self.name}"
