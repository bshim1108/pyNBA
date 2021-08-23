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

ROTOGURU_NAME_TO_NBA_NAME = {
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
    'Sheldon McClellan': 'Sheldon Mac',
    'Xavier Tillman': 'Xavier Tillman Sr.',
    'Didi Louzada Silva': 'Didi Louzada',
    'Kenyon Martin Jr.': 'KJ Martin',
}
BAD_ROTOGURU_DATES = ['2020-01-21']

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
    'M. Morris': {
        'LAL': 'Markieff Morris',
        'LAC': 'Marcus Morris Sr.',
        'DEN': 'Monte Morris'
        },
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
    'J. Holiday': {
        'IND': 'Justin Holiday',
        'MIL': 'Jrue Holiday'
        },
    'D. Sabonis': 'Domantas Sabonis',
    'Brian Bowen': 'Brian Bowen II',
    'D. Garland': 'Darius Garland',
    'A. Drummond': 'Andre Drummond',
    'Kevin Porter': 'Kevin Porter Jr.',
    'S. Gilgeous-Alexander': 'Shai Gilgeous-Alexander',
    'H. Diallo': 'Hamidou Diallo',
    'A. Schofield': 'Admiral Schofield',
    'A. Pokusevski': 'Aleksej Pokusevski',
    'J. Jackson': {
        'OKC': 'Justin Jackson',
        'MEM': 'Jaren Jackson Jr.',
        'DET': 'Josh Jackson'
        },
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
    'D. Green': {
        'GSW': 'Draymond Green',
        'PHI': 'Danny Green'
        },
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
    'D. Dotson': {
        'CLE': 'Damyean Dotson',
        'CHI': 'Devon Dotson'
        },
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
    'J. Green': {
        'DEN': 'JaMychal Green',
        'BOS': 'Javonte Green'
        },
    'G. Riller': 'Grant Riller',
    'K. Porter': 'Kevin Porter Jr.',
    'D. Smith': 'Dennis Smith Jr.',
    'A. Rivers': 'Austin Rivers',
    'O. Spellman': 'Omari Spellman',
    'T. Warren': 'T.J. Warren',
    'G. Bitadze': 'Goga Bitadze',
    'B. Bowen': 'Brian Bowen II',
    'J. Lamb': 'Jeremy Lamb',
    'G. Vincent': 'Gabe Vincent',
    'J. Ennis': 'James Ennis III',
    'R. Hachimura': 'Rui Hachimura',
    'D. Augustin': 'D.J. Augustin',
    'K. Walker': 'Kemba Walker',
    'W. Magnay': 'Will Magnay',
    'N. Powell': 'Norman Powell',
    'P. McCaw': 'Patrick McCaw',
    'D. Gallinari': 'Danilo Gallinari',
    'K. Huerter': 'Kevin Huerter',
    'C. Reddish': 'Cam Reddish',
    'B. Goodwin': 'Brandon Goodwin',
    'C. Capela': 'Clint Capela',
    'R. Rondo': 'Rajon Rondo',
    'T. Ariza': 'Trevor Ariza',
    'T. Maledon': 'Theo Maledon',
    'D. Miller': 'Darius Miller',
    'B. McLemore': 'Ben McLemore',
    'J. McLaughlin': 'Jordan McLaughlin',
    'J. Nowell': 'Jaylen Nowell',
    'L. Samanic': 'Luka Samanic',
    'D. White': 'Derrick White',
    'J. Porter': 'Jontay Porter',
    'J. Parker': 'Jabari Parker',
    'D. Favors': 'Derrick Favors',
    'Z. Collins': 'Zach Collins',
    'N. Little': 'Nassir Little',
    'M. Kleber': 'Maxi Kleber',
    'F. Kaminsky': 'Frank Kaminsky',
    'A. Nader': 'Abdel Nader',
    'D. Saric': 'Dario Saric',
    'G. Mathews': 'Garrison Mathews',
    'C. Winston': 'Cassius Winston',
    'A. Davis': 'Anthony Davis',
    'J. Murray': 'Jamal Murray',
    'K. Leonard': 'Kawhi Leonard',
    'J. Scrubb': 'Jay Scrubb',
    'B. Biyombo': 'Bismack Biyombo',
    'C. Zeller': 'Cody Zeller',
    'I. Okoro': 'Isaac Okoro',
    'D. Windler': 'Dylan Windler',
    'Kevin Knox': 'Kevin Knox II',
    'I. Quickley': 'Immanuel Quickley',
    'E. Sumner': 'Edmond Sumner',
    'L. James': 'LeBron James',
    'J. Smith': 'Jalen Smith',
    'S. Doumbouya': 'Sekou Doumbouya',
    'J. Okafor': 'Jahlil Okafor',
    'B. Griffin': 'Blake Griffin',
    'D. Rose': 'Derrick Rose',
    'K. Durant': 'Kevin Durant',
    'E. Gordon': 'Eric Gordon',
    'M. Jones': 'Mason Jones',
    'K. Martin': 'Kenyon Martin Jr.',
    'C. Anthony': {
        'POR': 'Carmelo Anthony',
        'ORL': 'Cole Anthony'
        },
    'A. Caruso': 'Alex Caruso',
    'K. Irving': 'Kyrie Irving',
    'J. Toscano-Anderson': 'Juan Toscano-Anderson',
    'J. Embiid': 'Joel Embiid',
    'F. Korkmaz': 'Furkan Korkmaz',
    'T. Craig': 'Torrey Craig',
    'M. Leonard': 'Meyers Leonard',
    'J. Butler': 'Jimmy Butler',
    'J. Okogie': 'Josh Okogie',
    'O. Toppin': 'Obi Toppin',
    'G. Hill': 'George Hill',
    'J. Culver': 'Jarrett Culver',
    'J. Morant': 'Ja Morant',
    'T. Luwawu-Cabarrot': 'Timothe Luwawu-Cabarrot',
    'Gary Trent': 'Gary Trent Jr.',
    'J. Tatum': 'Jayson Tatum',
    'G. Williams': 'Grant Williams',
    'K. Love': 'Kevin Love',
    'C. Hutchison': 'Chandler Hutchison',
    'T. Ross': 'Terrence Ross',
    'R. Arcidiacono': 'Ryan Arcidiacono',
    'A. Pasecniks': 'Anzejs Pasecniks',
    'K. Olynyk': 'Kelly Olynyk',
    'K. Hayes': 'Killian Hayes',
    'F. Jackson': 'Frank Jackson',
    'G. Allen': 'Grayson Allen',
    'E. Paschall': 'Eric Paschall',
    'T. Haliburton': 'Tyrese Haliburton',
    'E. Fournier': 'Evan Fournier',
    'C. Okeke': 'Chuma Okeke',
    'J. Harden': 'James Harden',
    "R. O'Neale": "Royce O'Neale",
    'L. Doncic': 'Luka Doncic',
    'R. Hood': 'Rodney Hood',
    'J. Teague': 'Jeff Teague',
    'P. Washington': 'P.J. Washington',
    'A. Bradley': 'Avery Bradley',
    'S. Thornwell': 'Sindarius Thornwell',
    'P. Connaughton': 'Pat Connaughton',
    'S. Merrill': 'Sam Merrill',
    'M. Carter-Williams': 'Michael Carter-Williams',
    'M. Smart': 'Marcus Smart',
    'D. House': 'Danuel House Jr.',
    'T. Prince': 'Taurean Prince',
    'J. Konchar': 'John Konchar',
    'J. Morgan': 'Juwan Morgan',
    'R. Kurucs': 'Rodions Kurucs',
    'A. Hagans': 'Ashton Hagans',
    'P. George': 'Paul George',
    'J. Lecque': 'Jalen Lecque',
    'N. Noel': 'Nerlens Noel',
    'N. Richards': 'Nick Richards',
    'J. Brantley': 'Jarrell Brantley',
    'W. Ellington': 'Wayne Ellington',
    'R. Perry': 'Reggie Perry',
    'C. Sexton': 'Collin Sexton',
    'D. Exum': 'Dante Exum',
    'T. Johnson': 'Tyler Johnson',
    'W. Cauley-Stein': 'Willie Cauley-Stein',
    'D. Eubanks': 'Drew Eubanks',
    'N. Melli': 'Nicolo Melli',
    'Taj Gibson': 'Taj Gibson',
    'S. Curry': 'Stephen Curry',
    'J. Poole': 'Jordan Poole',
    'D. Fox': "De'Aaron Fox",
    'A. Gordon': 'Aaron Gordon',
    'B. Thomas': 'Brodric Thomas',
    'S. Milton': 'Shake Milton',
    'T. Harris': 'Tobias Harris',
    'V. Poirier': 'Vincent Poirier',
    'M. Scott': 'Mike Scott',
    'B. Fernando': 'Bruno Fernando',
    'J. Brunson': 'Jalen Brunson',
    'B. Simmons': 'Ben Simmons',
    'C. Payne': 'Cameron Payne',
    'D. Mathias': 'Dakota Mathias',
    'T. McConnell': 'T.J. McConnell',
    'B. Beal': 'Bradley Beal',
    'T. Bryant': 'Thomas Bryant',
    'O. Porter': 'Otto Porter Jr.',
    'J. Brown': 'Jaylen Brown',
    'S. Ojeleye': 'Semi Ojeleye',
    'K. Looney': 'Kevon Looney',
    'B. Hield': 'Buddy Hield',
    'P. Achiuwa': 'Precious Achiuwa',
    'B. Adebayo': 'Bam Adebayo',
    'G. Dragic': 'Goran Dragic',
    'U. Haslem': 'Udonis Haslem',
    'K. Nunn': 'Kendrick Nunn',
    'J. Dudley': 'Jared Dudley',
    'D. Vassell': 'Devin Vassell',
    'D. DeRozan': 'DeMar DeRozan',
    'T. Bradley': 'Tony Bradley',
    'G. Harris': 'Gary Harris',
    'B. Portis': 'Bobby Portis',
    'D. Powell': 'Dwight Powell',
    'N. Alexander-Walker': 'Nickeil Alexander-Walker',
    'E. Bledsoe': 'Eric Bledsoe',
    'I. Zubac': 'Ivica Zubac',
    'J. Nurkic': 'Jusuf Nurkic',
    'K. Blevins': 'Keljin Blevins',
    'K. Antetokounmpo': 'Kostas Antetokounmpo',
    'C. LeVert': 'Caris LeVert',
    'E. Hughes': 'Elijah Hughes',
    'T. Hardaway': 'Tim Hardaway Jr.',
    'M. Turner': 'Myles Turner',
    'J. Sampson': 'JaKarr Sampson',
    'C. Edwards': 'Carsen Edwards',
    'K. Dunn': 'Kris Dunn',
    'T. Herro': 'Tyler Herro',
    'J. Vanderbilt': 'Jarred Vanderbilt',
    'R. Rubio': 'Ricky Rubio',
    'D. Jones': {
        'POR': 'Derrick Jones Jr.',
        'SAC': 'Damian Jones'
        },
    'M. Bagley': 'Marvin Bagley III',
    'J. Ramsey': "Jahmi'us Ramsey",
    'L. Williams': 'Lou Williams',
    'C. McCollum': 'CJ McCollum',
    'T. Davis': 'Terence Davis',
    'T. Rozier': 'Terry Rozier',
    'N. Darling': 'Nate Darling',
    'C. Silva': 'Chris Silva',
    'S. Adams': 'Steven Adams',
    'N. Marshall': 'Naji Marshall',
    'D. Gafford': 'Daniel Gafford',
    'L. Nance': 'Larry Nance Jr.',
    'J. Adams': 'Jaylen Adams',
    'M. Diakite': 'Mamadi Diakite',
    'D. Nwaba': 'David Nwaba',
    'D. Booker': 'Devin Booker',
    'J. Harris': 'Jalen Harris',
    'R. Jackson': 'Reggie Jackson',
    'I. Shumpert': 'Iman Shumpert',
    'J. Wiseman': 'James Wiseman',
    'J. Johnson': 'James Johnson',
    'L. Walker': 'Lonnie Walker IV',
    'J. Crowder': 'Jae Crowder',
    'F. Campazzo': 'Facundo Campazzo',
    'M. Muscala': 'Mike Muscala',
    'I. Roby': 'Isaiah Roby',
    'C. Martin': 'Caleb Martin',
    'I. Stewart': 'Isaiah Stewart',
    'M. Plumlee': 'Mason Plumlee',
    'D. Oturu': 'Daniel Oturu',
    'K. Williams': 'Kenrich Williams',
    'M. Conley': 'Mike Conley',
    'D. Bane': 'Desmond Bane',
    'F. Mason': 'Frank Mason',
    'J. Nwora': 'Jordan Nwora',
    'E. Payton': 'Elfrid Payton',
    'Dennis Smith': 'Dennis Smith Jr.',
    'D. Wright': 'Delon Wright',
    'M. Beasley': 'Malik Beasley',
    'C. Metu': 'Chimezie Metu',
    'N. Hinton': 'Nate Hinton',
    'T. Terry': 'Tyrell Terry',
    'D. Bembry': "DeAndre' Bembry",
    'S. Johnson': 'Stanley Johnson',
    'M. Flynn': 'Malachi Flynn',
    'P. Siakam': 'Pascal Siakam',
    'F. VanVleet': 'Fred VanVleet',
    'L. Kornet': 'Luke Kornet',
    'H. Giles': 'Harry Giles III',
    'R. Woodard': 'Robert Woodard II',
    'D. Bazley': 'Darius Bazley',
    'M. Howard': 'Markus Howard',
    'P. Millsap': 'Paul Millsap',
    'R. Hampton': 'R.J. Hampton',
    'P. Tucker': 'P.J. Tucker',
    'D. Bertans': 'Davis Bertans',
    'S. Ibaka': 'Serge Ibaka',
    'D. Cacok': 'Devontae Cacok',
    'L. Shamet': 'Landry Shamet',
    'R. McGruder': 'Rodney McGruder',
    'C. Joseph': 'Cory Joseph',
    'M. Wagner': 'Moritz Wagner',
    'B. Forbes': 'Bryn Forbes',
    'M. Bridges': {
        'PHX': 'Mikal Bridges',
        'CHA': 'Miles Bridges'
        },
    'J. McGee': 'JaVale McGee',
    'J. McDaniels': {
        'MIN': 'Jaden McDaniels',
        'CHA': 'Jalen McDaniels'
        },
    'B. Wanamaker': 'Brad Wanamaker',
    'L. Ball': {
        'NOP': 'Lonzo Ball',
        'CHA': 'LaMelo Ball'
        },
    'M. Thomas': 'Matt Thomas',
    'I. Hartenstein': 'Isaiah Hartenstein',
    'P. Watson': 'Paul Watson',
    'J. Hayes': 'Jaxson Hayes',
    'J. Randle': 'Julius Randle',
    'J. Grant': 'Jerami Grant',
    'B. Marjanovic': 'Boban Marjanovic',
    'L. Dort': 'Luguentz Dort',
    'J. Allen': 'Jarrett Allen',
    'Z. LaVine': 'Zach LaVine',
    'D. Theis': 'Daniel Theis',
    'I. Brazdeikis': 'Ignas Brazdeikis',
    'J. Collins': 'John Collins',
    'G. Dieng': 'Gorgui Dieng',
    'Kira Lewis': 'Kira Lewis Jr.',
    'T. Maxey': 'Tyrese Maxey',
    'R. Lopez': 'Robin Lopez',
    'J. Henson': 'John Henson',
    'A. Brooks': 'Armoni Brooks',
    'G. Payton': 'Gary Payton II'
}

