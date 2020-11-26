from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView, ListView

from cupapp import models
from cupapp.core import League
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
    model = models.Cup
    template_name = 'cupapp/cups.html'


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
        # return HttpResponseRedirect('')

    def get_context_data(self, **kwargs):
        context = super(Cup, self).get_context_data(**kwargs)
        context['cup'] = models.Cup.objects.get(id=kwargs.get('pk'))
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
        context['table'] = self.build_table(context)
        # logging.debug(connection.queries[-1])

        context['submit_fixture_form'] = SubmitFixture(self.request.POST or None)

        return context

    @staticmethod
    def build_table(context):
        stats = {}
        for fp in context.get('players'):
            stats[fp.name] = {
                "points": 0,
                "games": 0,
                "wins": 0,
                "draws": 0,
                "lost": 0,
                "goals_scored": 0,
                "goals_lost": 0,
                "goal_difference": 0,
            }
        for fixture in context.get('schedule'):
            if fixture.get('home_goals') is not None:
                if fixture['home_goals'] > fixture['away_goals']:
                    for fp in fixture['home_players']:
                        stats[fp.player.name]['points'] += 3
                        stats[fp.player.name]['games'] += 1
                        stats[fp.player.name]['wins'] += 1
                        stats[fp.player.name]['goals_scored'] += fixture['home_goals']
                        stats[fp.player.name]['goals_lost'] += fixture['away_goals']
                        stats[fp.player.name]['goal_difference'] += (fixture['home_goals'] - fixture['away_goals'])
                    for fp in fixture['away_players']:
                        stats[fp.player.name]['games'] += 1
                        stats[fp.player.name]['lost'] += 1
                        stats[fp.player.name]['goals_scored'] += fixture['away_goals']
                        stats[fp.player.name]['goals_lost'] += fixture['home_goals']
                        stats[fp.player.name]['goal_difference'] += (fixture['away_goals'] - fixture['home_goals'])
                elif fixture['home_goals'] == fixture['away_goals']:
                    for fp in fixture['home_players']:
                        stats[fp.player.name]['points'] += 1
                        stats[fp.player.name]['games'] += 1
                        stats[fp.player.name]['draws'] += 1
                        stats[fp.player.name]['goals_scored'] += fixture['home_goals']
                        stats[fp.player.name]['goals_lost'] += fixture['away_goals']
                    for fp in fixture['away_players']:
                        stats[fp.player.name]['points'] += 1
                        stats[fp.player.name]['games'] += 1
                        stats[fp.player.name]['draws'] += 1
                        stats[fp.player.name]['goals_scored'] += fixture['away_goals']
                        stats[fp.player.name]['goals_lost'] += fixture['home_goals']
                elif fixture['home_goals'] < fixture['away_goals']:
                    for fp in fixture['home_players']:
                        stats[fp.player.name]['games'] += 1
                        stats[fp.player.name]['lost'] += 1
                        stats[fp.player.name]['goals_scored'] += fixture['away_goals']
                        stats[fp.player.name]['goals_lost'] += fixture['home_goals']
                        stats[fp.player.name]['goal_difference'] += (fixture['away_goals'] - fixture['home_goals'])
                    for fp in fixture['away_players']:
                        stats[fp.player.name]['points'] += 3
                        stats[fp.player.name]['games'] += 1
                        stats[fp.player.name]['wins'] += 1
                        stats[fp.player.name]['goals_scored'] += fixture['home_goals']
                        stats[fp.player.name]['goals_lost'] += fixture['away_goals']
                        stats[fp.player.name]['goal_difference'] += (fixture['home_goals'] - fixture['away_goals'])
            else:
                break
        table = []
        for p, s in stats.items():
            table.append({"player_name": p, "stats": s})
        table.sort(key=lambda x: (x.get('stats').get('points'),
                                  x.get('stats').get('goal_difference'),
                                  x.get('stats').get('goals_scored')),
                   reverse=True)
        return table


@login_required(login_url='login')
def new_cup(request):
    template_name = 'cupapp/newcup.html'
    if request.method == 'POST':
        newcup = NewCup(request.POST)
        players_formset = PlayerFormset(request.POST)
        if newcup.is_valid() and players_formset.is_valid():
            cup = models.Cup()
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

            schedule = League(
                form=cup.form,
                players_home=cup.home_slots,
                players_away=cup.away_slots,
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

