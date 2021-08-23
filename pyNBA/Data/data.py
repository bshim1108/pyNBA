import json
import time
import requests
import pandas as pd
from functools import reduce
from bs4 import BeautifulSoup
from collections import Counter
from datetime import datetime, timedelta
from pyNBA.Data.sql import SQL
from pyNBA.Data.helpers import Helpers
from nba_api.stats.endpoints import (LeagueGameFinder, CommonPlayerInfo, ShotChartDetail, BoxScoreTraditionalV2,
                                     BoxScoreAdvancedV2, BoxScoreMiscV2, BoxScoreScoringV2, LeagueDashPlayerBioStats,
                                     PlayerDashboardByGameSplits)
from pyNBA.Data.constants import (SEASONS, TRADITIONAL_BOXSCORE_COLUMNS, ADVANCED_BOXSCORE_COLUMNS,
                                  MISC_BOXSCORE_COLUMNS, SCORING_BOXSCORE_COLUMNS, TEAM_NAME_TO_ABBREVIATION,
                                  ABBREVIATION_TO_SITE, ID_TO_SITE, MIN_CONTEST_DATE, BAD_CONTEST_DATES,
                                  POSSIBLE_POSITIONS, BAD_CONTEST_IDS, BAD_OWNERSHIP_KEYS, SEASON_TYPES,
                                  DAILY_FANTASY_FUEL_START_DATE, DAILY_FANTASY_FUEL_SITES,
                                  DAILY_FANTASY_FUEL_BAD_DATES, ROTOWIRE_START_DATE, BAD_ROTOGURU_DATES,
                                  LINESTARAPP_SITEID_TO_SITE, LINESTARAPP_MIN_PID, LINESTARAPP_INVALID_PID_RANGE,
                                  LINESTARAPP_INVALID_PID_VALUES, LINESTARAPP_MIN_DEF_PID)