UNKNOWN_PLAYERS = ['Shaquille Harrison', 'J. Bell' ]

LINEUP_TEAM_TO_NBA_TEAM = {
    'NY': 'NYK',
    'SA': 'SAS',
    'GS': 'GSW',
    'PHO': 'PHX',
    'NO': 'NOP'
}

NUMBERFIRE_NAME_TO_NBA_NAME = {
    'Kelly Oubre': 'Kelly Oubre Jr.',
    'C.J. McCollum': 'CJ McCollum',
    'Harry Giles': 'Harry Giles III',
    'C.J. Elleby': 'CJ Elleby',
    'Kevin Knox': 'Kevin Knox II',
    'Marcus Morris': 'Marcus Morris Sr.',
    'Patrick Mills': 'Patty Mills',
    'Lonnie Walker': 'Lonnie Walker IV',
    'DeAndre Bembry': "DeAndre' Bembry",
    'James Ennis': 'James Ennis III',
    'Otto Porter': 'Otto Porter Jr.',
    'Mohamed Bamba': 'Mo Bamba',
    'P.J. Dozier': 'PJ Dozier',
    'J.J. Redick': 'JJ Redick',
    'Robert Williams': 'Robert Williams III',
    'PJ Washington': 'P.J. Washington',
    'Wesley Iwundu': 'Wes Iwundu',
    'Bruce Brown Jr.': 'Bruce Brown',
    'Dennis Smith': 'Dennis Smith Jr.',
    'Juan Hernangomez': 'Juancho Hernangomez',
    'Sviatoslav Mykhailiuk': 'Svi Mykhailiuk',
    'Troy Brown': 'Troy Brown Jr.',
    'Terence Davis II': 'Terence Davis'
}

