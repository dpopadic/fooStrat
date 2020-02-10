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

# all relevant fields for the different bets..
field_home = list(odds_fields.get('odds_home_win'))
field_away = list(odds_fields.get('odds_away_win'))
field_both = list(odds_fields.get('odds_draw_win'))
# retrieve the odds..
data_odds = fodds(data, field_home = field_home, field_away = field_away, field_both = field_both)
# verify
# data_odds[(data_odds['date']=='2012-05-19') & (data_odds['div']=='SP2')].sort_values('val')



# store..
data_fct.to_pickle('./pro_data/data_fct.pkl')

data_fct = pd.read_pickle('pro_data/data_fct.pkl')
# verifying..
# a = data_fct[data_fct['team']=='Liverpool']
# a[a['date']>='2019-08-17']
# looks good comparing to premier league results. next step is to include international
# competitions (eg. champions league) and define it as a function..







