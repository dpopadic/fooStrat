# FACTOR CALCULATION ----------------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import fgoalsup, odds_fields, fodds, max_event_odds_sym, max_event_odds_ssym

# load plain field data..
data_prc = pd.read_pickle('pro_data/data_prc.pkl')
field_all = data_prc['field'].unique()
# data_fct = pd.read_pickle('pro_data/data_fct.pkl')

# goal superiority rating -----------------------------------------------
data_fct = fgoalsup(data_prc, field=['FTHG', 'FTAG'], k=5)
data_fct.to_pickle('./pro_data/data_fct.pkl')

# other approaches: find what kind of bets are the most mispriced
# factors: 3y h2h, last 10 matches in all competitions, average goals, moment of goals
# compute information coefficient (..lagged + odds/payoff required

# odds decomposition ----------------------------------------------------
# all relevant fields for the different bets..
field_home = list(odds_fields.get('odds_home_win'))
field_away = list(odds_fields.get('odds_away_win'))
field_both = list(odds_fields.get('odds_draw_win'))
# retrieve the odds..
data_odds = fodds(data_prc, field_home = field_home, field_away = field_away, field_both = field_both)
data_odds.to_pickle('./pro_data/data_odds.pkl')


# pnl computation -------------------------------------------------------

# structure..
# factors: date, team, val with additional columns div, season, field
# odds: date, team, val with additional columns div, season, field
# comp_pnl(factors, odds, by)











