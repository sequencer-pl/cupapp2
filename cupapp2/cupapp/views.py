from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView, ListView

from cupapp import models
from cupapp.core import League, SmartLeague, build_table
from cupapp.forms import NewCup, PlayerFormset, SubmitFixture
import logging

from logger.logging import logging_setup
logging_setup()


class Home(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'cupapp/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class Cups(LoginRequiredMixin, ListView):
    login_url = 'login'
    context_object_name = 'cups'
    model = models.Tournament
    template_name = 'cupapp/cups.html'

    def get_context_data(self, **kwargs):
        context = super(Cups, self).get_context_data(**kwargs)
        context['cups_info'] = []
        for cup in context.get('cups'):
            context['cups_info'].append({
                'id': cup.id,
                'name': cup.name,
                'description': cup.description,
                'form': cup.form,
                'owner': cup.owner,
                'home_slots': cup.home_slots,
                'away_slots': cup.away_slots,
                'players': [p for p in models.Player.objects.select_related('cup').filter(cup=cup)],
                'games_played': len(
                    [f for f in models.Fixture.objects.select_related('cup').filter(cup=cup)
                     if f.home_goals and f.away_goals]
                ),
                'games_total': len(models.Fixture.objects.select_related('cup').filter(cup=cup)),
            })
        s = [f for f in models.Fixture.objects.select_related('cup').filter(cup=cup)]
        logging.debug(s)
        logging.debug([f for f in models.Fixture.objects.select_related('cup').filter(cup=cup)
                       if not f.home_goals and not f.away_goals])
        logging.debug(context)
        return context


def get_players_by_cup_id(_id):
    queryset = models.Player.objects.select_related('cup').get(id=_id)
    return queryset


class Cup(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'cupapp/cup.html'

    def post(self, request, *args, **kwargs):
        logging.debug(request)
        context = self.get_context_data(**kwargs)
        logging.debug(context)
        if context['submit_fixture_form'].is_valid():
            logging.debug(context['next_matchday'])
            logging.debug(context['submit_fixture_form'])
            fixture = models.Fixture.objects.get(id=context['next_matchday'].get('fixture_id'))
            logging.debug(context['submit_fixture_form'].cleaned_data)
            fixture.home_goals = int(context['submit_fixture_form'].cleaned_data.get('home_goals'))
            fixture.away_goals = int(context['submit_fixture_form'].cleaned_data.get('away_goals'))
            fixture.save()
        return HttpResponseRedirect(reverse('cup', kwargs={'pk': context['cup'].id}))

    def get_context_data(self, **kwargs):
        context = super(Cup, self).get_context_data(**kwargs)
        context['cup'] = models.Tournament.objects.get(id=kwargs.get('pk'))
        context['players'] = models.Player.objects.filter(cup=context.get('cup'))
        fixtures = models.Fixture.objects.filter(cup=context.get('cup')).select_related('cup')
        context['fixtures'] = fixtures
        schedule = []
        for fixture in fixtures:
            home_players = models.FixturePlayer.objects.filter(fixture=fixture).filter(home_away_indicator='H')
            away_players = models.FixturePlayer.objects.filter(fixture=fixture).filter(home_away_indicator='A')
            schedule.append({
                'fixture_id': fixture.id,
                'matchday': fixture.order,
                'home_players': home_players,
                'home_goals': fixture.home_goals,
                'away_players': away_players,
                'away_goals': fixture.away_goals,
            })

            if not context.get('next_matchday') and fixture.home_goals is None:
                context['next_matchday'] = schedule[-1] if len(schedule) > 0 else None

        if self.request.GET.get('next'):
            logging.debug(self.request.GET.get('next'))
            fixture_id = self.request.GET.get('next')
            context['next_matchday'] = next((f for f in schedule if f['fixture_id'] == int(fixture_id)), None)
            logging.debug(context['next_matchday'])
        elif self.request.GET.get('edit'):
            logging.debug(self.request.GET.get('edit'))
            fixture_id = self.request.GET.get('edit')
            context['next_matchday'] = next((f for f in schedule if f['fixture_id'] == int(fixture_id)), None)

        context['schedule'] = schedule
        context['table'] = build_table(context)

        context['submit_fixture_form'] = SubmitFixture(self.request.POST or None)
        logging.debug(context)
        return context


@login_required(login_url='login')
def new_cup(request):
    template_name = 'cupapp/newcup.html'
    if request.method == 'POST':
        newcup = NewCup(request.POST)
        players_formset = PlayerFormset(request.POST)
        if newcup.is_valid() and players_formset.is_valid():
            cup = models.Tournament()
            cup.name = newcup.cleaned_data.get('name')
            cup.description = newcup.cleaned_data.get('description')
            cup.home_slots = newcup.cleaned_data.get('mode')[0]
            cup.away_slots = newcup.cleaned_data.get('mode')[1]
            cup.form = newcup.cleaned_data.get('form')
            cup.owner = request.user
            cup.save()

            players = {}
            for player_form in players_formset:
                if player_form.is_valid():
                    player = models.Player()
                    player.name = player_form.cleaned_data.get('name')
                    player.stars_handicap = player_form.cleaned_data.get('stars')
                    player.cup = cup
                    player.user = request.user
                    players[player.name] = player
                    player.save()

            if cup.form == 'smart_league':
                league = SmartLeague(
                    home_slots=cup.home_slots,
                    away_slots=cup.away_slots,
                    players=players.keys()
                )
                league.next_round()
                schedule = league.schedule
            else:
                schedule = League(
                    home_slots=cup.home_slots,
                    away_slots=cup.away_slots,
                    players=players.keys()
                ).create_schedule()

            matchday = 1
            for fixture in schedule:
                fixture_model = models.Fixture()
                fixture_model.order = matchday
                fixture_model.cup = cup
                fixture_model.save()
                for player_home in fixture[0]:
                    fixture_player_model = models.FixturePlayer()
                    fixture_player_model.fixture = fixture_model
                    fixture_player_model.home_away_indicator = 'H'
                    fixture_player_model.player = players.get(player_home)
                    fixture_player_model.save()
                for player_away in fixture[1]:
                    fixture_player_model = models.FixturePlayer()
                    fixture_player_model.fixture = fixture_model
                    fixture_player_model.home_away_indicator = 'A'
                    fixture_player_model.player = players.get(player_away)
                    fixture_player_model.save()
                matchday += 1

            messages.success(request, 'Cup created successfully!')
            return HttpResponseRedirect(reverse('cup', kwargs={'pk': cup.id}))
        else:
            return HttpResponseRedirect("")
    else:
        newcup = NewCup(request.GET or None)
        players_formset = PlayerFormset()

    return render(request, template_name, {
        'newcup': newcup,
        'players': players_formset,
    })

