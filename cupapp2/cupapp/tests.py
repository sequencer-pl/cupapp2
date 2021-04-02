from django.contrib.auth.models import User
from django.test import TestCase

from cupapp.core import League, WrongNumberOfPlayersException
from cupapp.models import Cup


class AdminTest(TestCase):
    cupName = 'CupOne'
    cupDesc = 'SomeDesc'

    def setUp(self):
        User.objects.create_superuser(username='testuser', email='test@test.com', password='pass')
        Cup.objects.create(name=self.cupName, description=self.cupDesc, form=('cup', 'cup'),
                           owner=User.objects.get(username='testuser'))

    def test_if_proper_cup_name_in_admin(self):
        cup_one = Cup.objects.get(name=self.cupName)
        self.assertEqual(str(cup_one), f'{self.cupName}')


class CoreTest(TestCase):

    def test_create_schedule_raise_exception_when_wrong_number_of_players_passed(self):
        # given
        league = League(
            form='league',
            players_home=2,
            players_away=2,
            players=['p1', 'p2', 'p3']
        )

        # then
        with self.assertRaises(WrongNumberOfPlayersException):
            # when
            league.create_schedule()

    def test_create_schedule_return_tuple_with_proper_number_of_fixtures(self):
        # given
        league = League(
            form='league',
            players_home=1,
            players_away=1,
            players=['p1', 'p2', 'p3']
        )
        expected_number_of_fixtures = 3

        # when
        schedule = league.create_schedule()

        # then
        self.assertIsInstance(schedule, tuple)
        self.assertEqual(len(schedule), expected_number_of_fixtures)

    def test_create_rematch_round_returns_schedule_with_inverted_home_away(self):
        # given
        league = League(
            form='league',
            players_home=2,
            players_away=2,
            players=['p1', 'p2', 'p3', 'p4']
        )
        schedule = league.create_schedule()
        err_msg = 'Players in rematch schedule are not original schedule switched home/away'

        # when
        rematch_round = league.create_rematch_round(schedule)

        # then
        for i in range(len(schedule)):
            self.assertEqual(schedule[i][0], rematch_round[i][1], err_msg)
            self.assertEqual(schedule[i][1], rematch_round[i][0], err_msg)
