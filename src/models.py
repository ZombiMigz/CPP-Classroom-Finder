from django.db import models


class ScheduleBlock(models.Model):
    building = models.CharField(max_length=30)
    room = models.CharField(max_length=30)
    start_time = models.TimeField()
    end_time = models.TimeField()
    day_of_the_week = models.CharField(max_length=2)

    def __str__(self):
        return f"ScheduleBlock(field1={self.building}, field2={self.room}, field3={self.start_time}, field4={self.end_time})"