class UpdateData(object):
    def __init__(self, sql):
        self.sql = sql
        self.helpers = Helpers()

    def update_game_data(self):
        query = """SELECT * FROM GAMES"""
        sql_data = self.sql.select_data(query)
        sql_ids = list(sql_data['ID'].unique())

        for season in SEASONS:
            for season_type in SEASON_TYPES:
                games = LeagueGameFinder(
                    league_id_nullable='00', season_nullable=season, season_type_nullable=season_type
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
                    game = (game_id, season, season_type, game['GAME_DATE'], home_team, away_team, winning_team)
                    self.sql.insert_game(game)

    def update_player_data(self):
        for season in SEASONS:
            print(season)
            player_bios = LeagueDashPlayerBioStats(season=season).get_data_frames()[0].fillna('')
            time.sleep(1.000)

            query = """SELECT * FROM PLAYERS"""
            sql_data = self.sql.select_data(query)
            sql_ids = list(sql_data['ID'].unique())
            sql_ids = [int(i) for i in sql_ids]
            uninserted_players = player_bios.loc[~player_bios['PLAYER_ID'].isin(sql_ids)]
            for player_id, player in uninserted_players.groupby('PLAYER_ID'):
                print(player_id)
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
        uninserted_game_ids.sort()
        for game_id in uninserted_game_ids:
            print(game_id)
            temp = []

            attempts_boxscores = self.helpers.get_attempts_boxscores(game_id)
            if attempts_boxscores.empty:
                print('Could not construct attempts boxscores for game_id: {}'.format(game_id))
                continue

            traditional_boxscores = BoxScoreTraditionalV2(
                game_id=game_id
                ).get_data_frames()[0][TRADITIONAL_BOXSCORE_COLUMNS]
            advanced_boxscores = BoxScoreAdvancedV2(game_id=game_id).get_data_frames()[0][ADVANCED_BOXSCORE_COLUMNS]
            misc_boxscores = BoxScoreMiscV2(game_id=game_id).get_data_frames()[0][MISC_BOXSCORE_COLUMNS]
            scoring_boxscores = BoxScoreScoringV2(game_id=game_id).get_data_frames()[0][SCORING_BOXSCORE_COLUMNS]
            time.sleep(1.000)

            game_boxscores = reduce(
                lambda left, right: pd.merge(left, right, on=['GAME_ID', 'PLAYER_ID']),
                [traditional_boxscores, advanced_boxscores, misc_boxscores, scoring_boxscores]
                )
            game_boxscores = game_boxscores.merge(attempts_boxscores, on=['GAME_ID', 'PLAYER_ID'], how='left')
            game_boxscores[attempts_boxscores.columns] = game_boxscores[attempts_boxscores.columns].fillna(0)

            if game_boxscores['PTS'].sum() == 0:
                print('Boxscores empty for game_id: {}'.format(game_id))
                continue

            teams = game_boxscores['TEAM_ABBREVIATION'].unique()
            for _, player_boxscore in game_boxscores.groupby('PLAYER_ID'):
                player_boxscore = player_boxscore.iloc[0]

                player_id = str(player_boxscore['PLAYER_ID'])
                comment = player_boxscore['COMMENT'].strip()
                team = player_boxscore['TEAM_ABBREVIATION']

                if len(teams) < 2:
                    opp_team = '???'
                elif teams[1] == team:
                    opp_team = teams[0]
                else:
                    opp_team = teams[1]

                if player_boxscore['MIN'] is None:
                    boxscore = (game_id, player_id, team, opp_team, comment,
                                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                else:
                    minutes_played, seconds_played = player_boxscore['MIN'].split(':')
                    seconds_played = int(minutes_played)*60 + int(seconds_played)
                    start = 0 if player_boxscore['START_POSITION'] == '' else 1
                    pct_ast_2pm = float(player_boxscore['PCT_AST_2PM']) if player_boxscore['PCT_AST_2PM'] is not None else 0
                    pct_ast_3pm = float(player_boxscore['PCT_AST_3PM']) if player_boxscore['PCT_AST_3PM'] is not None else 0

                    boxscore = (game_id, player_id, team, opp_team, comment,
                                start, seconds_played, int(player_boxscore['PTS']), int(player_boxscore['FGM']),
                                int(player_boxscore['FGA']), int(player_boxscore['FG3M']), int(player_boxscore['FG3A']),
                                int(player_boxscore['FTM']), int(player_boxscore['FTA']),
                                int(player_boxscore['PTS_OFF_TOV']), int(player_boxscore['PTS_2ND_CHANCE']),
                                int(player_boxscore['PTS_FB']), int(player_boxscore['PTS_PAINT']),
                                pct_ast_2pm, pct_ast_3pm,
                                int(player_boxscore['OREB']), float(player_boxscore['OREB_PCT']),
                                int(player_boxscore['DREB']), float(player_boxscore['DREB_PCT']),
                                int(player_boxscore['AST']), float(player_boxscore['AST_PCT']),
                                float(player_boxscore['AST_RATIO']), int(player_boxscore['STL']),
                                int(player_boxscore['BLK']), int(player_boxscore['TO']), int(player_boxscore['PF']),
                                int(player_boxscore['PLUS_MINUS']), float(player_boxscore['USG_PCT']),
                                float(player_boxscore['PACE']), float(player_boxscore['POSS']),
                                int(player_boxscore['TOTAL_ATTEMPTS']), int(player_boxscore['TOTAL_PTS']),
                                int(player_boxscore['TOTAL_FTA']), int(player_boxscore['TOTAL_FTM']),
                                int(player_boxscore['SHOT_ATTEMPTS']), int(player_boxscore['SHOT_PTS']),
                                int(player_boxscore['SHOT_FTA']), int(player_boxscore['SHOT_FTM']),
                                int(player_boxscore['SFOUL_ATTEMPTS']), int(player_boxscore['SFOUL_PTS']),
                                int(player_boxscore['SFOUL_FTA']), int(player_boxscore['SFOUL_FTM']),
                                int(player_boxscore['PFOUL_ATTEMPTS']), int(player_boxscore['PFOUL_PTS']),
                                int(player_boxscore['PFOUL_FTA']), int(player_boxscore['PFOUL_FTM']),
                                int(player_boxscore['TFOUL_ATTEMPTS']), int(player_boxscore['TFOUL_PTS']),
                                int(player_boxscore['TFOUL_FTA']), int(player_boxscore['TFOUL_FTM']))

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
        headers = {
            'User-Agent': 'My User Agent 1.0'
        }

        query = """SELECT * FROM ODDS"""
        sql_data = self.sql.select_data(query)
        sql_dates = set(sql_data['DATE'].unique())

        uninserted_game_dates = game_dates - sql_dates
        for date in uninserted_game_dates:
            temp = []

            formatted_date = date.replace('-', '')
            URL = 'https://www.sportsbookreview.com/betting-odds/nba-basketball/money-line/?date=' + formatted_date
            page = requests.get(URL, headers=headers)
            time.sleep(1.000)
            soup = BeautifulSoup(page.content, 'html.parser')

            results = soup.find_all('a', class_='gradientContainer-3iN6G')
            for result in results[::2]:
                href = result['href']
                URL = 'https://www.sportsbookreview.com' + href

                page = requests.get(URL, headers=headers)
                time.sleep(1.000)
                soup = BeautifulSoup(page.content, 'html.parser')
                print(URL + '...')

                all_results = soup.find('section', class_='mainColumn-iBrA5')

                period_results = all_results.find_all('div', class_='container-2fbfV')

                for period_result in period_results:
                    period = period_result.h2.text

                    teams = period_result.find_all('span', class_='participantBox-3ar9Y')
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

    def update_quarterly_boxscore_data(self, tuples, boxscores):
        query = """SELECT * FROM QUARTERLYBOXSCORES"""
        sql_data = self.sql.select_data(query)
        subset = sql_data[['SEASON', 'GAMEID', 'DATE', 'PLAYERID']]
        sql_tuples = set([tuple(x) for x in subset.to_numpy()])

        uninserted_tuples = tuples - sql_tuples
        uninserted_boxscores = boxscores.loc[
            boxscores[['SEASON', 'GAMEID', 'DATE', 'PLAYERID']].apply(
                lambda x: tuple(x.to_numpy()) in uninserted_tuples, axis=1
                )
        ]
        subset = uninserted_boxscores[['SEASON', 'SEASONTYPE', 'GAMEID', 'DATE', 'PLAYERID']]
        tuples = [tuple(x) for x in subset.to_numpy()]
        tuples.sort()


        num = len(tuples)
        i = 0
        for (season, season_type, game_id, date, player_id) in tuples:
            print('{}/{}'.format(str(i), str(num)))
            i += 1
            temp = []

            quarterly_boxscore = PlayerDashboardByGameSplits(
                player_id=player_id, season=season, date_from_nullable=date, date_to_nullable=date,
                season_type_playoffs=season_type
                ).get_data_frames()[2]
            time.sleep(1.000)

            if quarterly_boxscore.empty:
                raise Exception('Quarterly boxscore empty for tuple: ({}, {}, {}, {}, {})'.format(
                season, season_type, game_id, date, player_id
                ))

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

        uninserted_game_dates = list(game_dates - sql_dates)
        uninserted_game_dates.sort()
        for date in uninserted_game_dates:
            if date in BAD_ROTOGURU_DATES:
                continue
            print(date)
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
            print(date)
            temp = []

            formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%y')
            SLATES_URL = 'https://resultsdb-api.rotogrinders.com/api/slates?start={}&lean=True'.format(formatted_date)
            print(SLATES_URL)
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

    def update_daily_fantasy_fuel_data(self, game_dates):
        query = """SELECT * FROM DAILY_FANTASY_FUEL_PROJECTIONS"""
        sql_data = self.sql.select_data(query)
        sql_dates = set(sql_data['DATE'].unique())

        uninserted_game_dates = list(game_dates - sql_dates)
        uninserted_game_dates.sort()
        for date in uninserted_game_dates:
            is_too_early = pd.to_datetime(date) < pd.to_datetime(DAILY_FANTASY_FUEL_START_DATE)
            is_bad_date = date in DAILY_FANTASY_FUEL_BAD_DATES
            if is_too_early or is_bad_date:
                continue
            print(date)
            temp = []
            for site in DAILY_FANTASY_FUEL_SITES:
                URL = f'https://www.dailyfantasyfuel.com/nba/projections/{site}/{date}/'
                res = requests.get(URL)
                res.encoding = 'utf-8'
                res.raise_for_status()
                html = res.text

                soup = BeautifulSoup(html, 'html.parser')

                all_players = soup.find_all('tr', {'class': 'projections-listing'})
                for player in all_players:
                    l5_fp_min = player['data-ppg_min'] if player['data-ppg_min'] != '' else None
                    l5_fp_avg = player['data-ppg_avg'] if player['data-ppg_avg'] != '' else None
                    l5_fp_max = player['data-ppg_max'] if player['data-ppg_max'] != '' else None
                    player_info = (
                        site, date, player['data-name'], player['data-pos'], player['data-salary'],
                        player['data-inj'] , player['data-team'], player['data-opp'],
                        l5_fp_min, l5_fp_avg, l5_fp_max, player['data-ppg_proj'],
                        player['data-ou'], player['data-spread'], player['data-proj_score']
                    )
                    temp.append(player_info)

            for t in temp:
                self.sql.insert_daily_fantasy_fuel_projections(t)

    def update_rotowire_data(self, game_dates):
        query = """SELECT * FROM ROTOWIRE_PROJECTIONS"""
        sql_data = self.sql.select_data(query)
        sql_dates = set(sql_data['DATE'].unique())

        uninserted_game_dates = list(game_dates - sql_dates)
        uninserted_game_dates.sort()
        for date in uninserted_game_dates:
            is_too_early = pd.to_datetime(date) < pd.to_datetime(ROTOWIRE_START_DATE)
            if is_too_early:
                continue
            print(date)
            temp = []

            headers = {
                'Cookie': '_dlt=1; __gads=ID=5058a19006cea8ef-22ee9863bbba0089:T=1628913231:RT=1628990961:S=ALNI_MYB4_WnqAtZNyJ8aGMxonI_Lk4e5Q; _ga=GA1.2.1290194056.1628913231; _ga_DJZM5GNYZ8=GS1.1.1628990184.4.1.1628990960.0; _gid=GA1.2.640401548.1628913231; _uetsid=3c53b7d0fcb311eb9b3b99c01437cc0a; _uetvid=3c53e940fcb311eb89bff796026097a5; _pbjs_userid_consent_data=3524755945110770; cto_bidid=YSRDFl95anJGTm5NZ0tlS0U0cWdkcUx6dHBVJTJCdHlEWDdudkVGanlHUjkyU2cyQ2xSWFlNMVMwYVdDT1VFdWNHdyUyQjNHMlg0aWxZNzVDMnl5Q3MyaFRUTTBPVnRvJTJGdGZRSm84SHNpSFZ5S243WjBPc2JJNlljY2h2cWs3cjRZSlpGZGxxaA; cto_bundle=o80dIF85ZHhDWFZTSkk1Y0JVbUlMeTRPcG5zeiUyRjlmdHRWeVQ5NXdCSktNNkNtVnBWNzdxVVdudCUyRjlLVWhUSVBodW1tZVFkYyUyQlVSNzhnSkM4Y2FscEV6NVBFSW5oMmxsTnd3R2JZTXNsMTl3cEkzOW53UW1QRzQ5aGkyWTA0V3dmeWhBMFExdUxFN1Y1YkNOaVd6Z1lzbUN5JTJGbmZYUGI0RVJ6V3IxMWFDbzUyb1I1byUzRA; _dlt=1; _dc_gtm_UA-3226863-14=1; PHPSESSID=cf11b6b937dbc6d592ffc245efafac36; _dc_gtm_UA-3226863-1=1; _dc_gtm_UA-3226863-15=1; used_site_rw=nba-main%7C; used_site_rw_exp=1629010800; rwnav_NBA=Fantasy; _fbp=fb.1.1628990839537.931434173; RW_orderTotal=6.99; _lr_env_src_ats=false; _lr_retry_request=true; amplitude_id_c2c7a484a98d5a16340469d0baf32aefrotowire.com=eyJkZXZpY2VJZCI6Ijc1YTllYTgyLTMzOTgtNGE0OS05MmVjLTQ0NmQ4NGJjZTM5MVIiLCJ1c2VySWQiOm51bGwsIm9wdE91dCI6ZmFsc2UsInNlc3Npb25JZCI6MTYyODkxMzIzMDY4OSwibGFzdEV2ZW50VGltZSI6MTYyODkxMzI1NTQ3MywiZXZlbnRJZCI6MCwiaWRlbnRpZnlJZCI6MCwic2VxdWVuY2VOdW1iZXIiOjB9; cookie=%7B%22id%22%3A%2201FD1CPZZ6D92SK3ETQ3DSZFZF%22%2C%22ts%22%3A1628913238025%7D; _cc_id=2539301c81022d5781327f28f88677a0; panoramaId=19b756db47061e5e03da805262c04945a702c73d15a1c4eeea3e3b2a141a73c5; panoramaId_expiry=1629518037798; continent_code_found=NA; __qca=P0-163425031-1628913231594; _pubcid=6c347133-e0d8-4cd2-973e-384dfd065bd1; _fssid=ac82adaf-7b46-452f-8c6c-83c369bbb7cb; _gcl_au=1.1.194063521.1628913230; fsbotchecked=true'
            }
                
            URL = f'https://www.rotowire.com/basketball/tables/projections.php?type=daily&pos=ALL&date={date}'
            players = requests.get(URL, headers=headers).json()
            for player in players:
                player_info = (
                    date, player['player'], player['team'], player['pos'], player['G'],
                    player['DBLDBL'] , player['TRPDBL'], player['THREEPA'],
                    player['THREEPM'] , player['THREEPPCT'], player['AST'],
                    player['BLK'] , player['DREB'], player['FGPCT'],
                    player['FGA'] , player['FGM'], player['FTPCT'],
                    player['FTA'] , player['FTM'], player['MIN'],
                    player['OREB'] , player['PF'], player['PTS'],
                    player['REB'] , player['STL'], player['TO'],
                )
                temp.append(player_info)

            for t in temp:
                self.sql.insert_rotowire_projections(t)

    def update_linestarapp_data(self):
        query = """SELECT * FROM LINESTARAPP_DATA"""
        sql_data = self.sql.select_data(query)

        if sql_data.empty:
            period_id = LINESTARAPP_MIN_PID
        else:
            period_id = int(sql_data['PID'].max()) + 1

        while True:
            print(period_id)
            pid_in_invalid_range = period_id >= LINESTARAPP_INVALID_PID_RANGE[0] \
                and period_id <= LINESTARAPP_INVALID_PID_RANGE[1]
            pid_in_invalid_values = period_id in LINESTARAPP_INVALID_PID_VALUES
            if pid_in_invalid_range or pid_in_invalid_values:
                period_id += 1
                continue

            temp = []

            site_to_data = {}
            for site_id in LINESTARAPP_SITEID_TO_SITE:
                URL = (
                    'https://www.linestarapp.com/DesktopModules/DailyFantasyApi/API/Fantasy/GetSalariesV5?'
                    f'sport=2&site={site_id}&periodId={period_id}'
                )
                site_to_data[site_id] = requests.get(URL).json()
                if site_to_data[site_id]['SalaryContainerJson'] is None:
                    return

            for site_id in LINESTARAPP_SITEID_TO_SITE:
                data = site_to_data[site_id]
                games = json.loads(data['SalaryContainerJson'])['Games']
                salaries = json.loads(data['SalaryContainerJson'])['Salaries']

                player_id_to_data = {}
                if period_id >= LINESTARAPP_MIN_DEF_PID:
                    for i in range(11):
                        player_matchups = data['MatchupData'][i]['PlayerMatchups']
                        for player in player_matchups:
                            player_id = player['PlayerId']
                            if player_id not in player_id_to_data:
                                player_id_to_data[player_id] = {}
                            if i in [0, 1]:
                                player_id_to_data[player_id]['START'] = 1
                            elif i in [2, 3]:
                                player_id_to_data[player_id]['START'] = 0
                            elif i in [4, 5, 6, 7, 8]:
                                player_id_to_data[player_id]['START'] = 1
                                def_rank = int(player['Values'][6])
                                player_id_to_data[player_id]['OPPRANK_DvP_L20'] = def_rank
                            elif i == 9:
                                player_id_to_data[player_id]['START'] = 0
                                def_rank = int(player['Values'][6])
                                player_id_to_data[player_id]['OPPRANK_DvP_L20'] = def_rank
                            else:
                                def_rank = int(player['Values'][7])
                                player_id_to_data[player_id]['OPPRANK_D_L20'] = def_rank

                site = LINESTARAPP_SITEID_TO_SITE[site_id]

                team_to_odds = {}
                for game in games:
                    if game['VegasOverUnder'] != 0:
                        team_to_odds[game['AwayTeam']] = {}
                        team_to_odds[game['AwayTeam']]['Spread'] = game['VegasLineAway']
                        team_to_odds[game['AwayTeam']]['OverUnder'] = game['VegasOverUnder']
                        team_to_odds[game['HomeTeam']] = {}
                        team_to_odds[game['HomeTeam']]['Spread'] = game['VegasLineHome']
                        team_to_odds[game['HomeTeam']]['OverUnder'] = game['VegasOverUnder']

                for salary in salaries:
                    s = salary['GT']
                    date = pd.to_datetime(s[s.find("(")+1:s.find("-")], unit='ms')
                    date = date.tz_localize('UTC').tz_convert('EST').strftime("%Y-%m-%d")
                    player_id = salary['PID']
                    if player_id not in player_id_to_data:
                        start, def_vs_pos, def_overall = None, None, None
                    else:
                        player_data = player_id_to_data[player_id]
                        start = player_data['START'] if 'START' in player_data else None
                        def_vs_pos = player_data['OPPRANK_DvP_L20'] if 'OPPRANK_DvP_L20' in player_data else None
                        def_overall = player_data['OPPRANK_D_L20'] if 'OPPRANK_D_L20' in player_data else None
                    team = salary['PTEAM']
                    spread = team_to_odds[team]['Spread'] if team in team_to_odds else None
                    total = team_to_odds[team]['OverUnder'] if team in team_to_odds else None
                    player = (
                        int(period_id), date, site, player_id, salary['Name'], start, salary['POS'],
                        team, def_vs_pos, def_overall, salary['SAL'], salary['PP'], salary['PS'],
                        spread, total
                    )
                    temp.append(player)

            for t in temp:
                self.sql.insert_linestarapp_data(t)
            period_id += 1

class QueryData(object):
    def __init__(self, update=False):
        self.sql = SQL()
        self.sql.create_connection()
        self.sql.create_tables()
        self.update = update
        self.update_data = UpdateData(sql=self.sql)

    def query_game_data(self):
        if self.update:
            self.update_data.update_game_data()
        query = """SELECT * FROM GAMES"""
        sql_data = self.sql.select_data(query)

        cutoff = datetime.now()
        if cutoff.hour < 8:
            cutoff = cutoff - timedelta(days=1)
        sql_data = sql_data.loc[sql_data['DATE'] < cutoff.strftime("%Y-%m-%d")]

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
        sql_data = sql_data.merge(game_data, left_on='GAMEID', right_on='ID', how='left')
        sql_data = sql_data.merge(player_data, left_on='PLAYERID', right_on='ID', how='left')
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
            boxscore_data = boxscore_data.loc[boxscore_data['SECONDSPLAYED'] != 0]
            subset = boxscore_data[['SEASON', 'GAMEID', 'DATE', 'PLAYERID']]
            tuples = set([tuple(x) for x in subset.to_numpy()])
            self.update_data.update_quarterly_boxscore_data(tuples, boxscore_data)
        query = """SELECT * FROM QUARTERLYBOXSCORES"""
        sql_data = self.sql.select_data(query)
        return sql_data

    def query_salary_data(self):
        if self.update:
            game_data = self.query_game_data()
            game_data = game_data.loc[game_data['SEASONTYPE'] == 'Regular Season']
            game_dates = set(game_data['DATE'].unique())
            self.update_data.update_salary_data(game_dates)
        query = """SELECT * FROM SALARIES"""
        sql_data = self.sql.select_data(query)
        return sql_data

    def query_contest_data(self):
        if self.update:
            game_data = self.query_game_data()
            game_data = game_data.loc[game_data['SEASONTYPE'] == 'Regular Season']
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

    def query_daily_fantasy_fuel_data(self):
        if self.update:
            game_data = self.query_game_data()
            game_data = game_data.loc[game_data['SEASONTYPE'] == 'Regular Season']
            game_dates = set(game_data['DATE'].unique())
            self.update_data.update_daily_fantasy_fuel_data(game_dates)
        query = """SELECT * FROM DAILY_FANTASY_FUEL_PROJECTIONS"""
        sql_data = self.sql.select_data(query)
        return sql_data

    def query_rotowire_data(self):
        if self.update:
            game_data = self.query_game_data()
            game_data = game_data.loc[game_data['SEASONTYPE'] == 'Regular Season']
            game_dates = set(game_data['DATE'].unique())
            self.update_data.update_rotowire_data(game_dates)
        query = """SELECT * FROM ROTOWIRE_PROJECTIONS"""
        sql_data = self.sql.select_data(query)
        return sql_data

    def query_linestarapp_data(self):
        if self.update:
            self.update_data.update_linestarapp_data()
        query = """SELECT * FROM LINESTARAPP_DATA"""
        sql_data = self.sql.select_data(query)
        return sql_data
