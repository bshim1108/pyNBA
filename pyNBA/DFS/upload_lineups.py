import sys
import csv
import json
import pulp
import requests
import argparse
import numpy as np
import pandas as pd
from pyNBA.DFS.constants import Site
from pyNBA.DFS.rules import FPCalculator
from pyNBA.Data.constants import ROTOWIRE_NAME_TO_DK_NAME
from pydfs_lineup_optimizer import get_optimizer, Sport, Player
from pydfs_lineup_optimizer.solvers.pulp_solver import PuLPSolver


class CustomPuLPSolver(PuLPSolver):
    LP_SOLVER = pulp.GLPK_CMD(msg=0)


class UploadLineups(object):
    def __init__(self, file_name, use_rotowire, use_linestarapp):
        self.file_name = f"/Users/brandonshimiaie/Projects/pyNBA/pyNBA/DFS/DKEntries/{file_name}"
        self.use_rotowire = use_rotowire
        self.use_linestarapp = use_linestarapp

    def get_placeholders(self):
        placeholders = pd.read_csv(
            self.file_name,
            error_bad_lines=False,
            warn_bad_lines=False,
            header=0
            )
        placeholders = placeholders.iloc[:, :12].dropna(subset=['Entry ID'])
        return placeholders

    def get_slate_players(self):
        slate_players = pd.read_csv(
            self.file_name,
            error_bad_lines=False,
            header=7
            )
        slate_players = slate_players[['ID', 'Name', 'TeamAbbrev', 'Position', 'Salary']]
        return slate_players

    def get_linestarapp_projections(self):
        if self.use_linestarapp == "false":
            return pd.DataFrame(columns=['Name', 'TeamAbbrev', 'LSA_PROJ'])

        URL = 'https://www.linestarapp.com/DesktopModules/DailyFantasyApi/API/Fantasy/GetSalariesV5?sport=2&site=1'
        df = requests.get(URL).json()
        salaries = json.loads(df['SalaryContainerJson'])['Salaries']
        if len(salaries) == 0:
            return pd.DataFrame(columns=['Name', 'TeamAbbrev', 'LSA_PROJ'])

        temp = []
        for salary in salaries:
            player = (salary['Name'], salary['PTEAM'], salary['PP'])
            temp.append(player)
            
        linestarapp = pd.DataFrame(temp, columns=['Name', 'TeamAbbrev', 'LSA_PROJ'])
        return linestarapp

    def get_rotowire_projections(self):
        if self.use_rotowire == "false":
            return pd.DataFrame(columns=['Name', 'TeamAbbrev', 'ROTO_PROJ'])

        headers = {
            'Cookie': '_dlt=1; __gads=ID=5058a19006cea8ef-22ee9863bbba0089:T=1628913231:RT=1628990961:S=ALNI_MYB4_WnqAtZNyJ8aGMxonI_Lk4e5Q; _ga=GA1.2.1290194056.1628913231; _ga_DJZM5GNYZ8=GS1.1.1628990184.4.1.1628990960.0; _gid=GA1.2.640401548.1628913231; _uetsid=3c53b7d0fcb311eb9b3b99c01437cc0a; _uetvid=3c53e940fcb311eb89bff796026097a5; _pbjs_userid_consent_data=3524755945110770; cto_bidid=YSRDFl95anJGTm5NZ0tlS0U0cWdkcUx6dHBVJTJCdHlEWDdudkVGanlHUjkyU2cyQ2xSWFlNMVMwYVdDT1VFdWNHdyUyQjNHMlg0aWxZNzVDMnl5Q3MyaFRUTTBPVnRvJTJGdGZRSm84SHNpSFZ5S243WjBPc2JJNlljY2h2cWs3cjRZSlpGZGxxaA; cto_bundle=o80dIF85ZHhDWFZTSkk1Y0JVbUlMeTRPcG5zeiUyRjlmdHRWeVQ5NXdCSktNNkNtVnBWNzdxVVdudCUyRjlLVWhUSVBodW1tZVFkYyUyQlVSNzhnSkM4Y2FscEV6NVBFSW5oMmxsTnd3R2JZTXNsMTl3cEkzOW53UW1QRzQ5aGkyWTA0V3dmeWhBMFExdUxFN1Y1YkNOaVd6Z1lzbUN5JTJGbmZYUGI0RVJ6V3IxMWFDbzUyb1I1byUzRA; _dlt=1; _dc_gtm_UA-3226863-14=1; PHPSESSID=cf11b6b937dbc6d592ffc245efafac36; _dc_gtm_UA-3226863-1=1; _dc_gtm_UA-3226863-15=1; used_site_rw=nba-main%7C; used_site_rw_exp=1629010800; rwnav_NBA=Fantasy; _fbp=fb.1.1628990839537.931434173; RW_orderTotal=6.99; _lr_env_src_ats=false; _lr_retry_request=true; amplitude_id_c2c7a484a98d5a16340469d0baf32aefrotowire.com=eyJkZXZpY2VJZCI6Ijc1YTllYTgyLTMzOTgtNGE0OS05MmVjLTQ0NmQ4NGJjZTM5MVIiLCJ1c2VySWQiOm51bGwsIm9wdE91dCI6ZmFsc2UsInNlc3Npb25JZCI6MTYyODkxMzIzMDY4OSwibGFzdEV2ZW50VGltZSI6MTYyODkxMzI1NTQ3MywiZXZlbnRJZCI6MCwiaWRlbnRpZnlJZCI6MCwic2VxdWVuY2VOdW1iZXIiOjB9; cookie=%7B%22id%22%3A%2201FD1CPZZ6D92SK3ETQ3DSZFZF%22%2C%22ts%22%3A1628913238025%7D; _cc_id=2539301c81022d5781327f28f88677a0; panoramaId=19b756db47061e5e03da805262c04945a702c73d15a1c4eeea3e3b2a141a73c5; panoramaId_expiry=1629518037798; continent_code_found=NA; __qca=P0-163425031-1628913231594; _pubcid=6c347133-e0d8-4cd2-973e-384dfd065bd1; _fssid=ac82adaf-7b46-452f-8c6c-83c369bbb7cb; _gcl_au=1.1.194063521.1628913230; fsbotchecked=true'
        }

        date = pd.Timestamp('now', tz='EST').strftime("%Y-%m-%d")
        URL = f'https://www.rotowire.com/basketball/tables/projections.php?type=daily&pos=ALL&date={date}'
        players = requests.get(URL, headers=headers).json()
        if len(players) == 0:
            return pd.DataFrame(columns=['Name', 'TeamAbbrev', 'ROTO_PROJ'])

        temp = []
        for player in players:
            player_info = (
                player['player'], player['team'],
                player['DBLDBL'], player['TRPDBL'],
                player['THREEPM'], player['AST'],
                player['BLK'], player['PTS'],
                player['REB'], player['STL'], player['TO'],
            )
            temp.append(player_info)
            
        roto = pd.DataFrame(temp, columns=['Name', 'TeamAbbrev', 'DBLDBL%', 'TRPDBL%', 'THREEPM', 'AST', 'BLK', 'PTS', 'REB', 'STL', 'TOV'])
        roto[['DBLDBL%', 'TRPDBL%', 'THREEPM', 'AST', 'BLK', 'PTS', 'REB', 'STL', 'TOV']] = \
            roto[['DBLDBL%', 'TRPDBL%', 'THREEPM', 'AST', 'BLK', 'PTS', 'REB', 'STL', 'TOV']].astype(float)
        roto['ROTO_PROJ'] = roto.apply(
            lambda row: FPCalculator.calculate_draftkings_fp(
                row['PTS'], row['REB'], row['AST'], row['TOV'], row['BLK'], row['STL'],
                row['THREEPM'], (row['DBLDBL%'], row['TRPDBL%'])
            ),
            axis=1
        )
        roto = roto[['Name', 'TeamAbbrev', 'ROTO_PROJ']]
        roto['Name'] = roto['Name'].apply(
            lambda x: x if x not in ROTOWIRE_NAME_TO_DK_NAME else ROTOWIRE_NAME_TO_DK_NAME[x]
        )
        return roto

    def get_all_data(self):
        slate_players = self.get_slate_players()
        roto = self.get_rotowire_projections()
        linestarapp = self.get_linestarapp_projections()

        slate_players = slate_players.merge(roto, on=['Name', 'TeamAbbrev'], how='left')
        slate_players = slate_players.merge(linestarapp, on=['Name', 'TeamAbbrev'], how='left')

        def _get_projection(roto_projection, linestar_projection):
            if np.isnan(roto_projection) and np.isnan(linestar_projection):
                return 0
            elif np.isnan(roto_projection):
                return linestar_projection
            elif np.isnan(linestar_projection):
                return roto_projection
            elif roto_projection == 0 and linestar_projection != 0:
                return linestar_projection
            elif roto_projection != 0 and linestar_projection == 0:
                return 0
            else:
                return roto_projection

        slate_players['PROJECTION'] = slate_players.apply(
            lambda row: _get_projection(row['ROTO_PROJ'], row['LSA_PROJ']),
            axis=1
        )
        return slate_players
    
    def get_optimal_lineups(self, rCoeff=0.05):
        all_players = self.get_all_data()

        placeholders = self.get_placeholders()
        total_entries = len(placeholders)

        optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASKETBALL, solver=CustomPuLPSolver)

        players = []
        for _, player in all_players.iterrows():
            player_id = player['ID']
            name = player['Name'].split()
            first_name = name[0]
            last_name = name[1] if len(name) > 1 else ''
            positions = player['Position'].split('/')
            team = player['TeamAbbrev']
            projection = player['PROJECTION']
            stdev = rCoeff*projection
            salary =  player['Salary']

            player = Player(player_id, first_name, last_name, positions, team, salary, projection, stdev=stdev, max_exposure=0.80)
            players.append(player)

        optimizer.load_players(players)

        raw_lineups = optimizer.optimize(n=int(total_entries), randomness=True)

        lineups = pd.DataFrame()
        for raw_lineup in raw_lineups:
            player_positions = [i.lineup_position for i in raw_lineup.lineup]
            player_ids = [tuple([i.id for i in raw_lineup.lineup])]
            projected_score = all_players.loc[all_players['ID'].isin(player_ids[0]), 'PROJECTION'].sum()
            lineup = pd.DataFrame(player_ids, columns=player_positions)
            lineup['PROJSCORE'] = projected_score
            lineups = lineups.append(lineup)

        lineups = lineups.sort_values(by='PROJSCORE', ascending=False)
        lineups = lineups.drop(columns=['PROJSCORE'])

        return lineups

    def upload_lineups(self):
        lineups = self.get_optimal_lineups()

        r = csv.reader(open(self.file_name))
        lines = list(r)
        for i in range(len(lineups)):
            lineup = lineups.iloc[i]
            lines[i+1][4] = lineup['PG']
            lines[i+1][5] = lineup['SG']
            lines[i+1][6] = lineup['SF']
            lines[i+1][7] = lineup['PF']
            lines[i+1][8] = lineup['C']
            lines[i+1][9] = lineup['G']
            lines[i+1][10] = lineup['F']
            lines[i+1][11] = lineup['UTIL']
            
        writer = csv.writer(open(self.file_name, 'w'))
        writer.writerows(lines)


def create_parser():
    parser = argparse.ArgumentParser("Upload Lineups to Specified File")
    parser.add_argument(
        "--file-name",
        type=str,
        required=True,
        help="File name that contains slate players and placeholder entries"
    )
    parser.add_argument(
        "--use-roto",
        type=str,
        default="true",
        help="Use rotowire projections"
    )
    parser.add_argument(
        "--use-linestarapp",
        type=str,
        default="true",
        help="Use linestarapp projections"
    )

    return parser

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    UploadLineups(
        file_name=args.file_name,
        use_rotowire=args.use_roto,
        use_linestarapp=args.use_linestarapp
        ).upload_lineups()
  