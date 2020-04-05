# STRATEGY TESTING ----------------------------------------------------------------------------------------------------
import pandas as pd
from foostrat_utils import con_res, comp_pnl, comp_edge

# next: transform this score to a probability, 1st via constructing a z-score
# does the factor work as hypothesized?
# what are fair odds?
# next steps:
# update process function
# calculate IC
# derive probabilities
# calculate ic's (correlation between factor & goal difference in next game)
# problem: Chelsea missing on 22/02/2020!
# other approaches: find what kind of bets are the most mispriced
# factors: 3y h2h, last 10 matches in all competitions, average goals, moment of goals
# compute information coefficient (..lagged + odds/payoff required


# DATA PREPARATIONS ---------------------------------------------------------------------------------------------------
# load all required data
source_core = pd.read_pickle('pro_data/source_core.pkl')
factor_library = pd.read_pickle('pro_data/factor_library.pkl')
match_odds = pd.read_pickle('pro_data/match_odds.pkl')

# construct results object
results = con_res(source_core, field=['FTR'])


# SIGNAL EFFICACY -----------------------------------------------------------------------------------------------------

# 1) goal superiority signal
gsf_data = factor_library.query('field=="goal_superiority"')
res_custom = results.query('field=="win"').drop('field', axis=1)
gsf_edge = comp_edge(factor_data=gsf_data, results=res_custom, byf=['overall', 'div'])





# PNL ANALYSIS --------------------------------------------------------------------------------------------------------

# factor: max factor for every day played..
positions = factor_library.loc[factor_library.groupby(['div', 'season', 'date', 'field'])['val'].idxmax()].reset_index(drop=True)
positions = positions.loc[:,['div', 'season', 'date', 'team']]
# retrieve the right odds..
odds = match_odds.query('field == "odds_win"')
# calculate pnl
pnl_strats = comp_pnl(positions=positions, odds=odds, results=results, event='win', stake=10)






# APPENDIX ------------------------------------------------------------------------------------------------------------
# create a function to show the distribution
# across all leagues..
sns.distplot(data_gsf_0.val, bins=100, kde=False)
# premier league vs bundesliga..
x0 = data_gsf_0.query('div=="E0"').loc[:,'val']
x1 = data_gsf_0.query('div=="D1"').loc[:,'val']
f, axes = plt.subplots(2, 1, figsize=(7, 7), sharex=True)
sns.distplot(x0, color="skyblue", ax=axes[0]).set_title('Premier League')
sns.distplot(x1, color="red", ax=axes[1]).set_title('Bundesliga')








