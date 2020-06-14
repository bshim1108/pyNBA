import sqlite3
from sqlite3 import Error
import pandas as pd

class SQL(object):
    def __init__(self, db_file=r"/Users/brandonshimiaie/Projects/pyNBA/sqlite/db/nba.db"):
        self.db_file = db_file
        self.conn = None

    def __del__(self):
        if self.conn is not None:
            self.conn.close()

    def create_connection(self):
        try:
            print(self.db_file)
            self.conn = sqlite3.connect(self.db_file)
            print(sqlite3.version)
        except Error as e:
            print(e)

    def excecute(self, sql_command, values=None):
        if self.conn is None:
            print('Connection not established')
            return
        try:
            c = self.conn.cursor()
            if values is None:
                c.execute(sql_command)
            else:
                c.execute(sql_command, values)
            self.conn.commit()
            return c.fetchall()
        except Error as e:
            print(e)

    def create_tables(self):
        sql_create_games_table = """CREATE TABLE IF NOT EXISTS GAMES (
                                    ID text PRIMARY KEY,
                                    SEASON text NOT NULL,
                                    DATE text NOT NULL,
                                    HTM text NOT NULL,
                                    VTM text NOT NULL,
                                    W text NOT NULL
                                );"""
        self.excecute(sql_create_games_table)

        sql_create_players_table = """CREATE TABLE IF NOT EXISTS PLAYERS (
                                    ID text PRIMARY KEY,
                                    NAME text NOT NULL,
                                    POSITION text NOT NULL,
                                    SCHOOL text NOT NULL,
                                    COUNTRY text NOT NULL,
                                    HEIGHT integer NOT NULL,
                                    WEIGHT integer NOT NULL,
                                    DRAFTYEAR integer NOT NULL,
                                    DRAFTROUND integer NOT NULL,
                                    DRAFTNUMBER integer NOT NULL,
                                    BIRTHDATE text NOT NULL
                                );"""
        self.excecute(sql_create_players_table)

        sql_create_boxscores_table = """CREATE TABLE IF NOT EXISTS BOXSCORES (
                                        GAMEID text NOT NULL,
                                        PLAYERID text NOT NULL,
                                        TEAM text NOT NULL,
                                        OPP_TEAM text NOT NULL,
                                        COMMENT text NOT NULL,
                                        START integer NOT NULL,
                                        SECONDSPLAYED integer NOT NULL,
                                        PTS integer NOT NULL,
                                        FGM integer NOT NULL,
                                        FGA integer NOT NULL,
                                        FG3M integer NOT NULL,
                                        FG3A integer NOT NULL,
                                        FTM integer NOT NULL,
                                        FTA integer NOT NULL,
                                        PTS_OFF_TOV integer NOT NULL,
                                        PTS_2ND_CHANCE integer NOT NULL,
                                        PTS_FB integer NOT NULL,
                                        PTS_PAINT integer NOT NULL,
                                        PCT_AST_2PM real NOT NULL,
                                        PCT_AST_3PM real NOT NULL,
                                        OREB integer NOT NULL,
                                        OREB_PCT real NOT NULL,
                                        DREB real NOT NULL,
                                        DREB_PCT real NOT NULL,
                                        AST integer NOT NULL,
                                        AST_PCT real NOT NULL,
                                        AST_RATIO real NOT NULL,
                                        STL integer NOT NULL,
                                        BLK integer NOT NULL,
                                        TOV integer NOT NULL,
                                        PF integer NOT NULL,
                                        PLUSMINUS integer NOT NULL,
                                        USG_PCT real NOT NULL,
                                        PACE integer NOT NULL,
                                        PRIMARY KEY (GAMEID, PLAYERID),
                                        FOREIGN KEY (GAMEID) REFERENCES GAMES (ID),
                                        FOREIGN KEY (PLAYERID) REFERENCES PLAYERS (ID)
                                    );"""
        self.excecute(sql_create_boxscores_table)

        sql_create_shotchartdetails_table = """CREATE TABLE IF NOT EXISTS SHOTCHARTDETAILS (
                                                GAMEID text NOT NULL,
                                                GAMEEVENTID text NOT NULL,
                                                PLAYERID text NOT NULL,
                                                PERIOD integer NOT NULL,
                                                SECONDSREMAINING integer NOT NULL,
                                                EVENTTYPE text NOT NULL,
                                                ACTIONTYPE text NOT NULL,
                                                SHOTTYPE text NOT NULL,
                                                SHOTZONEBASIC text NOT NULL,
                                                SHOTZONEAREA text NOT NULL,
                                                SHOTZONERANGE text NOT NULL,
                                                SHOTDISTANCE text NOT NULL,
                                                PRIMARY KEY (GAMEID, GAMEEVENTID, PLAYERID),
                                                FOREIGN KEY (GAMEID) REFERENCES GAMES (ID),
                                                FOREIGN KEY (PLAYERID) REFERENCES PLAYERS (ID)
                                            );"""
        self.excecute(sql_create_shotchartdetails_table)

        sql_create_odds_table = """CREATE TABLE IF NOT EXISTS ODDS (
                                                DATE text NOT NULL,
                                                TEAM text NOT NULL,
                                                PERIOD text NOT NULL,
                                                POINTSPREAD real NOT NULL,
                                                MONEYLINE real NOT NULL,
                                                TOTAL real NOT NULL,
                                                PRIMARY KEY (DATE, TEAM, PERIOD)
                                            );"""
        self.excecute(sql_create_odds_table)

        sql_create_quarterly_boxscores_table = """CREATE TABLE IF NOT EXISTS QUARTERLYBOXSCORES (
                                        SEASON text NOT NULL,
                                        GAMEID text NOT NULL,
                                        DATE text NOT NULL,
                                        PLAYERID text NOT NULL,
                                        QUARTER integer NOT NULL,
                                        SECONDSPLAYED integer NOT NULL,
                                        PTS integer NOT NULL,
                                        FGM integer NOT NULL,
                                        FGA integer NOT NULL,
                                        FG3M integer NOT NULL,
                                        FG3A integer NOT NULL,
                                        FTM integer NOT NULL,
                                        FTA integer NOT NULL,
                                        OREB integer NOT NULL,
                                        DREB integer NOT NULL,
                                        AST integer NOT NULL,
                                        STL integer NOT NULL,
                                        BLK integer NOT NULL,
                                        TOV integer NOT NULL,
                                        PF integer NOT NULL,
                                        PLUSMINUS integer NOT NULL,
                                        PRIMARY KEY (GAMEID, PLAYERID, QUARTER),
                                        FOREIGN KEY (GAMEID) REFERENCES GAMES (ID),
                                        FOREIGN KEY (PLAYERID) REFERENCES PLAYERS (ID)
                                    );"""
        self.excecute(sql_create_quarterly_boxscores_table)

        sql_create_salaries_table = """CREATE TABLE IF NOT EXISTS SALARIES (
                                            SITE text NOT NULL,
                                            DATE text NOT NULL,
                                            PLAYER text NOT NULL,
                                            SALARY integer NOT NULL,
                                            PRIMARY KEY (SITE, DATE, PLAYER)
                                        );"""
        self.excecute(sql_create_salaries_table)
        
        sql_create_contests_table = """CREATE TABLE IF NOT EXISTS CONTESTS (
                                            SITE text NOT NULL,
                                            DATE text NOT NULL,
                                            SLATEID text NOT NULL,
                                            SLATETYPE text NOT NULL,
                                            GAMECOUNT integer NOT NULL,
                                            TEAMS text NOT NULL,
                                            CONTESTID text NOT NULL,
                                            CONTESTNAME text NOT NULL,
                                            PRIZEPOOL float NOT NULL,
                                            ENTRYFEE float NOT NULL,
                                            TOPPRIZE float NOT NULL,
                                            MAXENTRIES integer,
                                            TOTALENTRIES integer NOT NULL,
                                            CASHLINE float,
                                            TOPSCORE float,
                                            PRIMARY KEY (SITE, DATE, CONTESTID)
                                        );"""
        self.excecute(sql_create_contests_table)

        # a = """DROP TABLE CONTESTINFO"""
        # self.excecute(a)
        sql_create_contest_info_table = """CREATE TABLE IF NOT EXISTS CONTESTINFO (
                                            CONTESTID text NOT NULL,
                                            PRIZE float NOT NULL,
                                            MINPOINTS float,
                                            MAXPOINTS float,
                                            MINRANK integer,
                                            MAXRANK integer,
                                            PRIMARY KEY (CONTESTID, PRIZE)
                                        );"""
        self.excecute(sql_create_contest_info_table)

    def insert_game(self, game):
        sql_game = """INSERT INTO GAMES(ID, SEASON, DATE, HTM, VTM, W)
                        VALUES(?, ?, ?, ?, ?, ?)
                    """
        self.excecute(sql_game, game)

    def insert_player(self, player):
        sql_player = """INSERT INTO PLAYERS(ID, NAME, POSITION, SCHOOL, COUNTRY, HEIGHT,
                            WEIGHT, DRAFTYEAR, DRAFTROUND, DRAFTNUMBER, BIRTHDATE)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
        self.excecute(sql_player, player)

    def insert_boxscore(self, boxscore):
        sql_boxscore= """INSERT INTO BOXSCORES(GAMEID, PLAYERID, TEAM, OPP_TEAM, COMMENT, START, SECONDSPLAYED,
                            PTS, FGM, FGA, FG3M, FG3A, FTM, FTA, PTS_OFF_TOV, PTS_2ND_CHANCE, PTS_FB,
                            PTS_PAINT, PCT_AST_2PM, PCT_AST_3PM, OREB,
                            OREB_PCT, DREB, DREB_PCT, AST, AST_PCT, AST_RATIO, STL, BLK, TOV,
                            PF, PLUSMINUS, USG_PCT, PACE)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
        self.excecute(sql_boxscore, boxscore)

    def insert_shotchartdetail(self, shotchartdetail):
        sql_shotchartdetail= """INSERT INTO SHOTCHARTDETAILS(GAMEID, GAMEEVENTID, PLAYERID, PERIOD, SECONDSREMAINING,
                            EVENTTYPE, ACTIONTYPE, SHOTTYPE, SHOTZONEBASIC, SHOTZONEAREA, SHOTZONERANGE,
                            SHOTDISTANCE)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
        self.excecute(sql_shotchartdetail, shotchartdetail)

    def insert_odds(self, odds):
        sql_odds= """INSERT INTO ODDS(DATE, TEAM, PERIOD, POINTSPREAD, MONEYLINE, TOTAL)
                        VALUES(?, ?, ?, ?, ?, ?)
                    """
        self.excecute(sql_odds, odds)

    def insert_quarterly_boxscore(self, quarterly_boxscore):
        sql_quarterly_boxscore= """INSERT INTO QUARTERLYBOXSCORES(SEASON, GAMEID, DATE, PLAYERID, QUARTER,
                            SECONDSPLAYED, PTS, FGM, FGA, FG3M, FG3A, FTM, FTA, OREB, DREB, AST, STL, BLK, TOV,
                            PF, PLUSMINUS)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
        self.excecute(sql_quarterly_boxscore, quarterly_boxscore)

    def insert_salary(self, salary):
        sql_salary= """INSERT INTO SALARIES(SITE, DATE, PLAYER, SALARY)
                        VALUES(?, ?, ?, ?)
                    """
        self.excecute(sql_salary, salary)

    def insert_contest(self, contest):
        sql_contest= """INSERT INTO CONTESTS(SITE, DATE, SLATEID, SLATETYPE, GAMECOUNT, TEAMS,
                            CONTESTID, CONTESTNAME, PRIZEPOOL, ENTRYFEE, TOPPRIZE, MAXENTRIES,
                            TOTALENTRIES, CASHLINE, TOPSCORE)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
        self.excecute(sql_contest, contest)

    def insert_contest_info(self, contest_info):
        sql_contest_info= """INSERT INTO CONTESTINFO(CONTESTID, PRIZE, MINPOINTS, MAXPOINTS, MINRANK, MAXRANK)
                        VALUES(?, ?, ?, ?, ?, ?)
                    """
        self.excecute(sql_contest_info, contest_info)

    def select_data(self, query):
        return pd.read_sql_query(query, self.conn)