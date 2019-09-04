"""File to get raw data from nfl.com and process drives out of it.
Will likely be useful later when I need to get more data than just drive outcomes

4-Sep-2019: Mostly functional. A few small bugs that are noted, but most data is in and correct.
"""
# todo better documentation
import xmltodict
import dataclasses as dc
from dataclasses import dataclass
import urllib3
import logging
import pandas as pd
import time

# setup logging
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# class to contain yardline data. It comes to us as "TEAM yardline" like SEA 25, so include int (-50:50)
@dataclass
class Yardline:
    side: str
    side_pos: int
    yard_int: int


# class to contain Play data. Contains ugly if statement to calculate number of points to award
@dataclass
class Play:
    play_id: int
    pos_team: str
    description: str
    yardline: Yardline
    scoring_type: str = None
    scoring_team_abbr: str = None
    points: int = 0

    def calculate_points(self):
        if self.scoring_type is not None:
            if self.scoring_type == 'TD':
                self.points = 6
            elif self.scoring_type == 'FG':
                self.points = 3
            elif self.scoring_type == 'PAT':
                self.points = 1
            elif self.scoring_type == 'PAT2' or self.scoring_type == 'SFTY':
                self.points = 2
            else:
                logger.error('Unknown scoring type found: {}'.format(self.scoring_type))


# class to contain Drive data. Contains all plays in drive, and some post_init calculated fields
@dataclass
class Drive:
    drive_id: int
    start_time: str
    end_time: str
    plays: list
    pos_team: str
    drive_start: Yardline = dc.field(default=None, init=False)
    scoring_team: str = dc.field(default=None, init=False)
    points: int = dc.field(default=None, init=False)

    def __post_init__(self):
        [x.calculate_points() for x in self.plays]
        self.calculate_scoring()
        self.drive_start = self.calculate_drive_start(self.plays)

    # Function to calculate the starting yardline of a drive given the drive's plays
    # Complicated as some drives' first play has no yardline, hence the recursion
    # fixme this often gets kickoff's yardline, not actual drive start yardline
    def calculate_drive_start(self, plays_list):
        if plays_list[0].yardline is not None:
            return plays_list[0].yardline
        else:
            logger.debug("Drive's first play has no yardline: {}".format(plays_list[0]))
            return self.calculate_drive_start(plays_list[1:])

    def calculate_scoring(self):
        if any([x.points for x in self.plays]):
            self.points = sum([x.points for x in self.plays])
            scoring_team_list = [x.scoring_team_abbr for x in self.plays if x.points != 0]
            if all(x != scoring_team_list[0] for x in scoring_team_list):
                logger.error("Different teams are listed as scoring in this drive! {}".format(scoring_team_list))
            self.scoring_team = scoring_team_list[0]


