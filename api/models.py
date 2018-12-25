from django.db import models


# Create your models here.
class User(models.Model):
    password = models.CharField(default='', max_length=100)
    id = models.AutoField(primary_key=True)


class Sleep(models.Model):
    start = models.CharField(max_length=20, default='')
    end = models.CharField(max_length=20, default='')
    id = models.AutoField(primary_key=True)


class BootTime(models.Model):
    start = models.CharField(max_length=20, default='')
    id = models.AutoField(primary_key=True)


class AcConfig(models.Model):
    power = models.BooleanField(default=False)
    working_mode = models.IntegerField(default=0)
    temperature = models.IntegerField(default=0)
    wind_speed = models.IntegerField(default=0)
    wind_flap = models.BooleanField(default=False)
    sleep_mode = models.BooleanField(default=False)
    anion = models.BooleanField(default=False)
    light = models.BooleanField(default=False)
    desiccation = models.BooleanField(default=False)
    ventilation = models.BooleanField(default=False)
    vertical_flap = models.BooleanField(default=False)
    horizontal_flap = models.BooleanField(default=False)
    temperature_display = models.BooleanField(default=False)
    energy_saving = models.BooleanField(default=False)
    season = models.IntegerField(default=1)
    id = models.AutoField(primary_key=True)


class Preference(models.Model):
    prepare = models.IntegerField(default=5)
    delay = models.IntegerField(default=5)
    season = models.IntegerField(default=1)
    id = models.AutoField(primary_key=True)


class CurrentAcConfig(models.Model):
    power = models.BooleanField(default=False)
    working_mode = models.IntegerField(default=0)
    temperature = models.IntegerField(default=0)
    wind_speed = models.IntegerField(default=0)
    wind_flap = models.BooleanField(default=False)
    sleep_mode = models.BooleanField(default=False)
    anion = models.BooleanField(default=False)
    light = models.BooleanField(default=False)
    desiccation = models.BooleanField(default=False)
    ventilation = models.BooleanField(default=False)
    vertical_flap = models.BooleanField(default=False)
    horizontal_flap = models.BooleanField(default=False)
    temperature_display = models.BooleanField(default=False)
    energy_saving = models.BooleanField(default=False)
    season = models.IntegerField(default=1)


class NoPeopleTime(models.Model):
    minute = models.CharField(default='', max_length=100)
    id = models.AutoField(primary_key=True)
