CURRENT_SEASON = '2020-21'

SEASONS = ['2014-15', '2015-16', '2016-17', '2017-18', '2018-19', '2019-20', '2020-21']
INCOMPLETE_SEASONS = ['2020-21']

SEASON_TYPES = ['Pre Season', 'Regular Season']

TRADITIONAL_BOXSCORE_COLUMNS = ['GAME_ID', 'PLAYER_ID', 'TEAM_ABBREVIATION', 'START_POSITION', 'MIN',
                                'PTS', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'OREB', 'DREB',
                                'AST', 'STL', 'BLK', 'TO', 'PF', 'PLUS_MINUS', 'COMMENT']
ADVANCED_BOXSCORE_COLUMNS = ['GAME_ID', 'PLAYER_ID', 'OREB_PCT', 'DREB_PCT', 'AST_PCT', 'AST_RATIO',
                             'USG_PCT', 'PACE', 'POSS']
MISC_BOXSCORE_COLUMNS = ['GAME_ID', 'PLAYER_ID', 'PTS_OFF_TOV',
                         'PTS_2ND_CHANCE', 'PTS_FB', 'PTS_PAINT']
SCORING_BOXSCORE_COLUMNS = ['GAME_ID', 'PLAYER_ID', 'PCT_AST_2PM',
                            'PCT_AST_3PM']