DAILY_FANTASY_FUEL_START_DATE = '2019-10-22'
DAILY_FANTASY_FUEL_SITES = ['draftkings', 'fanduel']
DAILY_FANTASY_FUEL_BAD_DATES = ['2020-01-21', '2020-12-22']

ROTOWIRE_START_DATE = '2015-10-27'
ROTOWIRE_NAME_TO_NBA_NAME = {
    'Cam Reynolds': 'Cameron Reynolds',
    'Charlie Brown': 'Charles Brown Jr.',
    'Danuel House': 'Danuel House Jr.',
    'Derrick Jones': 'Derrick Jones Jr.',
    'Gary Payton': 'Gary Payton II',
    'Gary Trent': 'Gary Trent Jr.',
    'Harry Giles': 'Harry Giles III',
    'Jaren Jackson': 'Jaren Jackson Jr.',
    'Joseph Young': 'Joe Young',
    'Kelly Oubre': 'Kelly Oubre Jr.',
    'Kevin Knox': 'Kevin Knox II',
    'Kevin Porter': 'Kevin Porter Jr.',
    'Kenyon Martin': 'KJ Martin',
    'Kira Lewis': 'Kira Lewis Jr.',
    'Larry Nance': 'Larry Nance Jr.',
    'Lonnie Walker': 'Lonnie Walker IV',
    'Marcus Morris': 'Marcus Morris Sr.',
    'Marvin Bagley': 'Marvin Bagley III',
    'Michael Porter': 'Michael Porter Jr.',
    'Otto Porter': 'Otto Porter Jr.',
    'Robert Williams': 'Robert Williams III',
    'Robert Woodard': 'Robert Woodard II',
    'T.J. Leaf': 'TJ Leaf',
    'Tim Hardaway': 'Tim Hardaway Jr.',
    'Troy Brown': 'Troy Brown Jr.',
    'Vernon Carey': 'Vernon Carey Jr.',
    'Wendell Carter': 'Wendell Carter Jr.',
    'Xavier Tillman': 'Xavier Tillman Sr.',
    'Zach Norvell': 'Zach Norvell Jr.'
}

