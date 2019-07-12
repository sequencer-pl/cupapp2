from django.contrib import admin
from cupapp.models import Cup, Player, Fixture, FixturePlayer

admin.site.register(Cup)
admin.site.register(Player)
admin.site.register(Fixture)
admin.site.register(FixturePlayer)
