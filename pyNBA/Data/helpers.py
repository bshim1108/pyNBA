import pandas as pd
from nba_api.stats.endpoints import PlayByPlayV2

class Helpers(object):
    def __init__(self):
        pass

    def increment_timestring(self, timestring):
        temp = timestring.split(':')
        minutes = temp[0]
        seconds = int(temp[1])
        seconds += 1
        return '{}:{}'.format(minutes, str(seconds))

    def get_play_by_play_attempts(self, game_id):
        play_by_play = PlayByPlayV2(game_id=game_id).get_data_frames()[0]

        play_by_play['DESCRIPTION'] = None
        play_by_play.loc[~play_by_play['VISITORDESCRIPTION'].isnull(), 'DESCRIPTION'] = \
            play_by_play.loc[~play_by_play['VISITORDESCRIPTION'].isnull(), 'VISITORDESCRIPTION']
        play_by_play.loc[~play_by_play['HOMEDESCRIPTION'].isnull(), 'DESCRIPTION'] = \
            play_by_play.loc[~play_by_play['HOMEDESCRIPTION'].isnull(), 'HOMEDESCRIPTION']
        play_by_play.loc[~play_by_play['NEUTRALDESCRIPTION'].isnull(), 'DESCRIPTION'] = \
            play_by_play.loc[~play_by_play['NEUTRALDESCRIPTION'].isnull(), 'HOMEDESCRIPTION']
        play_by_play['DESCRIPTION'] = play_by_play['DESCRIPTION'].str.replace('Personal Take Foul','PFOUL')
        play_by_play['DESCRIPTION'] = play_by_play['DESCRIPTION'].str.replace('Offensive Charge Foul','OFOUL')
        play_by_play['DESCRIPTION'] = play_by_play['DESCRIPTION'].str.replace('Flagrant','FLAGRANT')
        play_by_play['DESCRIPTION'] = play_by_play['DESCRIPTION'].str.replace('Foul','FOUL')

        attempt_data = play_by_play.loc[play_by_play['EVENTMSGTYPE'].isin([1, 2]), ['PERIOD', 'PCTIMESTRING', 'DESCRIPTION', 'PLAYER1_ID']]
        attempt_data = attempt_data.rename(columns={'PLAYER1_ID': 'PLAYER_ID'})

        ft_data = pd.DataFrame(columns=['PERIOD', 'PCTIMESTRING', 'DESCRIPTION', 'PLAYER_ID', 'FTA', 'FTM'])
        raw_ft_data = play_by_play.loc[play_by_play['EVENTMSGTYPE'].isin([3, 6])]
        prev_time = None
        for index, row in raw_ft_data.loc[raw_ft_data['EVENTMSGTYPE'] == 6].iterrows():
            time = row['PCTIMESTRING']
            if time == prev_time:
                raw_ft_data.loc[index:, 'PCTIMESTRING'] = raw_ft_data.loc[index:, 'PCTIMESTRING'].apply(
                    lambda x: self.increment_timestring(x)
                    )
            prev_time = time
        for (period, time), rows in raw_ft_data.groupby(['PERIOD', 'PCTIMESTRING']):
            ft_rows = rows.loc[rows['EVENTMSGTYPE'] == 3]
            if ft_rows.empty:
                continue

            foul_play = rows.loc[rows['EVENTMSGTYPE'] == 6]
            if len(foul_play) > 0:
                description = foul_play['DESCRIPTION'].iloc[0]
            else:
                description = None

            if description is not None:
                words = description.split(' ')
                foul_type = None
                for word in words:
                    if 'FOUL' in word:
                        foul_type = word.replace('.', '')
                        break
                foul_type = foul_type or 'UNKNOWNFOUL'
                description = '{} TRIP'.format(foul_type)
            else:
                description = 'UNKNOWNFOUL TRIP'

            for player_id, player_ft_rows in ft_rows.groupby('PLAYER1_ID'):
                if 'Technical' in player_ft_rows['DESCRIPTION'].iloc[0]:
                    player_description = 'TFOUL TRIP'
                else:
                    player_description = description
                fta = len(player_ft_rows)
                ftm = len(player_ft_rows.loc[~player_ft_rows['DESCRIPTION'].str.contains("MISS")])
                temp = pd.Series(
                    [period, time, player_description, player_id, fta, ftm],
                    index=['PERIOD', 'PCTIMESTRING', 'DESCRIPTION', 'PLAYER_ID', 'FTA', 'FTM']
                    )
                ft_data = ft_data.append(temp, ignore_index=True)

        attempt_data = pd.merge(
            attempt_data, ft_data[['PLAYER_ID', 'PERIOD', 'PCTIMESTRING', 'FTA', 'FTM']],
            on=['PLAYER_ID', 'PERIOD', 'PCTIMESTRING'], how='left'
            )

        subset = attempt_data[['PLAYER_ID', 'PERIOD', 'PCTIMESTRING']]
        attemp_indexes = set([tuple(x) for x in subset.to_numpy()])
        ft_trips = ft_data.loc[
            ft_data[['PLAYER_ID', 'PERIOD', 'PCTIMESTRING']].apply(
                lambda x: (x['PLAYER_ID'], x['PERIOD'], x['PCTIMESTRING']) not in attemp_indexes, axis=1
                )
            ]
        attempt_data = attempt_data.append(ft_trips)

        attempt_data[['FTA', 'FTM']] = attempt_data[['FTA', 'FTM']].fillna(0)
        attempt_data['PTS'] = attempt_data['FTM']
        attempt_data.loc[
            ~(attempt_data['DESCRIPTION'].str.contains('FOUL') & attempt_data['DESCRIPTION'].str.contains('TRIP')) &
            ~attempt_data['DESCRIPTION'].str.contains('MISS') &
            ~attempt_data['DESCRIPTION'].str.contains('BLOCK') &
            ~attempt_data['DESCRIPTION'].str.contains('3PT'),
            'PTS'] += 2
        attempt_data.loc[
            ~(attempt_data['DESCRIPTION'].str.contains('FOUL') & attempt_data['DESCRIPTION'].str.contains('TRIP')) &
            ~attempt_data['DESCRIPTION'].str.contains('MISS') &
            ~attempt_data['DESCRIPTION'].str.contains('BLOCK') &
            attempt_data['DESCRIPTION'].str.contains('3PT'),
            'PTS'] += 3

        attempt_data = attempt_data.drop_duplicates()
        return attempt_data

    def get_attempts_boxscores(self, game_id):
        play_by_play_attempts = self.get_play_by_play_attempts(game_id)

        attempts_boxscores = pd.DataFrame(columns=[
            'PLAYER_ID', 'TOTAL_ATTEMPTS', 'TOTAL_PTS', 'TOTAL_FTA', 'TOTAL_FTM',
            'SHOT_ATTEMPTS', 'SHOT_PTS', 'SHOT_FTA', 'SHOT_FTM',
            'SFOUL_ATTEMPTS', 'SFOUL_PTS', 'SFOUL_FTA', 'SFOUL_FTM',
            'PFOUL_ATTEMPTS', 'PFOUL_PTS', 'PFOUL_FTA', 'PFOUL_FTM',
            'TFOUL_PTS'
            ])
        for player_id, player_plays in play_by_play_attempts.groupby(['PLAYER_ID']):
            shot_plays = player_plays.loc[~player_plays['DESCRIPTION'].str.contains('TRIP')]
            shot_attempts = len(shot_plays)
            shot_pts = shot_plays['PTS'].sum()
            shot_fta = shot_plays['FTA'].sum()
            shot_ftm = shot_plays['FTM'].sum()

            sfoul_plays = player_plays.loc[player_plays['DESCRIPTION'] == 'SFOUL TRIP']
            sfoul_attempts = len(sfoul_plays)
            sfoul_pts = sfoul_plays['PTS'].sum()
            sfoul_fta = sfoul_plays['FTA'].sum()
            sfoul_ftm = sfoul_plays['FTM'].sum()

            pfoul_plays = player_plays.loc[
                (player_plays['DESCRIPTION'].str.contains('TRIP')) &
                (player_plays['DESCRIPTION'] != 'SFOUL TRIP') & 
                (~player_plays['DESCRIPTION'].str.contains('TFOUL')) &
                (~player_plays['DESCRIPTION'].str.contains('FLAGRANTFOUL'))
                ]
            pfoul_attempts = len(pfoul_plays)
            pfoul_pts = pfoul_plays['PTS'].sum()
            pfoul_fta = pfoul_plays['FTA'].sum()
            pfoul_ftm = pfoul_plays['FTM'].sum()

            tfoul_plays = player_plays.loc[
                (player_plays['DESCRIPTION'].str.contains('TFOUL')) |
                (player_plays['DESCRIPTION'].str.contains('FLAGRANTFOUL'))
                ]
            tfoul_pts = tfoul_plays['PTS'].sum()

            total_attempts = len(player_plays) - len(tfoul_plays)
            total_pts = player_plays['PTS'].sum()
            total_fta = player_plays['FTA'].sum()
            total_ftm = player_plays['FTM'].sum()

            temp = pd.Series(
                [player_id, total_attempts, total_pts, total_fta, total_ftm,
                shot_attempts, shot_pts, shot_fta, shot_ftm,
                sfoul_attempts, sfoul_pts, sfoul_fta, sfoul_ftm,
                pfoul_attempts, pfoul_pts, pfoul_fta, pfoul_ftm,
                tfoul_pts],
                index=['PLAYER_ID', 'TOTAL_ATTEMPTS', 'TOTAL_PTS', 'TOTAL_FTA', 'TOTAL_FTM',
                    'SHOT_ATTEMPTS', 'SHOT_PTS', 'SHOT_FTA', 'SHOT_FTM',
                    'SFOUL_ATTEMPTS', 'SFOUL_PTS', 'SFOUL_FTA', 'SFOUL_FTM',
                    'PFOUL_ATTEMPTS', 'PFOUL_PTS', 'PFOUL_FTA', 'PFOUL_FTM',
                    'TFOUL_PTS']
                )
            attempts_boxscores = attempts_boxscores.append(temp, ignore_index=True)

        attempts_boxscores['GAME_ID'] = game_id
        return attempts_boxscores