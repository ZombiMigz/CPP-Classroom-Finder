from django.db import models


class ScheduleBlock(models.Model):
    building = models.CharField(max_length=30)
    room = models.CharField(max_length=30)
    start_time = models.TimeField()
    end_time = models.TimeField()
    day_of_the_week = models.CharField(max_length=2)
