from django.contrib import admin
from cupapp.models import Tournament, Player, Fixture, FixturePlayer

admin.site.register(Tournament)
admin.site.register(Player)
admin.site.register(Fixture)
admin.site.register(FixturePlayer)
