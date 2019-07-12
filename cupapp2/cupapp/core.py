import itertools
import logging
from random import shuffle

from logger.logging import logging_setup


class League:
    def __init__(self, form, players_home, players_away, players):
        logging_setup()
        self.form = form
        self.players_home = int(players_home)
        self.players_away = int(players_away)
        self.players = players
        self.schedule = ()
        self.ordered_schedule = ()

    def create_schedule(self):
        if not self.players_home or not self.players_away \
                or len(self.players) < self.players_home + self.players_away:
            raise WrongNumberOfPlayersException

        if self.form == 'league':
            for home in itertools.combinations(self.players, self.players_home):
                for away_pos in itertools.combinations(self.players, self.players_away):
                    away_filtered = [p for p in away_pos if p not in home]
                    if len(away_filtered) != self.players_away:
                        continue
                    away = tuple(away_filtered)
                    fixture = (home, away)
                    if (away, home) not in self.schedule:
                        self.schedule += (fixture,)
            self.ordered_schedule = self._order_schedule()
            return self.ordered_schedule

    @staticmethod
    def create_rematch_round(schedule):
        rematch_round = ()
        for fixture in schedule:
            rematch_round += ((fixture[1], fixture[0]),)
        return rematch_round

    def _order_schedule(self, pre_shuffle=1):

        def add_to_matches_count(players):
            for p in players:
                matches_count[p] += 1

        schedule = list(self.schedule)
        if pre_shuffle:
            shuffle(schedule)
        matches_count = {}
        for player in self.players:
            matches_count[player] = 0

        while len(self.ordered_schedule) < len(self.schedule):
            min_games_players = [player for player in matches_count
                                 if matches_count.get(player) == min(matches_count.values())]
            logging.debug(f'players with minimum games played: {min_games_players}')

            next_fixture = None
            matchday_players = set()
            for i in range(len(min_games_players)):
                for miss in itertools.combinations(min_games_players, i):
                    optimal_players = set([player for player in min_games_players if player not in miss])
                    logging.debug(f'optimal players: {optimal_players}')

                    for fixture in schedule:
                        matchday_players = set()
                        for teams in fixture:
                            for player in teams:
                                matchday_players.add(player)
                        logging.debug(f'matchday players: {matchday_players}')
                        if len(optimal_players) > len(matchday_players):
                            for lucky_players in itertools.combinations(optimal_players, len(matchday_players)):
                                if all(x in matchday_players for x in set(lucky_players)):
                                    next_fixture = fixture
                                    logging.debug(f'lucky players found: {lucky_players}')
                                    break
                                if next_fixture:
                                    break
                        else:
                            if all(x in matchday_players for x in optimal_players):
                                next_fixture = fixture
                                logging.debug(f'optimal players found: {optimal_players}')
                                break
                        if next_fixture:
                            break
                    if next_fixture:
                        break
                if next_fixture:
                    self.ordered_schedule += (next_fixture,)
                    schedule.remove(next_fixture)
                    add_to_matches_count(matchday_players)
                    logging.debug(f'fixture (stage {i}) found: {fixture}')
                    break

        logging.debug(f'ordered schedule: {self.ordered_schedule}')
        return self.ordered_schedule


class WrongNumberOfPlayersException(Exception):
    pass
