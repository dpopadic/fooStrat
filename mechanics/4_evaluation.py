# STRATEGY TESTING ----------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import fooStrat.evaluation as se
from fooStrat.modelling import est_prob

# DATA PREPARATIONS ---------------------------------------------------------------------------------------------------
# load all required data
source_core = pd.read_pickle('data/pro_data/source_core.pkl')
flib = pd.read_pickle('data/pro_data/flib.pkl')
match_odds = pd.read_pickle('data/pro_data/match_odds.pkl')
game_day = pd.read_pickle('data/pro_data/game_day.pkl')
res_obj = se.con_res(data=source_core, obj=['wdl', 'gd'])



# SIGNAL EFFICACY -----------------------------------------------------------------------------------------------------
# Q: Is the hit ratio higher for teams that have a higher gsf score?
# H: The higher the score, the higher the hit ratio.
fe = se.eval_feature(data=flib, results=res_obj, feature="goal_superiority")

# compute probability & evaluate
gsf_proba, gsf_evaly = est_prob(scores=data_gsf, result=res_custom, field = fm)


# 2) home advantage signal -----
# Q: Do teams that play at home win more often than when they play away?
data_ha = flib.query('field=="home"')
data_ha.rename(columns={'val': 'bucket'}, inplace=True)
res_custom = res_obj['wd'].query('field=="win"').drop('field', axis=1)
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