LINESTARAPP_SITEID_TO_SITE = {
    1: 'DRAFTKINGS',
    2: 'FANDUEL'
}
LINESTARAPP_MIN_PID = 207
LINESTARAPP_MIN_DEF_PID = 607
LINESTARAPP_INVALID_PID_RANGE = (1168, 1292)
LINESTARAPP_INVALID_PID_VALUES = set([1309])
LINESTARAPP_TEAM_TO_NBA_TEAM = {
    'NO': 'NOP',
    'GS': 'GSW',
    'NY': 'NYK',
    'SA': 'SAS',
    'PHO': 'PHX'
}
LINESTARAPP_NAME_TO_NBA_NAME = {
    ' Nene': 'Nene',
    'A.J. Hammons': 'AJ Hammons',
    'Andrew White': 'Andrew White III',
    'André Miller': 'Andre Miller',
    'B.J. Johnson': 'BJ Johnson',
    'Billy Garrett Jr.': 'Billy Garrett',
    'Brad Beal': 'Bradley Beal',
    'Brian Bowen': 'Brian Bowen II',
    'Bruce Brown Jr.': 'Bruce Brown',
    'Bryce Jones': 'Bryce Dejean-Jones',
    'C.J. McCollum': 'CJ McCollum',
    'C.J. Miles': 'CJ Miles',
    'Cameron Reddish': 'Cam Reddish',
    'Charles Brown': 'Charles Brown Jr.',
    'Charlie Brown': 'Charles Brown Jr.',
    'Cristiano Felício': 'Cristiano Felicio',
    'D.J. Stephens': 'DJ Stephens',
    'Danté Exum': 'Dante Exum',
    'Danuel House': 'Danuel House Jr.',
    'Dejounte Murray': 'Dejounte Murray',
    'Denis Schroder': 'Dennis Schroder',
    'Dennis Smith': 'Dennis Smith Jr.',
    'Derrick Jones': 'Derrick Jones Jr.',
    'Derrick Walton': 'Derrick Walton Jr.',
    'Didi Louzada Silva': 'Didi Louzada',
    'Frank Mason III': 'Frank Mason',
    'Gary Trent': 'Gary Trent Jr.',
    'Glenn Robinson': 'Glenn Robinson III',
    'Guillermo Hernangomez': 'Willy Hernangomez',
    'Guillermo Hernangómez': 'Willy Hernangomez',
    'Harry Giles': 'Harry Giles III',
    'Ishmael Smith': 'Ish Smith',
    'J.J. Hickson': 'JJ Hickson',
    'J.J. Redick': 'JJ Redick',
    'J.R. Smith': 'JR Smith',
    'Jacob Evans III': 'Jacob Evans',
    'Jakarr Sampson': 'JaKarr Sampson',
    'James Ennis': 'James Ennis III',
    'James Webb': 'James Webb III',
    'Jaren Jackson': 'Jaren Jackson Jr.',
    "Johnny O'Bryant": "Johnny O'Bryant III",
    'Joseph Young': 'Joe Young',
    'Juan Hernangomez': 'Juancho Hernangomez',
    'Juancho Hernangómez': 'Juancho Hernangomez',
    'José Calderón': 'Jose Calderon',
    'Jose Juan Barea': 'J.J. Barea',
    'K.J. McDaniels': 'KJ McDaniels',
    'KJ Martin Jr.': 'KJ Martin',
    'Kelly Oubre': 'Kelly Oubre Jr.',
    'Kenyon Martin': 'KJ Martin',
    'Kevin Knox': 'Kevin Knox II',
    'Kevin Martín': 'Kevin Martin',
    'Kevin Porter': 'Kevin Porter Jr.',
    'Kira Lewis': 'Kira Lewis Jr.',
    'Larry Nance': 'Larry Nance Jr.',
    'Lonnie Walker': 'Lonnie Walker IV',
    'Louis Amundson': 'Lou Amundson',
    'Louis Williams': 'Lou Williams',
    'Luc Richard Mbah a Moute': 'Luc Mbah a Moute',
    'Manu Ginóbili': 'Manu Ginobili',
    'Marcus Morris': 'Marcus Morris Sr.',
    'Marvin Bagley': 'Marvin Bagley III',
    'Melvin Frazier': 'Melvin Frazier Jr.',
    'Michael Porter': 'Michael Porter Jr.',
    'Mitch Creek': 'Mitchell Creek',
    'Moe Harkless': 'Maurice Harkless',
    'Mohamed Bamba': 'Mo Bamba',
    'Nazareth Mitrou-Long': 'Naz Mitrou-Long',
    'Nene Hilario': 'Nene',
    'Nicolás Brussino': 'Nicolas Brussino',
    'Nicolás Laprovittola': 'Nicolas Laprovittola',
    'Otto Porter': 'Otto Porter Jr.',
    'P.J. Dozier': 'PJ Dozier',
    'P.J. Hairston': 'PJ Hairston',
    'PJ Tucker': 'P.J. Tucker',
    'PJ Washington': 'P.J. Washington',
    'Patrick Mills': 'Patty Mills',
    'Phil (Flip) Pressey': 'Phil Pressey',
    'R.J. Hunter': 'RJ Hunter',
    'Robert Williams': 'Robert Williams III',
    'Robert Woodard': 'Robert Woodard II',
    'Roy Devyn Marble': 'Devyn Marble',
    'Sergio Rodríguez': 'Sergio Rodriguez',
    'Sergio  Rodríguez': 'Sergio Rodriguez',
    'Sheldon McClellan': 'Sheldon Mac',
    'Stephen Zimmerman Jr.': 'Stephen Zimmerman',
    'Sviatoslav Mykhailiuk': 'Svi Mykhailiuk',
    'T.J. Leaf': 'TJ Leaf',
    'TJ Warren': 'T.J. Warren',
    'Tim Hardaway': 'Tim Hardaway Jr.',
    'Timothé Luwawu-Cabarrot': 'Timothe Luwawu-Cabarrot',
    'Troy Brown': 'Troy Brown Jr.',
    'Vernon Carey': 'Vernon Carey Jr.',
    'Vince Hunter': 'Vincent Hunter',
    'Walter Lemon': 'Walt Lemon Jr.',
    'Walter Lemon Jr.': 'Walt Lemon Jr.',
    'Walter Tavares': 'Edy Tavares',
    'Wayne Selden Jr.': 'Wayne Selden',
    'Wendell Carter': 'Wendell Carter Jr.',
    'Xavier Tillman': 'Xavier Tillman Sr.',
    'Zach Norvell': 'Zach Norvell Jr.',
    'Álex Abrines': 'Alex Abrines'
}