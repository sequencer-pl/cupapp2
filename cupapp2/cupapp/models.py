from django.contrib.auth.models import User
from django.db import models


class Cup(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    forms = (
        ('cup', 'cup'),
        ('league', 'league'),
    )
    form = models.CharField(choices=forms, max_length=64)
    home_slots = models.PositiveSmallIntegerField(default=1)
    away_slots = models.PositiveSmallIntegerField(default=1)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.name}'


class Player(models.Model):
    name = models.CharField(max_length=64)
    stars_handicap = models.SmallIntegerField(default=10)
    cup = models.ForeignKey(Cup, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'


class Fixture(models.Model):
    order = models.SmallIntegerField(default=0)
    home_goals = models.PositiveSmallIntegerField(null=True)
    away_goals = models.PositiveSmallIntegerField(null=True)
    cup = models.ForeignKey(Cup, on_delete=models.CASCADE)


class FixturePlayer(models.Model):
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    home_away_indicators = (
        ('H', 'home'),
        ('A', 'away'),
    )
    home_away_indicator = models.CharField(choices=home_away_indicators, max_length=64)
