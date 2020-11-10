# STRATEGY TESTING ----------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import fooStrat.evaluation as se
from fooStrat.modelling import est_prob
from fooStrat.response import con_res

# DATA PREPARATIONS ---------------------------------------------------------------------------------------------------
source_core = pd.read_pickle('data/pro_data/source_core.pkl')
flib = pd.read_pickle('data/pro_data/flib_e0.pkl')
match_odds = pd.read_pickle('data/pro_data/match_odds.pkl')
game_day = pd.read_pickle('data/pro_data/game_day.pkl')
results = con_res(data=source_core, obj=['wdl', 'gd'])

a = flib.query("team=='liverpool' & season=='2019' & field=='uncertainty_composite'")
source_core['div'].unique()


# SIGNAL EFFICACY -----------------------------------------------------------------------------------------------------
# 1. Is the hit ratio higher for teams that have a higher score?
# 2. Is the factor predictive (ic analysis)?
# 3. Would the factor on itself make money?

flib['field'].unique()
fesel = "home"
# feature evaluation analysis
fe = se.eval_feature(data=flib, results=results, feature=fesel, categorical=True)
# estimate probability & evaluate (only non-categorical)
pe, fme = est_prob(factors=flib,
                   results=results['wdl'][results['wdl']['field']=='win'],
                   feature=fesel)
fe['summary']
fe['edge_div']

# best features: avg_goal_scored, goal_superiority, not_failed_scoring,
# points_per_game, form_home, form_away, form_all, points_advantage, rank_position, turnaround_ability_last,
# h2h_next_opponent_advantage, h2h_next_opponent_chance, turnaround_ability_trend, odds_volatility,
# odds_accuracy, uncertainty_composite, home





# pnl analysis
# top bucket..
P = gsf_data.query('bucket==10 & div=="E0"').loc[:, ['season', 'div', 'date', 'team']]
P.sort_values(by=['season', 'date'], inplace=True)
O = match_odds.query('field == "odds_win"')
gsf_pnl = se.comp_pnl(positions=P, odds=O, results=results, event='win', stake=10)

# factor: max factor for every day played..
positions = flib.loc[flib.groupby(['div', 'season', 'date', 'field'])['val'].idxmax()].reset_index(drop=True)
positions = positions.loc[:,['div', 'season', 'date', 'team']]
# retrieve the right odds..
odds = match_odds.query('field == "odds_win"')
# calculate pnl
pnl_strats = se.comp_pnl(positions=positions, odds=odds, results=results, event='win', stake=10)











