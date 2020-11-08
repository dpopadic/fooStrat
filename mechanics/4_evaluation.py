# STRATEGY TESTING ----------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import fooStrat.evaluation as se
from fooStrat.modelling import est_prob

# DATA PREPARATIONS ---------------------------------------------------------------------------------------------------
source_core = pd.read_pickle('data/pro_data/source_core.pkl')
flib = pd.read_pickle('data/pro_data/flib_e0.pkl')
match_odds = pd.read_pickle('data/pro_data/match_odds.pkl')
game_day = pd.read_pickle('data/pro_data/game_day.pkl')
results = se.con_res(data=source_core, obj=['wdl', 'gd'])

a = flib.query("team=='liverpool' & season=='2019' & date=='2020-07-26'")
source_core['div'].unique()


# SIGNAL EFFICACY -----------------------------------------------------------------------------------------------------
# 1. Is the hit ratio higher for teams that have a higher score?
# 2. Is the factor predictive (ic analysis)?
# 3. Would the factor on itself make money?

flib['field'].unique()
fe = se.eval_feature(data=flib, results=results, feature="uncertainty_composite")

fe['summary']
fe['edge_div']

# best features: avg_goal_scored, goal_superiority, not_failed_scoring,
# points_per_game, form_home, form_away, form_all, points_advantage, rank_position, turnaround_ability_last,
# h2h_next_opponent_advantage, h2h_next_opponent_chance, turnaround_ability_trend, odds_volatility,
# odds_accuracy, uncertainty_composite, home

# compute probability & evaluate
gsf_proba, gsf_evaly = est_prob(factors=flib, results=results['wdl'], feature="uncertainty_composite")


# 2) home advantage signal -----
# Q: Do teams that play at home win more often than when they play away?
data_ha = flib.query('field=="home"')
data_ha.rename(columns={'val': 'bucket'}, inplace=True)
res_custom = results['wd'].query('field=="win"').drop('field', axis=1)
# compute the hit ratio for home-away
ha_edge = comp_edge(factor_data=data_ha, results=res_custom, byf=['overall', 'div'])
f0 = ['E0', 'D1']
ha_edge.query("field in @f0")





# PNL ANALYSIS --------------------------------------------------------------------------------------------------------

# run a logistic regression for all data to rertieve a probability
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











