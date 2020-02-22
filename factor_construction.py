# FACTOR CALCULATION ----------------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import fgoalsup, odds_fields, fodds, max_event_odds_sym, max_event_odds_asym
import plotly.express as px

# load source data..
source_core = pd.read_pickle('pro_data/source_core.pkl')
field_all = source_core['field'].unique()

source_core.query('field=="BbMx>2.5"')

# goal superiority rating -----------------------------------------------
# next: transform this score to a probability, 1st via constructing a z-score

data_fct = fgoalsup(data=source_core, field=['FTHG', 'FTAG'], k=5)


# create function to transform factor to z-score
# create a function to show the distribution

# across all leagues..
x = np.random.randn(1000)
hist_data = [x]
group_labels = ['distplot'] # name of the dataset

hist_data = [np.array(data_fct.val)]
fig = ff.create_distplot(hist_data, group_labels)
fig.show()

import matplotlib.pyplot as plt


# distribution ---------------
# determine distribution of scores
# https://plot.ly/python/distplot/



factor_library = data_fct
factor_library.to_pickle('./pro_data/factor_library.pkl')

# other approaches: find what kind of bets are the most mispriced
# factors: 3y h2h, last 10 matches in all competitions, average goals, moment of goals
# compute information coefficient (..lagged + odds/payoff required

# odds decomposition ----------------------------------------------------
# all relevant fields for the different bets..
field_home = list(odds_fields.get('odds_home_win'))
field_away = list(odds_fields.get('odds_away_win'))
field_both = list(odds_fields.get('odds_draw_win'))
# retrieve the odds..
match_odds = fodds(source_core, field_home=field_home, field_away=field_away, field_both=field_both)
match_odds.to_pickle('./pro_data/match_odds.pkl')


# pnl computation -------------------------------------------------------

# structure..
# factors: date, team, val with additional columns div, season, field
# odds: date, team, val with additional columns div, season, field
# comp_pnl(factors, odds, by)

# steps:
# 1. move factors forward (lag)
# 2. compute pnl for goal superiority -20:+20
# 3. highest ranking by factor for testing