TEAM_NAME_TO_ABBREVIATION = {
    'Atlanta': 'ATL',
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

BAD_CONTEST_DATES = set(['2017-10-17', '2017-11-21', '2020-01-09'])

BAD_CONTEST_IDS = set([
    '5ae6052efd67640e26f63f1b', '5ae5f6e83825540e24a13d26', '5ae4d118dd71203dfc4b8365', '5bfd6301b0f6775f492abe8b',
    '5bfd62fcb0f6775f492abe8a', '5ae51600b819ea7334644b7d', '5bfd62b7b0f6775f492aa33e'
    ])

POSSIBLE_POSITIONS = ['PG', 'SG', 'SF', 'PF', 'C']

ROTO_NAME_TO_NBA_NAME = {
    'Nene Hilario': 'Nene',
    'Jose Barea': 'J.J. Barea',
    'K.J. McDaniels': 'KJ McDaniels',
    'C.J. Miles': 'CJ Miles',
    'Louis Williams': 'Lou Williams',
    'Maurice Williams': 'Mo Williams',
    'Amare Stoudemire': "Amar'e Stoudemire",
    'C.J. McCollum': 'CJ McCollum',
    'J.R. Smith': 'JR Smith',
    'Wes Matthews': 'Wesley Matthews',
    'James Ennis': 'James Ennis III',
    'Marcus Morris': 'Marcus Morris Sr.',
    'Otto Porter': 'Otto Porter Jr.',
    'Glen Rice Jr.': 'Glen Rice',
    'J.J. Redick': 'JJ Redick',
    'P.J. Hairston': 'PJ Hairston',
    'A.J. Price': 'AJ Price',
    'Ishmael Smith': 'Ish Smith',
    'J.J. Hickson': 'JJ Hickson',
    'Louis Amundson': 'Lou Amundson',
    'Luigi Datome': 'Gigi Datome',
    "Johnny O'Bryant": "Johnny O'Bryant III",
    'Sviatoslav Mykhailiuk': 'Svi Mykhailiuk',
    'Kevin Knox': 'Kevin Knox II',
    'Timothe Luwawu': 'Timothe Luwawu-Cabarrot',
    'Mohamed Bamba': 'Mo Bamba',
    'Danuel House': 'Danuel House Jr.',
    'Juan Hernangomez': 'Juancho Hernangomez',
    'Larry Nance': 'Larry Nance Jr.',
    'Derrick Jones': 'Derrick Jones Jr.',
    'Frank Mason III': 'Frank Mason',
    'Harry Giles': 'Harry Giles III',
    'Robert Williams': 'Robert Williams III',
    'Michael Porter': 'Michael Porter Jr.',
    'Kevin Porter': 'Kevin Porter Jr.',
    'Guillermo Hernangomez': 'Willy Hernangomez',
    'Lonnie Walker': 'Lonnie Walker IV',
    'Gary Payton': 'Gary Payton II',
    'Kelly Oubre': 'Kelly Oubre Jr.',
    'Jaren Jackson': 'Jaren Jackson Jr.',
    'Jacob Evans III': 'Jacob Evans',
    'Charlie Brown': 'Charles Brown Jr.',
    'B.J. Johnson': 'BJ Johnson',
    'Marvin Bagley': 'Marvin Bagley III',
    'DeAndre Bembry': "DeAndre' Bembry",
    'Melvin Frazier': 'Melvin Frazier Jr.',
    'Nazareth Mitrou-Long': 'Naz Mitrou-Long',
    'Walter Lemon Jr.': 'Walt Lemon Jr.',
    'Mitch Creek': 'Mitchell Creek',
    'R.J. Hunter': 'RJ Hunter',
    'Wade Baldwin': 'Wade Baldwin IV',
    'D.J. Stephens': 'DJ Stephens',
    'James Webb': 'James Webb III',
    'Joseph Young': 'Joe Young',
    'Andrew White': 'Andrew White III',
    'Matt Williams': 'Matt Williams Jr.',
    'Vince Hunter': 'Vincent Hunter',
    "Maurice N'dour": "Maurice Ndour",
    'A.J. Hammons': 'AJ Hammons',
    'Sheldon McClellan': 'Sheldon Mac'
}

DB_TEAM_TO_NBA_TEAM = {
    'PHO': 'PHX',
    'GS': 'GSW',
    'SA': 'SAS',
    'NY': 'NYK',
    'NO': 'NOP'
}

BAD_OWNERSHIP_KEYS = ['name', 'slatePosition', 'salary', '_id', 'actualFpts',
                      'projectedFpts', 'projectedOwnership', 'combinedOwnership']

BAD_CONTEST_SUBSTRINGS = ['satellite', ' sat ', 'megasat', 'supersat', 'supersatellite', 'qualifier', 'megaqual']

OWNERSHIP_NAME_TO_NBA_NAME = {
    'A.J. Hammons': 'AJ Hammons',
    'B.J. Johnson': 'BJ Johnson',
    'Billy Garrett Jr.': 'Billy Garrett',
    'Bruce Brown Jr.':  'Bruce Brown',
    'C.J. McCollum': 'CJ McCollum',
    'C.J. Miles': 'CJ Miles',
    'CJ Wilcox': 'C.J. Wilcox',
    'Charlie Brown': 'Charles Brown Jr.',
    'D.J. Stephens': 'DJ Stephens',
    'Danuel House': 'Danuel House Jr.',
    'DeAndre Bembry': "DeAndre' Bembry",
    'Dennis Smith': 'Dennis Smith Jr.',
    'Derrick Jones': 'Derrick Jones Jr.',
    'Derrick Walton': 'Derrick Walton Jr.',
    'Deyonta Davis ': 'Deyonta Davis',
    'Frank Mason III': 'Frank Mason',
    'Gary Payton': 'Gary Payton II',
    'Gary Trent': 'Gary Trent Jr.',
    'Glenn Robinson': 'Glenn Robinson III',
    'Guillermo Hernangomez': 'Willy Hernangomez',
    'Harry Giles': 'Harry Giles III',
    'J.J. Redick': 'JJ Redick',
    'J.R. Smith': 'JR Smith',
    'Jacob Evans III': 'Jacob Evans',
    'Jakarr Sampson': 'JaKarr Sampson',
    'Jake Wiley': 'Jacob Wiley',
    'Jalen Adams': 'Jaylen Adams',
    'James McAdoo': 'James Michael McAdoo',
    'Jaren Jackson': 'Jaren Jackson Jr.',
    "Johnny O'Bryant": "Johnny O'Bryant III",
    'Joseph Young': 'Joe Young',
    'Juan Hernangomez': 'Juancho Hernangomez',
    'K.J. McDaniels': 'KJ McDaniels',
    'Kelly Oubre': 'Kelly Oubre Jr.',
    'Kevin Knox': 'Kevin Knox II',
    'Kevin Porter': 'Kevin Porter Jr.',
    'Larry Drew': 'Larry Drew II',
    'Larry Nance': 'Larry Nance Jr.',
    'Luc Richard Mbah a Moute': 'Luc Mbah a Moute',
    'Marcus Morris': 'Marcus Morris Sr.',
    'Matt Williams': 'Matt Williams Jr.',
    'Melvin Frazier': 'Melvin Frazier Jr.',
    'Michael Porter': 'Michael Porter Jr.',
    'Mitch Creek': 'Mitchell Creek',
    'Moe Harkless': 'Maurice Harkless',
    'Mohamed Bamba': 'Mo Bamba',
    'Nazareth Mitrou-Long': 'Naz Mitrou-Long',
    'Nene Hilario': 'Nene',
    'Otto Porter': 'Otto Porter Jr.',
    'P.J. Dozier': 'PJ Dozier',
    'PJ Washington': 'P.J. Washington',
    'Raulzinho Neto': 'Raul Neto',
    'R.J. Hunter': 'RJ Hunter',
    'Robert Williams': 'Robert Williams III',
    'Sviatoslav Mykhailiuk': 'Svi Mykhailiuk',
    'TJ Warren': 'T.J. Warren',
    'Thomas Bryant ': 'Thomas Bryant',
    'Tim Hardaway': 'Tim Hardaway Jr.',
    'Tomas Satoransky ': 'Tomas Satoransky',
    'Troy Brown': 'Troy Brown Jr.',
    'Vince Hunter': 'Vincent Hunter',
    'Wade Baldwin': 'Wade Baldwin IV',
    'Wayne Selden Jr.': 'Wayne Selden',
    'Wendell Carter': 'Wendell Carter Jr.',
    'Wesley Iwundu': 'Wes Iwundu',
    'Zach Norvell': 'Zach Norvell Jr.'
}

LINEUP_NAME_TO_NBA_NAME = {
    'M. Fultz': 'Markelle Fultz',
    'N. Vucevic': 'Nikola Vucevic',
    'A. Aminu': 'Al-Farouq Aminu',
    'J. Isaac': 'Jonathan Isaac',
    'James Ennis': 'James Ennis III',
    'B. Bogdanovic': {
        'ATL': 'Bogdan Bogdanovic',
        'UTA': 'Bojan Bogdanovic'
        },
    'D. Hunter': "De'Andre Hunter",
    'O. Okongwu': 'Onyeka Okongwu',
    'M. Robinson': 'Mitchell Robinson',
    'S. Mykhailiuk': 'Svi Mykhailiuk',
    'D. Sirvydis': 'Deividas Sirvydis',
    'Danuel House': 'Danuel House Jr.',
    'D. Cousins': 'DeMarcus Cousins',
    'S. Brown': 'Sterling Brown',
    'Otto Porter': 'Otto Porter Jr.',
    'L. Markkanen': 'Lauri Markkanen',
    'W. Carter': 'Wendell Carter Jr.',
    'G. Temple': 'Garrett Temple',
    'D. Valentine': 'Denzel Valentine',
    'T. Young': 'Thaddeus Young',
    'P. Beverley': 'Patrick Beverley',
    'Marcus Morris': 'Marcus Morris Sr.',
    'D. Schroder': 'Dennis Schroder',
    'W. Matthews': 'Wesley Matthews',
    'K. Caldwell-Pope': 'Kentavious Caldwell-Pope',
    'M. Morris': 'Markieff Morris',
    'A. McKinnie': 'Alfonzo McKinnie',
    'H. Barnes': 'Harrison Barnes',
    'N. Bjelica': 'Nemanja Bjelica',
    'R. Holmes': 'Richaun Holmes',
    'Marvin Bagley': 'Marvin Bagley III',
    'H. Whiteside': 'Hassan Whiteside',
    'D. Lillard': 'Damian Lillard',
    'Derrick Jones': 'Derrick Jones Jr.',
    'R. Covington': 'Robert Covington',
    'M. Kidd-Gilchrist': 'Michael Kidd-Gilchrist',
    'C. Wood': 'Christian Wood',
    'M. Brogdon': 'Malcolm Brogdon',
    'V. Oladipo': 'Victor Oladipo',
    'J. Holiday': 'Justin Holiday',
    'D. Sabonis': 'Domantas Sabonis',
    'Brian Bowen': 'Brian Bowen II',
    'D. Garland': 'Darius Garland',
    'A. Drummond': 'Andre Drummond',
    'Kevin Porter': 'Kevin Porter Jr.',
    'S. Gilgeous-Alexander': 'Shai Gilgeous-Alexander',
    'H. Diallo': 'Hamidou Diallo',
    'A. Schofield': 'Admiral Schofield',
    'A. Pokusevski': 'Aleksej Pokusevski',
    'J. Jackson': 'Justin Jackson',
    'D. Murray': 'Dejounte Murray',
    'L. Aldridge': 'LaMarcus Aldridge',
    'K. Johnson': 'Keldon Johnson',
    'Q. Weatherspoon': 'Quinndary Weatherspoon',
    'Lonnie Walker': 'Lonnie Walker IV',
    'D. Graham': "Devonte' Graham",
    'G. Hayward': 'Gordon Hayward',
    'PJ Washington': 'P.J. Washington',
    'Tim Hardaway': 'Tim Hardaway Jr.',
    'J. Richardson': 'Josh Richardson',
    'K. Porzingis': 'Kristaps Porzingis',
    'D. DiVincenzo': 'Donte DiVincenzo',
    'K. Middleton': 'Khris Middleton',
    'G. Antetokounmpo': 'Giannis Antetokounmpo',
    'B. Clarke': 'Brandon Clarke',
    'J. Valanciunas': 'Jonas Valanciunas',
    'Jaren Jackson': 'Jaren Jackson Jr.',
    'K. Tillie': 'Killian Tillie',
    'J. Winslow': 'Justise Winslow',
    'D. Melton': "De'Anthony Melton",
    'D. Russell': "D'Angelo Russell",
    'A. Edwards': 'Anthony Edwards',
    'J. Hernangomez': 'Juancho Hernangomez',
    'K. Towns': 'Karl-Anthony Towns',
    'M. Porter': 'Michael Porter Jr.',
    'A. Wiggins': 'Andrew Wiggins',
    'Kelly Oubre': 'Kelly Oubre Jr.',
    'D. Green': 'Draymond Green',
    'D. Mitchell': 'Donovan Mitchell',
    'S. Harrison': 'Shaquille Harrison',
    'M. Dellavedova': 'Matthew Dellavedova',
    'G. Whittington': 'Greg Whittington',
    'C. Johnson': 'Cameron Johnson',
    'Troy Brown': 'Troy Brown Jr.',
    'J. Robinson': 'Jerome Robinson',
    'R. Westbrook': 'Russell Westbrook',
    'S. Dinwiddie': 'Spencer Dinwiddie',
    'D. Jordan': 'DeAndre Jordan',
    'N. Claxton': 'Nicolas Claxton',
    'M. Harrell': 'Montrezl Harrell',
    'P. Pritchard': 'Payton Pritchard',
    'R. Langford': 'Romeo Langford',
    'T. Thompson': 'Tristan Thompson',
    'M. Thybulle': 'Matisse Thybulle',
    'T. Ferguson': 'Terrance Ferguson',
    'K. Bates-Diop': 'Keita Bates-Diop',
    'D. Jeffries': 'DaQuan Jeffries',
    'R. Williams': 'Robert Williams III',
    'M. Chriss': 'Marquese Chriss',
    'A. Smailagic': 'Alen Smailagic',
    'C. Matthews': 'Charles Matthews',
    'Larry Nance': 'Larry Nance Jr.',
    'T. Satoransky': 'Tomas Satoransky',
    'A. Simons': 'Anfernee Simons',
    'RJ Hampton': 'R.J. Hampton',
    'D. Dotson': 'Damyean Dotson',
    'F. Ntilikina': 'Frank Ntilikina',
    'R. Bullock': 'Reggie Bullock',
    'X. Tillman': 'Xavier Tillman',
    'S. McDermott': 'Sean McDermott',
    'Charlie Brown': 'Charles Brown Jr.',
    'D. Finney-Smith': 'Dorian Finney-Smith',
    'U. Azubuike': 'Udoka Azubuike',
    'P. Patterson': 'Patrick Patterson',
    'D. McDermott': 'Doug McDermott',
    'D. Robinson': 'Duncan Robinson',
    'M. Harkless': 'Maurice Harkless',
    'A. Iguodala': 'Andre Iguodala',
    'B. Ingram': 'Brandon Ingram',
    'Z. Williamson': 'Zion Williamson',
    'W. Gabriel': 'Wenyen Gabriel',
    'P. Williams': 'Patrick Williams',
    'J. Green': 'JaMychal Green'
}

LINEUP_TEAM_TO_NBA_TEAM = {
    'NY': 'NYK',
    'SA': 'SAS',
    'GS': 'GSW',
    'PHO': 'PHX',
    'NO': 'NOP'
}