# class to hold Game data. Has some fields meant to be input on init (from the NFL schedule XML)
# and some fields added later (from boxscorePbP XML)
@dataclass
class Game:
    season_year: int
    season_type: str
    game_week: int
    home_team: str
    away_team: str
    game_id: str
    drives: list = dc.field(default=None, init=False)
    home_score: int = dc.field(default=None, init=False)
    away_score: int = dc.field(default=None, init=False)

    def __repr__(self):
        str_rep = """{year}_{type}_{week}, id={game_id}\t{away} ({away_score}) vs. {home} ({home_score})"""\
            .format(year=self.season_year, type=self.season_type,
                    week=self.game_week, game_id=self.game_id,
                    away=self.away_team, home=self.home_team,
                    away_score=self.away_score, home_score=self.home_score)
        return str_rep

    # given the game id, get boxscorePbP XML and populate Drives objects and all other Game fields
    def get_game_details(self):
        # Build URL, get XML, convert to dict, get out and store easy values
        game_url = "http://www.nfl.com/feeds-rs/boxscorePbp/{}.xml".format(self.game_id)
        logger.debug('Getting game details {}'.format(game_url))
        xml_string = download_xml(game_url)
        game_dict = xmltodict.parse(xml_string, force_list={'play': True})['boxScorePBPFeed']
        self.home_score = game_dict['score']['homeTeamScore']['@pointTotal']
        self.away_score = game_dict['score']['visitorTeamScore']['@pointTotal']

        # Extract the 'drives'/'drive' dict and all data from within it
        drives_dict = game_dict['drives']['drive']
        drives_list = [Drive(int(float(x['@sequence'])),  # Python has some dumb bugs man
                             x['@startTime'],
                             x['@endTime'],
                             [Play(int(y.get('@playId', None)),
                                   y.get('@teamId', None),
                                   y.get('playDescription', None),
                                   Yardline(y.get('@yardlineSide'),
                                            y.get('@yardlineNumber'),
                                            (-1 if y['@teamId'] == y['@yardlineSide'] else 1) * (
                                                        50 - int(y['@yardlineNumber'])))
                                   if y.get('@yardlineSide') else None,
                                   y.get('@scoringType', None),
                                   y.get('@scoringTeamId', None))
                              for y in x['plays'].get('play')],
                             x['@possessionTeamAbbr']) for x in drives_dict]

        # fixme need to add drives/plays PATs after int/fumble returned for TD - they're on scoringplays at the top but not always in the data

        self.drives = drives_list
        self.check_score_integrity()

    # check to make sure that the number of points recorded within drives matches the top-level given result
    def check_score_integrity(self):
        drives_points = sum([x.points for y in self.drives for x in y.plays])
        game_points = int(self.home_score) + int(self.away_score)
        if drives_points == game_points:
            logger.debug('drives_points={}, game_points={}'.format(drives_points, game_points))
        else:
            logger.error('game_id={}, drives_points={}, game_points={}'
                         .format(self.game_id, drives_points, game_points))

    # smart export - since I only need drive result, make this a drive-level line-output for file storage
    def export(self):
        drive_list = []
        for drive in self.drives:
            drive_list.append({'game_id': self.game_id,
                               'season_year': self.season_year,
                               'season_type': self.season_type,
                               'game_week': self.game_week,
                               'home_team': self.home_team,
                               'away_team': self.away_team,
                               'drive_id': drive.drive_id,
                               'drive_pos_team': drive.pos_team,
                               'drive_start': drive.drive_start.yard_int,
                               'drive_num_plays': len(drive.plays),
                               'drive_scoring_team': drive.scoring_team,
                               'drive_points': drive.points
                               })
        return drive_list


# helper function to get the xml and ensure that status 200 is returned
def download_xml(path: str):
    http = urllib3.PoolManager()
    r = http.request('GET', path)
    assert r.status == 200
    time.sleep(2)
    return r.data


# function to get all games from a schedule file and build Game objects
def get_games(game_year: int):
    schedule_url = "http://www.nfl.com/feeds-rs/schedules/{}".format(game_year)
    xml_string = download_xml(schedule_url)

    game_dict = xmltodict.parse(xml_string)['gameSchedulesFeed']['gameSchedules']['gameSchedule']

    games_list = [Game(x['@season'],
                       x['@seasonType'],
                       int(x['@week']),
                       x['@homeTeamAbbr'],
                       x['@visitorTeamAbbr'],
                       x['@gameId']) for x in game_dict]

    return games_list


# get all schedule files 2009+, put all games in one list
games = []
for year in range(2009, 2010):
    games += get_games(year)

# using list of games, get game details and append full Game.export() dict to new list
games_dicts = []
for g in games:
    if g.season_type == 'REG':  # fixme There are some issues with POST - not willing to fix now
        g.get_game_details()
        logger.info(g)
        games_dicts += g.export()

# we have a list of dicts, one for every drive - turn into a pd.DataFrame and export
df = pd.DataFrame(games_dicts).set_index(['game_id', 'drive_id'])
df.to_parquet('drives_out.pq')