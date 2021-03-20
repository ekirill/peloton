from django.db import models

from track.models import TrackSector, SectorPosition


class Car(models.Model):
    name = models.CharField(max_length=64)

    max_speed = 55.0  # m/s ~ 200 km/h
    max_acc = 3.5  # m/s
    min_acc = -9.8  # m/s

    def __str__(self):
        return f'Car "{self.name}"'
