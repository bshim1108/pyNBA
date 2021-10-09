def slate_contests_to_enter(df, max_slate_value, max_contest_value,
                            min_contest_fee, max_contest_fee, min_contest_entries):
    df['VALUE'] = df['ENTRYFEE'] * df['MAXENTRIES']
    df = df.loc[
        (df['ENTRYFEE'] >= min_contest_fee) &
        (df['ENTRYFEE'] <= max_contest_fee) &
        (df['TOTALENTRIES'] >= min_contest_entries) &
        (df['VALUE'] <= max_contest_value)
        ]
    if df.empty:
        return set()
    df = df.sort_values(by='ENTRYFEE')
    df['TOTAL_VALUE'] = df['VALUE'].expanding().sum()
    df = df.loc[df['TOTAL_VALUE'] < max_slate_value]
    return set(df['CONTESTID'].unique())

def get_prizes(lineups, contest_info):
    prizes = []
    for _, lineup in lineups.iterrows():
        prize = contest_info.loc[contest_info['MINPOINTS'] <= lineup['REALSCORE'], 'PRIZE'].max()
        prizes.append(prize)
    lineups['PRIZE'] = prizes
    return lineups