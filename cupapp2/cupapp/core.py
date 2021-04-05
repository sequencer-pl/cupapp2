import itertools
import logging
from random import shuffle

from logger.logging import logging_setup
logging_setup()


class Tournament:
    def __init__(self, home_slots, away_slots, players):
        logging_setup()
        self.home_slots = int(home_slots)
        self.away_slots = int(away_slots)
        self.players = players
        self.schedule = ()
        self.ordered_schedule = ()

    @staticmethod
    def create_rematch_round(schedule):
        rematch_round = ()
        for fixture in schedule:
            rematch_round += ((fixture[1], fixture[0]),)
        return rematch_round


class League(Tournament):
    def __init__(self, home_slots, away_slots, players):
        super().__init__(home_slots, away_slots, players)

    def create_schedule(self):
        if not self.home_slots or not self.away_slots \
                or len(self.players) < self.home_slots + self.away_slots:
            raise WrongNumberOfPlayersException

        for home in itertools.combinations(self.players, self.home_slots):
            for away_pos in itertools.combinations(self.players, self.away_slots):
                away_filtered = [p for p in away_pos if p not in home]
                if len(away_filtered) != self.away_slots:
                    continue
                away = tuple(away_filtered)
                fixture = (home, away)
                if (away, home) not in self.schedule:
                    self.schedule += (fixture,)
        self.ordered_schedule = self._order_schedule()
        return self.ordered_schedule

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
                    logging.debug(f'fixture (stage {i}) found: {next_fixture}')
                    break

        logging.debug(f'ordered schedule: {self.ordered_schedule}')
        return self.ordered_schedule


class SmartLeague(Tournament):
    def __init__(self, home_slots, away_slots, players):
        super().__init__(home_slots, away_slots, players)
        self.home_teams = []
        self.away_teams = []
        self.home_combinations = tuple(itertools.combinations(self.players, self.home_slots))
        away_combinations = list(itertools.combinations(self.players, self.away_slots))
        away_combinations.reverse()
        self.away_combinations = tuple(away_combinations)

    def next_round(self):
        self.home_teams, self.away_teams = list(self.home_combinations), list(self.away_combinations)
        self._set_equal_matches_count()
        self._match_home_to_away_teams()
        self._prepare_schedule()

    def _set_equal_matches_count(self):
        if len(self.home_teams) == len(self.away_teams):
            return
        elif len(self.home_teams) > len(self.away_teams):
            self.away_teams += self.away_combinations
        else:
            self.home_teams += self.home_combinations
        self._set_equal_matches_count()

    def _match_home_to_away_teams(self):
        schedule = []
        for i, h in enumerate(self.home_teams):
            for _ in range(i, len(self.away_teams)):
                if set(h) != set(h) - set(self.away_teams[i]) or {h, self.away_teams[i]} in schedule:
                    pop = self.away_teams.pop(i)
                    self.away_teams.append(pop)
                    continue
                schedule.append({h, self.away_teams[i]})
                break
        if len(schedule) != len(self.home_teams):
            for i in range(len(self.home_teams) - 1, 0, -1):
                if {self.home_teams[i], self.away_teams[i]} in schedule:
                    continue
                for j in range(i, 0, -1):
                    if set(self.away_teams[i]) == set(self.away_teams[i]) - set(self.home_teams[j]) \
                            and set(self.home_teams[i]) == set(self.home_teams[i]) - set(self.away_teams[j]):
                        i_to_sub = self.away_teams.pop(i)
                        j_to_sub = self.away_teams.pop(j)
                        self.away_teams.insert(j, i_to_sub)
                        self.away_teams.insert(i, j_to_sub)
                        schedule.pop(j)
                        schedule.append({self.home_teams[j], i_to_sub})
                        schedule.append({self.home_teams[i], j_to_sub})
                        break

    def _prepare_schedule(self):
        schedule = list(self.schedule)
        for i in range(len(self.home_teams)):
            fixture = (self.home_teams[i], self.away_teams[i])
            schedule.append(fixture)
        self.schedule = tuple(schedule)


class WrongNumberOfPlayersException(Exception):
    pass
