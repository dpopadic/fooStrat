# STRATEGY TESTING ----------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import con_res, comp_pnl, comp_edge, comp_bucket
import matplotlib.pyplot as plt
import seaborn as sns

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

# construct result objects
# win-lose-draw
res_wd = con_res(data=source_core, obj='wd', field='FTR')
# goals
res_gd = con_res(data=source_core, obj='gd', field=['FTHG', 'FTAG'])



# create info_coef function..

data = factor_library.query('field=="goal_superiority"')
results = res_gd

def info_coef(data, results):
    """Computes the information coefficient for a signal.

    Parameters:
    -----------
        data (dataframe):       A dataframe with factors and columns div, season, date, team, field, val
        results (dataframe):    A dataframe with results and columns season, div, date, team, val

    Returns:
    --------
        A dataframe of information coefficients.

    """
    R = results.rename(columns={'val': 'gd'}).copy()
    A = pd.merge(R, data, on=['div', 'season', 'team', 'date'], how='left')
    r = A.groupby(['div'])["gd"].corr(A["val"], method='spearman').reset_index()

    A["gd"].corr(A["val"], method='spearman')
    A["gd"].corr(A["val"], method='spearman')

    A.drop(['field'], axis=1, inplace=True)

    from scipy import stats
    stats.spearmanr([1, 2, 3, 4, 5], [5, 6, 7, 8, 7])
    x2n = np.random.randn(100, 2)
    stats.spearmanr(x2n)
    A.query('div=="E0" & season=="2019"')









# SIGNAL EFFICACY -----------------------------------------------------------------------------------------------------

# 1) goal superiority signal
# Q: Is the hit ratio higher for teams that have a higher gsf score?
# get factor scores
data_gsf = factor_library.query('field=="goal_superiority"')
# calculate buckets
data_gsf = comp_bucket(data_gsf, bucket_method='first', bucket=5)
# retrieve relevant results to test against
res_custom = res_wd.query('field=="win"').drop('field', axis=1)
# compute the hit ratio by bucket for the factor
gsf_edge = comp_edge(factor_data=data_gsf, results=res_custom, byf=['overall', 'div'])



# 2) home advantage signal
# Q: Do teams that play at home win more often than when they play away?
data_ha = factor_library.query('field=="home"')
data_ha.rename(columns={'val': 'bucket'}, inplace=True)
res_custom = res_wd.query('field=="win"').drop('field', axis=1)
# compute the hit ratio for home-away
ha_edge = comp_edge(factor_data=data_ha, results=res_custom, byf=['overall', 'div'])







# create a function to show the distribution
# across all leagues..
sns.distplot(gsf_edge.val, bins=100, kde=False)
# premier league vs bundesliga..
x0 = gsf_edge.query('field=="E0"').loc[:,'val']
x1 = gsf_edge.query('field=="D1"').loc[:,'val']
f, axes = plt.subplots(2, 1, figsize=(7, 7), sharex=True)
sns.distplot(x0, color="skyblue", ax=axes[0]).set_title('Premier League')
sns.distplot(x1, color="red", ax=axes[1]).set_title('Bundesliga')



lc1 = ml_map[ml_map['class']==1].loc[:, 'div'].values
A = gsf_edge.query('field in @lc1')
sns.set(style="dark")


g = sns.catplot(x="field", y="val", hue="bucket", data=A,
                height=6, kind="bar", palette="muted")
g.set_xticklabels(rotation=65, horizontalalignment='right')
# g.set_title('Historical Probability: Goal Superiority Signal')
g.set_ylabels("historical probability")
g.set_xlabels("")





iris = sns.load_dataset("iris")

sns.pairplot(iris, hue="species")

grid = sns.FacetGrid(gsf_edge, row="field", col="bucket", margin_titles=True)
grid.map(plt.hist, "val", bins=np.linspace(0, 40, 15));


# PNL ANALYSIS --------------------------------------------------------------------------------------------------------

# run a logistic regression for all data to rertieve a probability



# top bucket..
P = gsf_data.query('bucket==10 & div=="E0"').loc[:, ['season', 'div', 'date', 'team']]
P.sort_values(by=['season', 'date'], inplace=True)
O = match_odds.query('field == "odds_win"')
gsf_pnl = comp_pnl(positions=P, odds=O, results=results, event='win', stake=10)

# factor: max factor for every day played..
positions = factor_library.loc[factor_library.groupby(['div', 'season', 'date', 'field'])['val'].idxmax()].reset_index(drop=True)
positions = positions.loc[:,['div', 'season', 'date', 'team']]
# retrieve the right odds..
odds = match_odds.query('field == "odds_win"')
# calculate pnl
pnl_strats = comp_pnl(positions=positions, odds=odds, results=results, event='win', stake=10)






# APPENDIX ------------------------------------------------------------------------------------------------------------








