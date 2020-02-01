# FACTOR CALCULATION ----------------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import fgoalsup, odds_fields

# load plain field data..
data_prc = pd.read_pickle('pro_data/data_prc.pkl')
field_all = data_prc['field'].unique()

# goal superiority rating -----------------------------------------------
data_fct = fgoalsup(data_prc, field=['FTHG', 'FTAG'], k=5)
# other approaches: find what kind of bets are the most mispriced
# factors: 3y h2h, last 10 matches in all competitions, average goals, moment of goals
# compute information coefficient (..lagged + odds/payoff required)
data = data_prc
field = list(odds_fields.get('odds_draw_win'))
odds_fields.keys()


# write a function to check whether a field is in all tables and how many times..

# odds decomposition ----------------------------------------------------
# which odds to take for tests?
# get odds in right format.. -> div | date | season | team | field | val
def fodds(data, field, k):
    """Calculates the goal superiority factor across divisions and seasons for each team on a
    rolling basis.

    """
    o_h = list(odds_fields.get('odds_home_win'))
    o_a = list(odds_fields.get('odds_away_win'))
    o_d = list(odds_fields.get('odds_draw_win'))
    # --- home
    # filter relevant fields..
    data_ed = data.loc[data['field'].isin(field),['date','div','season','home_team','field','val']]
    data_ed.rename(columns={'home_team':'team'}, inplace=True)
    data_ed['val'] = pd.to_numeric(data_ed.loc[:, 'val'], errors='coerce')
    # a = data_ed.loc[(data_ed['season']=='2019/2020') & (data_ed['div']=='Switzerland Super League') & (data_ed['date']=='2019-10-05'),:]
    # retrieve the best odds..
    max_odds = data_ed.groupby(['season','div','date','team']).max()['val'].reset_index()
    max_odds['field'] = 'odds_win'

    # --- away
    # filter relevant fields..
    data_ed = data.loc[data['field'].isin(field),['date','div','season','away_team','field','val']]
    data_ed.rename(columns={'away_team':'team'}, inplace=True)
    data_ed['val'] = pd.to_numeric(data_ed.loc[:, 'val'], errors='coerce')
    # retrieve the best odds..
    max_odds = data_ed.groupby(['season','div','date','team']).max()['val'].reset_index()
    max_odds['field'] = 'odds_win'

    # --- draw
    # need a function that concatenates a home/away by a field in the form: div, season, team, date, team, field, val
    data_ed = data[(data['field'].isin(field))]
    data_ed['val'] = pd.to_numeric(data_ed.loc[:, 'val'], errors='coerce')
    max_odds = data_ed.groupby(['season', 'div', 'date', 'home_team','away_team']).max()['val'].reset_index()
    # home numbers
    max_odds_dh = max_odds.loc[:,max_odds.columns!='away_team']
    max_odds_dh.rename(columns={'home_team': 'team'}, inplace=True)
    max_odds_dh['field'] = 'odds_draw'
    # away numbers
    max_odds_da = max_odds.loc[:, max_odds.columns != 'home_team']
    max_odds_da.rename(columns={'away_team': 'team'}, inplace=True)
    max_odds_da['field'] = 'odds_draw'
    max_odds_draw = pd.concat([max_odds_dh, max_odds_da], axis=0, sort=False, ignore_index=True)
    














# store..
data_fct.to_pickle('./pro_data/data_fct.pkl')

data_fct = pd.read_pickle('pro_data/data_fct.pkl')
# verifying..
# a = data_fct[data_fct['team']=='Liverpool']
# a[a['date']>='2019-08-17']
# looks good comparing to premier league results. next step is to include international
# competitions (eg. champions league) and define it as a function..







