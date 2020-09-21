# STRATEGY TESTING ----------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import con_res, comp_pnl, est_prob, eval_feature
import charut as cu
# next: transform this score to a probability, 1st via constructing a z-score
# does the factor work as hypothesized?
# what are fair odds?
# other approaches: find what kind of bets are the most mispriced
# factors: 3y h2h, last 10 matches in all competitions, average goals, moment of goals
# compute information coefficient (..lagged + odds/payoff required

# DATA PREPARATIONS ---------------------------------------------------------------------------------------------------
# load all required data
source_core = pd.read_pickle('pro_data/source_core.pkl')
flib = pd.read_pickle('pro_data/flib.pkl')
match_odds = pd.read_pickle('pro_data/match_odds.pkl')
game_day = pd.read_pickle('pro_data/game_day.pkl')

# construct test objects
res_obj = con_res(data=source_core, obj=['wdl', 'gd'])


# SIGNAL EFFICACY -----------------------------------------------------------------------------------------------------

# 1) goal superiority signal -----
# Q: Is the hit ratio higher for teams that have a higher gsf score?

fe = eval_feature(data=flib, results=res_obj, feature="goal_superiority")




# compute probability & evaluate
gsf_proba, gsf_evaly = est_prob(scores=data_gsf, result=res_custom, field = fm)




# match_odds need to have long- & short version
# bet structuring strategies:
# 1) specific residuals
# 2) all significant residuals
# 3) hedging
# create a scatterplot of resid vs implied & coloured pnl


# 2) home advantage signal -----
# Q: Do teams that play at home win more often than when they play away?
data_ha = flib.query('field=="home"')
data_ha.rename(columns={'val': 'bucket'}, inplace=True)
res_custom = res_obj['wd'].query('field=="win"').drop('field', axis=1)
# compute the hit ratio for home-away
ha_edge = comp_edge(factor_data=data_ha, results=res_custom, byf=['overall', 'div'])
f0 = ['E0', 'D1']
ha_edge.query("field in @f0")






# create a function to show the distribution
# across all leagues..
sns.distplot(gsf_edge.val, bins=100, kde=False)
# premier league vs bundesliga..
x0 = gsf_edge.query('field=="E0"').loc[:,'val']
x1 = gsf_edge.query('field=="D1"').loc[:,'val']
f, axes = plt.subplots(2, 1, figsize=(7, 7), sharex=True)
sns.distplot(x0, color="skyblue", ax=axes[0]).set_title('Premier League')
sns.distplot(x1, color="red", ax=axes[1]).set_title('Bundesliga')



# PNL ANALYSIS --------------------------------------------------------------------------------------------------------

# run a logistic regression for all data to rertieve a probability
# top bucket..
P = gsf_data.query('bucket==10 & div=="E0"').loc[:, ['season', 'div', 'date', 'team']]
P.sort_values(by=['season', 'date'], inplace=True)
O = match_odds.query('field == "odds_win"')
gsf_pnl = comp_pnl(positions=P, odds=O, results=results, event='win', stake=10)

# factor: max factor for every day played..
positions = flib.loc[flib.groupby(['div', 'season', 'date', 'field'])['val'].idxmax()].reset_index(drop=True)
positions = positions.loc[:,['div', 'season', 'date', 'team']]
# retrieve the right odds..
odds = match_odds.query('field == "odds_win"')
# calculate pnl
pnl_strats = comp_pnl(positions=positions, odds=odds, results=results, event='win', stake=10)


cu.plt_tsline(data=gsf_pnl.loc[:,['date', 'payoff_cum']],
              title="P&L of Goal Superiority Factor",
              subtitle="initial investment of 10$",
              var_names={'payoff_cum':'val'})









