import pandas as pd
import pulp
from pydfs_lineup_optimizer import get_optimizer, Sport, Player
from pydfs_lineup_optimizer.solvers.pulp_solver import PuLPSolver
from pyNBA.DFS.constants import Site

class CustomPuLPSolver(PuLPSolver):
    LP_SOLVER = pulp.GLPK_CMD(msg=0)

class GetLineups(object):
    def __init__(self):
        self.optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASKETBALL, solver=CustomPuLPSolver)

    def get_best_lineups_v1(self, slate_players, total_entries):
        players = []
        for _, player in slate_players.iterrows():
            player_id = player['PLAYER_ID']
            name = player['PLAYER_NAME'].split()
            first_name = name[0]
            last_name = name[1] if len(name) > 1 else ''
            positions = player['POS'].split('/')
            team = player['TEAM']
            projection = player['PROJECTION']
            salary =  player['SALARY']

            player = Player(player_id, first_name, last_name, positions, team, salary, projection)
            players.append(player)

        self.optimizer.load_players(players)

        lineups = self.optimizer.optimize(n=int(total_entries))

        lineup_scores = pd.DataFrame()
        for lineup in lineups:
            player_ids = [i.id for i in lineup.lineup]
            real_score = slate_players.loc[slate_players['PLAYER_ID'].isin(player_ids), 'FINAL'].sum()
            projected_score = slate_players.loc[slate_players['PLAYER_ID'].isin(player_ids), 'PROJECTION'].sum()
            lineup_score = pd.DataFrame({
                'PLAYERIDS': [player_ids], 'REALSCORE': [real_score], 'PROJSCORE': [projected_score]
                })
            lineup_scores = lineup_scores.append(lineup_score)
        
        lineup_scores = lineup_scores.sort_values(by='PROJSCORE', ascending=False)
        lineup_scores.index = range(len(lineup_scores))

        return lineup_scores

    def get_best_lineups_v2(self, slate_players, total_entries):
        players = []
        for _, player in slate_players.iterrows():
            player_id = player['PLAYER_ID']
            name = player['PLAYER_NAME'].split()
            first_name = name[0]
            last_name = name[1] if len(name) > 1 else ''
            positions = player['POS'].split('/')
            team = player['TEAM']
            projection = player['PROJECTION']
            # ownership = player['OWNERSHIP_HAT']
            # projection = projection - 0.10*projection*ownership
            stdev = 0.05*projection
            salary =  player['SALARY']

            player = Player(player_id, first_name, last_name, positions, team, salary, projection, stdev=stdev, max_exposure=0.80)
            players.append(player)

        self.optimizer.load_players(players)

        lineups = self.optimizer.optimize(n=int(total_entries), randomness=True)

        lineup_scores = pd.DataFrame()
        for lineup in lineups:
            player_ids = [i.id for i in lineup.lineup]
            real_score = slate_players.loc[slate_players['PLAYER_ID'].isin(player_ids), 'FINAL'].sum()
            projected_score = slate_players.loc[slate_players['PLAYER_ID'].isin(player_ids), 'PROJECTION'].sum()
            lineup_score = pd.DataFrame({
                'PLAYERIDS': [player_ids], 'REALSCORE': [real_score], 'PROJSCORE': [projected_score]
                })
            lineup_scores = lineup_scores.append(lineup_score)
        
        lineup_scores = lineup_scores.sort_values(by='PROJSCORE', ascending=False)
        lineup_scores.index = range(len(lineup_scores))

        return lineup_scores