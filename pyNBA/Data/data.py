from nba_api.stats.endpoints import (LeagueGameFinder, CommonPlayerInfo, ShotChartDetail, BoxScoreTraditionalV2,
                                     BoxScoreAdvancedV2, BoxScoreMiscV2, BoxScoreScoringV2, LeagueDashPlayerBioStats,
                                     PlayerDashboardByGameSplits)
from pyNBA.Data.sql import SQL
from datetime import datetime
from functools import reduce
import pandas as pd
from collections import Counter
import time
import requests
from bs4 import BeautifulSoup
from pyNBA.Data.constants import (SEASONS, TRADITIONAL_BOXSCORE_COLUMNS, ADVANCED_BOXSCORE_COLUMNS,
                                  MISC_BOXSCORE_COLUMNS, SCORING_BOXSCORE_COLUMNS, TEAM_NAME_TO_ABBREVIATION,
                                  ABBREVIATION_TO_SITE, ID_TO_SITE, MIN_CONTEST_DATE, BAD_CONTEST_DATES,
                                  POSSIBLE_POSITIONS, BAD_CONTEST_IDS, BAD_OWNERSHIP_KEYS)


class UpdateData(object):
    def __init__(self, sql):
        self.sql = sql

    def update_game_data(self):
        query = """SELECT * FROM GAMES"""
        sql_data = self.sql.select_data(query)
        sql_ids = list(sql_data['ID'].unique())

        SEASONS.sort(reverse=True)
        for season in SEASONS:
            games = LeagueGameFinder(
                league_id_nullable='00', season_nullable=season, season_type_nullable='Regular Season'
                ).get_data_frames()[0]
            time.sleep(1.000)
            games = games.drop_duplicates(subset='GAME_ID')
            uninserted_games = games.loc[~games['GAME_ID'].isin(sql_ids)]
            for _, game in uninserted_games.iterrows():
                game_id = game['GAME_ID']
                matchup = game['MATCHUP'].split()
                if matchup[1] == '@':
                    home_team, away_team = matchup[2], matchup[0]
                else:
                    home_team, away_team = matchup[0], matchup[2]
                if game['TEAM_ABBREVIATION'] == home_team and game['WL'] == 'W':
                    winning_team = home_team
                else:
                    winning_team = away_team
                game = (game_id, season, game['GAME_DATE'], home_team, away_team, winning_team)
                self.sql.insert_game(game)

    def update_player_data(self):
        query = """SELECT * FROM PLAYERS"""
        sql_data = self.sql.select_data(query)
        sql_ids = list(sql_data['ID'].unique())

        SEASONS.sort(reverse=True)
        for season in SEASONS:
            player_bios = LeagueDashPlayerBioStats(season=season).get_data_frames()[0].fillna('')
            time.sleep(1.000)
            uninserted_players = player_bios.loc[~player_bios['PLAYER_ID'].isin(sql_ids)]
            for player_id, player in uninserted_players.groupby('PLAYER_ID'):
                player = player.iloc[0]

                player_id = str(player_id)
                draft_year = int(player['DRAFT_YEAR']) if player['DRAFT_YEAR'] not in ['Undrafted', ''] else -1
                draft_round = int(player['DRAFT_ROUND']) if player['DRAFT_ROUND'] not in ['Undrafted', ''] else -1
                draft_number = int(player['DRAFT_NUMBER']) if player['DRAFT_NUMBER'] not in ['Undrafted', ''] else -1
                weight = int(player['PLAYER_WEIGHT']) if player['PLAYER_WEIGHT'] != '' else -1
                height = int(player['PLAYER_HEIGHT_INCHES']) if player['PLAYER_HEIGHT_INCHES'] != '' else -1

                player_misc = CommonPlayerInfo(player_id=player_id).get_data_frames()[0].iloc[0].fillna('')
                time.sleep(1.000)

                birthdate = player_misc['BIRTHDATE']
                if birthdate != '':
                    birthdate = birthdate[0:10]

                player = (player_id, player['PLAYER_NAME'], player_misc['POSITION'], player['COLLEGE'],
                          player['COUNTRY'], height, weight, draft_year, draft_round, draft_number, birthdate)
                self.sql.insert_player(player)
                sql_ids.append(player_id)

    def update_boxscore_data(self, game_ids):
        query = """SELECT * FROM BOXSCORES"""
        sql_data = self.sql.select_data(query)
        sql_ids = list(sql_data['GAMEID'].unique())

        uninserted_game_ids = list(set(game_ids) - set(sql_ids))
        for game_id in uninserted_game_ids:
            temp = []

            traditional_boxscore = BoxScoreTraditionalV2(
                game_id=game_id
                ).get_data_frames()[0][TRADITIONAL_BOXSCORE_COLUMNS]
            advanced_boxscore = BoxScoreAdvancedV2(game_id=game_id).get_data_frames()[0][ADVANCED_BOXSCORE_COLUMNS]
            misc_boxscore = BoxScoreMiscV2(game_id=game_id).get_data_frames()[0][MISC_BOXSCORE_COLUMNS]
            scoring_boxscore = BoxScoreScoringV2(game_id=game_id, ).get_data_frames()[0][SCORING_BOXSCORE_COLUMNS]
            time.sleep(1.000)

            game_boxscore = reduce(lambda left, right: pd.merge(left, right, on=['GAME_ID', 'PLAYER_ID']),
                                   [traditional_boxscore, advanced_boxscore, misc_boxscore, scoring_boxscore])
            teams = game_boxscore['TEAM_ABBREVIATION'].unique()
            for _, player_boxscore in game_boxscore.groupby('PLAYER_ID'):
                player_boxscore = player_boxscore.iloc[0]

                player_id = str(player_boxscore['PLAYER_ID'])
                comment = player_boxscore['COMMENT'].strip()
                team = player_boxscore['TEAM_ABBREVIATION']
                opp_team = teams[0] if teams[1] == team else teams[1]

                if player_boxscore['MIN'] is None:
                    boxscore = (game_id, player_id, team, opp_team, comment,
                                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                else:
                    minutes_played, seconds_played = player_boxscore['MIN'].split(':')
                    seconds_played = int(minutes_played)*60 + int(seconds_played)
                    start = 0 if player_boxscore['START_POSITION'] == '' else 1

                    boxscore = (game_id, player_id, team, opp_team, comment,
                                start, seconds_played, int(player_boxscore['PTS']), int(player_boxscore['FGM']),
                                int(player_boxscore['FGA']), int(player_boxscore['FG3M']), int(player_boxscore['FG3A']),
                                int(player_boxscore['FTM']), int(player_boxscore['FTA']),
                                int(player_boxscore['PTS_OFF_TOV']), int(player_boxscore['PTS_2ND_CHANCE']),
                                int(player_boxscore['PTS_FB']), int(player_boxscore['PTS_PAINT']),
                                float(player_boxscore['PCT_AST_2PM']), float(player_boxscore['PCT_AST_3PM']),
                                int(player_boxscore['OREB']), float(player_boxscore['OREB_PCT']),
                                int(player_boxscore['DREB']), float(player_boxscore['DREB_PCT']),
                                int(player_boxscore['AST']), float(player_boxscore['AST_PCT']),
                                float(player_boxscore['AST_RATIO']), int(player_boxscore['STL']),
                                int(player_boxscore['BLK']), int(player_boxscore['TO']), int(player_boxscore['PF']),
                                int(player_boxscore['PLUS_MINUS']), float(player_boxscore['USG_PCT']),
                                float(player_boxscore['PACE']))
                temp.append(boxscore)

            for t in temp:
                self.sql.insert_boxscore(t)

    def update_shotchartdetail_data(self, game_player_tuples):
        query = """SELECT * FROM SHOTCHARTDETAILS"""
        sql_data = self.sql.select_data(query)
        subset = sql_data[['GAMEID', 'PLAYERID']]
        sql_game_player_tuples = set([tuple(x) for x in subset.to_numpy()])

        uninserted_game_player_tuples = game_player_tuples-sql_game_player_tuples
        for (game_id, player_id) in uninserted_game_player_tuples:
            temp = []

            shotchartdetails = ShotChartDetail(
                team_id=0, player_id=player_id, game_id_nullable=game_id, context_measure_simple='FGA'
                ).get_data_frames()[0]
            time.sleep(1.000)
            for _, shotchartdetail in shotchartdetails.iterrows():

                seconds_remaining = shotchartdetail['MINUTES_REMAINING']*60 + shotchartdetail['SECONDS_REMAINING']
                shotchartdetail = (game_id, shotchartdetail['GAME_EVENT_ID'], player_id, shotchartdetail['PERIOD'],
                                   seconds_remaining, shotchartdetail['EVENT_TYPE'], shotchartdetail['ACTION_TYPE'],
                                   shotchartdetail['SHOT_TYPE'], shotchartdetail['SHOT_ZONE_BASIC'],
                                   shotchartdetail['SHOT_ZONE_AREA'], shotchartdetail['SHOT_ZONE_RANGE'],
                                   shotchartdetail['SHOT_DISTANCE'])
                temp.append(shotchartdetail)

            for t in temp:
                self.sql.insert_shotchartdetail(t)

    def update_odds_data(self, game_dates):
        query = """SELECT * FROM ODDS"""
        sql_data = self.sql.select_data(query)
        sql_dates = set(sql_data['DATE'].unique())

        uninserted_game_dates = game_dates - sql_dates
        for date in uninserted_game_dates:
            temp = []

            formatted_date = date.replace('-', '')
            URL = 'https://www.sportsbookreview.com/betting-odds/nba-basketball/money-line/?date=' + formatted_date
            page = requests.get(URL)
            soup = BeautifulSoup(page.content, 'html.parser')

            results = soup.find_all('a', class_='_3qi53')
            for result in results[::2]:
                href = result['href']
                URL = 'https://www.sportsbookreview.com' + href

                page = requests.get(URL)
                soup = BeautifulSoup(page.content, 'html.parser')
                print(URL + '...')

                all_results = soup.find('section', class_='_2LZJ_')

                period_results = all_results.find_all('div', class_='_398eq')

                for period_result in period_results:
                    period = period_result.h2.text

                    teams = period_result.find_all('span', class_='_3O1Gx')
                    lines = period_result.find_all('span', class_='opener')

                    ps1_i = 2
                    if lines[ps1_i].text == '-':
                        ps2_i = ps1_i + 1
                    else:
                        ps2_i = ps1_i + 2

                    if lines[ps2_i].text == '-':
                        ml1_i = ps2_i + 3
                    else:
                        ml1_i = ps2_i + 4
                    ml2_i = ml1_i + 1

                    t1_i = ml2_i + 3
                    if lines[t1_i].text == '-':
                        t2_i = t1_i + 1
                    else:
                        t2_i = t1_i + 2

                    team_1 = TEAM_NAME_TO_ABBREVIATION[teams[0].text]
                    odds_1 = (date, team_1, period, lines[ps1_i].text.replace('½', '.5'), lines[ml1_i].text,
                              lines[t1_i].text.replace('½', '.5'))
                    temp.append(odds_1)

                    team_2 = TEAM_NAME_TO_ABBREVIATION[teams[1].text]
                    odds_2 = (date, team_2, period, lines[ps2_i].text.replace('½', '.5'), lines[ml2_i].text,
                              lines[t2_i].text.replace('½', '.5'))
                    temp.append(odds_2)

            for t in temp:
                self.sql.insert_odds(t)

    def update_quarterly_boxscore_data(self, tuples):
        query = """SELECT * FROM QUARTERLYBOXSCORES"""
        sql_data = self.sql.select_data(query)
        subset = sql_data[['SEASON', 'GAMEID', 'DATE', 'PLAYERID']]
        sql_tuples = set([tuple(x) for x in subset.to_numpy()])

        uninserted_tuples = tuples - sql_tuples
        for (season, game_id, date, player_id) in uninserted_tuples:
            temp = []

            quarterly_boxscore = PlayerDashboardByGameSplits(
                player_id=player_id, season=season, date_from_nullable=date, date_to_nullable=date
                ).get_data_frames()[2]
            time.sleep(1.000)

            for quarter, quarter_boxscore in quarterly_boxscore.groupby('GROUP_VALUE'):
                quarter_boxscore = quarter_boxscore.iloc[0]

                seconds_played = int(quarter_boxscore['MIN']*60)

                boxscore = (season, game_id, date, player_id, quarter, seconds_played,
                            int(quarter_boxscore['PTS']), int(quarter_boxscore['FGM']),
                            int(quarter_boxscore['FGA']), int(quarter_boxscore['FG3M']), int(quarter_boxscore['FG3A']),
                            int(quarter_boxscore['FTM']), int(quarter_boxscore['FTA']),
                            int(quarter_boxscore['OREB']), int(quarter_boxscore['DREB']), int(quarter_boxscore['AST']),
                            int(quarter_boxscore['STL']), int(quarter_boxscore['BLK']), int(quarter_boxscore['TOV']),
                            int(quarter_boxscore['PF']), int(quarter_boxscore['PLUS_MINUS']))
                temp.append(boxscore)

            for t in temp:
                self.sql.insert_quarterly_boxscore(t)

    def update_salary_data(self, game_dates):
        query = """SELECT * FROM SALARIES"""
        sql_data = self.sql.select_data(query)
        sql_dates = set(sql_data['DATE'].unique())

        uninserted_game_dates = game_dates - sql_dates
        for date in uninserted_game_dates:
            temp = []
            for site_abbreviation in ABBREVIATION_TO_SITE:
                date_list = date.split('-')
                year, month, day = date_list[0], date_list[1], date_list[2]
                URL = 'http://rotoguru1.com/cgi-bin/hyday.pl?game={}&mon={}&day={}&year={}'.format(
                    site_abbreviation, month, day, year
                    )
                page = requests.get(URL)
                soup = BeautifulSoup(page.content, 'html.parser')

                temp_positions = soup.find_all('td')
                positions = []
                for t in temp_positions:
                    text = t.text
                    text_list = text.split('/')
                    is_position = True
                    for text in text_list:
                        if text not in POSSIBLE_POSITIONS:
                            is_position = False
                    if is_position:
                        positions.append('_'.join(text_list))

                players = soup.find_all('a', {'target': '_blank'})
                players = [i for i in players if 'playrh' in i['href'] and i.text != 'Player Lookup']

                salaries = soup.find_all('td', {'align': 'right'})
                salaries = [i for i in salaries if '$' in i.text]

                for player, position, salary in zip(players, positions, salaries):
                    salary = int(salary.text.replace('$', '').replace(',', ''))
                    data = (ABBREVIATION_TO_SITE[site_abbreviation], date, player.text, position, salary)
                    temp.append(data)

            for t in temp:
                self.sql.insert_salary(t)

    def update_contest_data(self, game_dates):
        query = """SELECT * FROM CONTESTS"""
        sql_data = self.sql.select_data(query)
        sql_dates = set(sql_data['DATE'].unique())

        uninserted_game_dates = list((game_dates - sql_dates) - BAD_CONTEST_DATES)
        uninserted_game_dates = [i for i in uninserted_game_dates if i >= MIN_CONTEST_DATE]
        uninserted_game_dates.sort()
        for date in uninserted_game_dates:
            temp = []

            formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%y')
            SLATES_URL = 'https://resultsdb-api.rotogrinders.com/api/slates?start={}&lean=True'.format(formatted_date)
            slate_data = requests.get(SLATES_URL).json()

            for slate in slate_data:
                if slate['sport'] != 3:
                    continue

                site_id = slate['siteId']
                if site_id in ID_TO_SITE:
                    site = ID_TO_SITE[site_id]
                else:
                    print('Site ID {} not supported'.format(str(site_id)))
                    continue

                slate_id = slate['_id']
                slate_type = slate['slateTypeName']
                game_count = slate['gameCount']

                players = slate['slatePlayers']
                teams = Counter()
                for player in players:
                    if 'team' in player:
                        team = player['team']
                        teams[team] += 1
                most_common = teams.most_common(game_count*2)
                most_common = [i[0] for i in most_common]
                teams = '_'.join(most_common)

                CONTEST_URL = 'https://resultsdb-api.rotogrinders.com/api/contests?slates={}&lean=true'.format(slate_id)
                contest_data = requests.get(CONTEST_URL).json()

                for contest in contest_data:
                    if contest['sport'] != 3:
                        continue

                    entries = contest['entryCount']
                    if entries == 0:
                        continue

                    contest_id = contest['_id']
                    contest_name = contest['name']
                    prize_pool = contest['prizePool']
                    entry_fee = contest['entryFee']
                    max_entries_per_user = contest['maxEntriesPerUser']

                    top = contest['prizes'][0]
                    if 'value' in top:
                        top_prize = top['value']
                    elif 'cash' in top:
                        top_prize = top['cash']
                    else:
                        continue

                    SUMMARY_URL = 'https://resultsdb-api.rotogrinders.com/api/slates/{}/summary'.format(slate_id)

                    try:
                        summary_data = requests.get(SUMMARY_URL).json()['winnerMap'][contest_id]
                        cash_line = summary_data['cashLine']
                        winning_score = summary_data['score']
                    except Exception:
                        cash_line = None
                        winning_score = None

                    data = (site, date, slate_id, slate_type, game_count, teams, contest_id, contest_name, prize_pool,
                            entry_fee, top_prize, max_entries_per_user, entries, cash_line, winning_score)
                    temp.append(data)

            for t in temp:
                self.sql.insert_contest(t)

    def update_contest_info_data(self, contest_ids):
        query = """SELECT * FROM CONTESTINFO"""
        sql_data = self.sql.select_data(query)
        sql_ids = set(sql_data['CONTESTID'].unique())

        uninserted_contest_ids = list((contest_ids - sql_ids) - BAD_CONTEST_IDS)

        uninserted_contest_ids.sort()
        for contest_id in uninserted_contest_ids:
            prizes = {}
            prev_prize = None
            prev_points = None
            prev_rank = None

            index = 0
            while True:
                ENTRY_URL = (
                    "https://resultsdb-api.rotogrinders.com/api/entries?_contestId={}&sortBy=points&"
                    "order=desc&index={}&users=false&isLive=false&incomplete=false").format(contest_id, str(index))
                entry_data = requests.get(ENTRY_URL).json()['entries']
                if len(entry_data) == 0 and (not bool(prizes)):
                    break

                for entry in entry_data:
                    rank = entry['rank']
                    points = entry['points']
                    if 'prize' in entry:
                        prize = entry['prize']['cash']
                    else:
                        prize = 0

                    if prize not in prizes:
                        prizes[prize] = {}
                        prizes[prize]['MAXPOINTS'] = points
                        prizes[prize]['MINRANK'] = rank

                        if prev_prize is not None:
                            prizes[prev_prize]['MINPOINTS'] = prev_points
                            prizes[prev_prize]['MAXRANK'] = prev_rank

                    prev_prize = prize
                    prev_rank = rank
                    prev_points = points

                if prize == 0 or len(entry_data) == 0:
                    prizes[prize]['MINPOINTS'] = None
                    prizes[prize]['MAXRANK'] = None
                    break

                index += 1

            for prize in prizes:
                data = (contest_id, prize, prizes[prize]['MINPOINTS'], prizes[prize]['MAXPOINTS'],
                        prizes[prize]['MINRANK'], prizes[prize]['MAXRANK'])
                self.sql.insert_contest_info(data)

    def update_ownership_data(self, slate_ids):
        query = """SELECT * FROM OWNERSHIP"""
        sql_data = self.sql.select_data(query)
        sql_ids = set(sql_data['SLATEID'].unique())

        uninserted_slate_ids = list(slate_ids - sql_ids)

        uninserted_slate_ids.sort()
        for slate_id in uninserted_slate_ids:
            temp = []

            URL = "https://resultsdb-api.rotogrinders.com/api/contest-ownership?_slateId={}".format(slate_id)
            ownership_data = requests.get(URL).json()

            for player_name in ownership_data:
                player_ownership_data = ownership_data[player_name]
                for contest_name in player_ownership_data:
                    if contest_name not in BAD_OWNERSHIP_KEYS:
                        ownership = player_ownership_data[contest_name]
                        data = (slate_id, player_name, contest_name, ownership)
                        temp.append(data)

            for t in temp:
                self.sql.insert_ownership(t)


class QueryData(object):
    def __init__(self, update=False):
        self.sql = SQL()
        self.sql.create_connection()
        self.update = update
        self.update_data = UpdateData(sql=self.sql)

    def query_game_data(self):
        if self.update:
            self.update_data.update_game_data()
        query = """SELECT * FROM GAMES"""
        sql_data = self.sql.select_data(query)
        return sql_data

    def query_player_data(self):
        if self.update:
            self.update_data.update_player_data()
        query = """SELECT * FROM PLAYERS"""
        sql_data = self.sql.select_data(query)
        return sql_data

    def query_boxscore_data(self):
        if self.update:
            game_data = self.query_game_data()
            game_ids = game_data['ID'].tolist()
            self.update_data.update_boxscore_data(game_ids)
        query = """SELECT * FROM BOXSCORES"""
        sql_data = self.sql.select_data(query)

        game_data = self.query_game_data()
        player_data = self.query_player_data()
        sql_data = sql_data.merge(game_data, left_on='GAMEID', right_on='ID').merge(
            player_data, left_on='PLAYERID', right_on='ID'
            )
        return sql_data

    def query_shotchartdetail_data(self):
        if self.update:
            boxscore_data = self.query_boxscore_data()
            subset = boxscore_data.loc[boxscore_data['FGA'] > 0, ['GAMEID', 'PLAYERID']]
            game_player_tuples = set([tuple(x) for x in subset.to_numpy()])
            self.update_data.update_shotchartdetail_data(game_player_tuples)
        query = """SELECT * FROM SHOTCHARTDETAILS"""
        sql_data = self.sql.select_data(query)
        return sql_data

    def query_odds_data(self):
        if self.update:
            game_data = self.query_game_data()
            game_dates = set(game_data['DATE'].unique())
            self.update_data.update_odds_data(game_dates)
        query = """SELECT * FROM ODDS"""
        sql_data = self.sql.select_data(query)
        return sql_data

    def query_quarterly_boxscore_data(self):
        if self.update:
            boxscore_data = self.query_boxscore_data()
            boxscore_data = boxscore_data.loc[~(boxscore_data['SECONDSPLAYED'] == 0)]
            subset = boxscore_data[['SEASON', 'GAMEID', 'DATE', 'PLAYERID']]
            tuples = set([tuple(x) for x in subset.to_numpy()])
            self.update_data.update_quarterly_boxscore_data(tuples)
        query = """SELECT * FROM QUARTERLYBOXSCORES"""
        sql_data = self.sql.select_data(query)
        return sql_data

    def query_salary_data(self):
        if self.update:
            game_data = self.query_game_data()
            game_dates = set(game_data['DATE'].unique())
            self.update_data.update_salary_data(game_dates)
        query = """SELECT * FROM SALARIES"""
        sql_data = self.sql.select_data(query)
        return sql_data

    def query_contest_data(self):
        if self.update:
            game_data = self.query_game_data()
            game_dates = set(game_data['DATE'].unique())
            self.update_data.update_contest_data(game_dates)
        query = """SELECT * FROM CONTESTS"""
        sql_data = self.sql.select_data(query)
        return sql_data

    def query_contest_info_data(self):
        if self.update:
            contest_data = self.query_contest_data()
            contest_ids = set(contest_data['CONTESTID'].unique())
            self.update_data.update_contest_info_data(contest_ids)
        query = """SELECT * FROM CONTESTINFO"""
        sql_data = self.sql.select_data(query)
        return sql_data

    def query_ownership_data(self):
        if self.update:
            contest_data = self.query_contest_data()
            slate_ids = set(contest_data['SLATEID'].unique())
            self.update_data.update_ownership_data(slate_ids)
        query = """SELECT * FROM OWNERSHIP"""
        sql_data = self.sql.select_data(query)
        return sql_data
