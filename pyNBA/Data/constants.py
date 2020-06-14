SEASONS = ['2014-15', '2015-16', '2016-17', '2017-18', '2018-19', '2019-20']

TRADITIONAL_BOXSCORE_COLUMNS = ['GAME_ID', 'PLAYER_ID', 'TEAM_ABBREVIATION', 'START_POSITION', 'MIN',
                                    'PTS', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'OREB', 'DREB',
                                    'AST', 'STL', 'BLK', 'TO', 'PF', 'PLUS_MINUS', 'COMMENT']
ADVANCED_BOXSCORE_COLUMNS = ['GAME_ID', 'PLAYER_ID', 'OREB_PCT', 'DREB_PCT', 'AST_PCT', 'AST_RATIO',
                                'USG_PCT', 'PACE']
MISC_BOXSCORE_COLUMNS = ['GAME_ID', 'PLAYER_ID', 'PTS_OFF_TOV', 'PTS_2ND_CHANCE', 'PTS_FB', 'PTS_PAINT']
SCORING_BOXSCORE_COLUMNS = ['GAME_ID', 'PLAYER_ID', 'PCT_AST_2PM', 'PCT_AST_3PM']

TEAM_NAME_TO_ABBREVIATION = {
    'Atlanta' : 'ATL',
    'Boston': 'BOS',
    'Brooklyn': 'BKN',
    'Charlotte': 'CHA',
    'Chicago': 'CHI',
    'Cleveland': 'CLE',
    'Dallas': 'DAL',
    'Denver': 'DEN',
    'Detroit': 'DET',
    'Golden State': 'GSW',
    'Houston': 'HOU',
    'Indiana': 'IND',
    'L.A. Clippers': 'LAC',
    'L.A. Lakers': 'LAL',
    'Memphis': 'MEM',
    'Miami': 'MIA',
    'Milwaukee': 'MIL',
    'Minnesota': 'MIN',
    'New Orleans': 'NOP',
    'New York': 'NYK',
    'Oklahoma City': 'OKC',
    'Orlando': 'ORL',
    'Philadelphia': 'PHI',
    'Phoenix': 'PHX',
    'Portland': 'POR',
    'Sacramento': 'SAC',
    'San Antonio': 'SAS',
    'Toronto': 'TOR',
    'Utah': 'UTA',
    'Washington': 'WAS'
}

ABBREVIATION_TO_SITE = {
    'dk': 'DRAFTKINGS',
    'fd': 'FANDUEL'
}

ID_TO_SITE = {
    20: 'DRAFTKINGS'
}

MIN_CONTEST_DATE = '2017-07-14'

BAD_CONTEST_DATES = set(['2017-11-21', '2020-01-09'])