from collections import namedtuple

from django.test import TestCase
from parameterized import parameterized

from cupapp.core import League, WrongNumberOfPlayersException, SmartLeague, build_table


class TournamentLeagueTest(TestCase):

    def test_create_schedule_raise_exception_when_wrong_number_of_players_passed(self):
        # given
        league = League(
            home_slots=2,
            away_slots=2,
            players=['p1', 'p2', 'p3']
        )

        # then
        with self.assertRaises(WrongNumberOfPlayersException):
            # when
            league.create_schedule()

    def test_create_schedule_return_tuple_with_proper_number_of_fixtures(self):
        # given
        league = League(
            home_slots=1,
            away_slots=1,
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
            home_slots=2,
            away_slots=2,
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

    @parameterized.expand([
        ([(0, 0)], [1, 1, 0, 0, 0, 0, 1, 0], [1, 1, 0, 0, 0, 0, 1, 0]),
        ([(2, 0)], [0, 1, 2, 0, 2, 0, 3, 1], [0, 1, -2, 2, 0, 1, 0, 0]),
        ([(3, 0), (None, None), (1, 1)], [1, 2, 3, 1, 4, 0, 4, 1], [1, 2, -3, 4, 1, 1, 1, 0]),
    ])
    def test_build_table_returns_table_from_context(
            self, fixtures, player_a_stats, player_b_stats
    ):
        # given
        player = namedtuple('player', ('player', 'name'))
        player_name = namedtuple('name', ('name',))
        p1 = player(player_name('A'), 'A')
        p2 = player(player_name('B'), 'B')
        context = {
            'players': [p1, p2],
            'schedule': [
                {
                    'home_players': [p1],
                    'home_goals': f[0],
                    'away_players': [p2],
                    'away_goals': f[1]
                } for f in fixtures
            ]
        }

        expected_table = [
            {
                'player_name': 'A',
                'stats': {
                    'draws': player_a_stats[0],
                    'games': player_a_stats[1],
                    'goal_difference': player_a_stats[2],
                    'goals_lost': player_a_stats[3],
                    'goals_scored': player_a_stats[4],
                    'lost': player_a_stats[5],
                    'points': player_a_stats[6],
                    'wins': player_a_stats[7]
                }
            },
            {
                'player_name': 'B',
                'stats': {
                    'draws': player_b_stats[0],
                    'games': player_b_stats[1],
                    'goal_difference': player_b_stats[2],
                    'goals_lost': player_b_stats[3],
                    'goals_scored': player_b_stats[4],
                    'lost': player_b_stats[5],
                    'points': player_b_stats[6],
                    'wins': player_b_stats[7]
                }
            }
        ]

        # when
        table = build_table(context)

        # then
        self.assertEqual(table, expected_table,
                         msg="Not expected tournament table data generated from context")


class SmartLeagueTest(TestCase):

    def test_next_round_prepare_schedules_with_tuple_of_tuples(self):
        # given
        league = SmartLeague(
            home_slots=1,
            away_slots=1,
            players=['p1', 'p2', 'p3']
        )

        # when
        league.next_round()

        # then
        self.assertIsInstance(league.schedule, tuple,
                              f"Schedule should be tuple instead of {type(league.schedule)}")
        self.assertGreater(len(league.schedule), 0, f"Schedule should not be empty")
        for fixture in league.schedule:
            self.assertIsInstance(fixture, tuple,
                                  f"Fixture should be tuple instead of {type(fixture)}")

    @parameterized.expand([
        (1, 1, ('p1', 'p2'), 2),
        (1, 1, ('p1', 'p2', 'p3'), 3),
        (1, 1, ('p1', 'p2', 'p3', 'p4'), 4),
        (1, 1, ('p1', 'p2', 'p3', 'p4', 'p5'), 5),
        (2, 1, ('p1', 'p2', 'p3'), 3),
        (2, 1, ('p1', 'p2', 'p3', 'p4'), 12),
        (2, 1, ('p1', 'p2', 'p3', 'p4', 'p5'), 10),
        (2, 1, ('p1', 'p2', 'p3', 'p4', 'p5', 'p6'), 30),
        (2, 2, ('p1', 'p2', 'p3', 'p4'), 6),
        (2, 2, ('p1', 'p2', 'p3', 'p4', 'p5'), 10),
        (2, 2, ('p1', 'p2', 'p3', 'p4', 'p5', 'p6'), 15),
        (2, 2, ('p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7'), 21),
    ])
    def test_next_round_inserts_proper_number_of_fixtures_to_schedule(
            self, home_slots, away_slots, players, expected_matches_count
    ):
        # given
        league = SmartLeague(
            home_slots=home_slots,
            away_slots=away_slots,
            players=players
        )

        # when
        league.next_round()

        # then
        self.assertEqual(len(league.schedule), expected_matches_count,
                         f"There should be {expected_matches_count} for "
                         f"game type {home_slots} vs {away_slots} and players {players} "
                         f"but there is {len(league.schedule)} fixtures in schedule: {league.schedule}")

    @parameterized.expand([
        (1, 1, ('p1', 'p2')),
        (1, 1, ('p1', 'p2', 'p3')),
        (1, 1, ('p1', 'p2', 'p3', 'p4')),
        (1, 1, ('p1', 'p2', 'p3', 'p4', 'p5')),
        (2, 1, ('p1', 'p2', 'p3')),
        (2, 1, ('p1', 'p2', 'p3', 'p4')),
        (2, 1, ('p1', 'p2', 'p3', 'p4', 'p5')),
        (2, 1, ('p1', 'p2', 'p3', 'p4', 'p5', 'p6')),
        (2, 2, ('p1', 'p2', 'p3', 'p4')),
        (2, 2, ('p1', 'p2', 'p3', 'p4', 'p5')),
        (2, 2, ('p1', 'p2', 'p3', 'p4', 'p5', 'p6')),
        (2, 2, ('p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7')),
    ])
    def test_no_players_conflicts_in_schedule(
            self, home_slots, away_slots, players
    ):
        # given
        league = SmartLeague(
            home_slots=home_slots,
            away_slots=away_slots,
            players=players
        )

        # when
        league.next_round()

        # then
        for fixture in league.schedule:
            home = fixture[0]
            away = fixture[1]
            self.assertFalse(any([p for p in home if p in away]),
                             f"There is conflict in fixture {home} vs {away} "
                             f"for {home_slots} vs {away_slots} game type "
                             f"and schedule {league.schedule}")
