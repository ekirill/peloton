from django.db import models


class Race(models.Model):
    title = models.CharField(max_length=256)


class RaceFrame(models.Model):
    race = models.ForeignKey(Race, on_delete=models.PROTECT)
    race_time = models.DecimalField(decimal_places=2, max_digits=10)


class RaceLog(models.Model):
    race_frame = models.ForeignKey(RaceFrame, on_delete=models.PROTECT)
    car = models.ForeignKey('car.Car', on_delete=models.PROTECT)

    distance_from_start = models.FloatField()
    acceleration = models.FloatField()
    speed = models.FloatField()
