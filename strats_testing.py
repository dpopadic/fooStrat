# STRATEGY TESTING ----------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import con_res, comp_pnl, comp_edge, comp_bucket, info_coef, est_prob, \
    comp_mispriced, con_res_wd, con_mod_datset
import charut as cu
# next: transform this score to a probability, 1st via constructing a z-score
# does the factor work as hypothesized?
# what are fair odds?
# next steps:
# update process function
# calculate IC
# derive probabilities
# calculate ic's (correlation between factor & goal difference in next game)
# other approaches: find what kind of bets are the most mispriced
# factors: 3y h2h, last 10 matches in all competitions, average goals, moment of goals
# compute information coefficient (..lagged + odds/payoff required

# DATA PREPARATIONS ---------------------------------------------------------------------------------------------------
# load all required data
source_core = pd.read_pickle('pro_data/source_core.pkl')
factor_library = pd.read_pickle('pro_data/flib_e0.pkl')
match_odds = pd.read_pickle('pro_data/match_odds.pkl')
game_day = pd.read_pickle('pro_data/game_day.pkl')

# construct result objects
# win-lose-draw
res_wd = con_res(data=source_core, obj='wdl', field='FTR')
# goals
res_gd = con_res(data=source_core, obj='gd', field=['FTHG', 'FTAG'])


# SIGNAL EFFICACY -----------------------------------------------------------------------------------------------------

# 1) goal superiority signal -----
# Q: Is the hit ratio higher for teams that have a higher gsf score?
# get factor scores
fm = factor_library['field'].unique()[9]

data_gsf = factor_library.query('field==@fm')
# calculate buckets
data_gsf = comp_bucket(data_gsf, bucket_method='first', bucket=5)
# retrieve relevant results to test against
res_custom = res_wd.query('field=="win"').drop('field', axis=1)

# compute the hit ratio by bucket for the factor
gsf_edge = comp_edge(factor_data=data_gsf, results=res_custom, byf=['overall', 'div'])
gsf_edge2 = comp_edge(factor_data=data_gsf, results=res_custom, byf=['season'])
# compute IC's
gsf_ic = info_coef(data=data_gsf, results=res_gd, byf=['div', 'season'])
# compute probability & evaluate
gsf_proba, gsf_evaly = est_prob(scores=data_gsf, result=res_custom, field = fm)



from scipy import stats
from scipy.stats import randint
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import roc_auc_score

results = con_res_wd(data=source_core, field=['FTR'], encoding=False)
arcon = con_mod_datset(scores=factor_library, results=results)

from pandas_datareader import data as web


def est_prob_rf(data):
    """Estimate probability using a random forest classification model."""
    # construct date universe
    per_ind = pd.DataFrame(arcon["date"].unique(), columns=['date']).sort_values(by="date")
    per_ind['val'] = 1
    per_ind_t = per_ind.set_index('date').last('3Y').reset_index()

    # make rolling k estimations
    date_univ = pd.DataFrame(game_day.query("div == 'E0'")['date'].unique(), columns=['date'])

    arcon_spec = arcon.query("season in ['2017', '2018', '2019']").reset_index(drop=True)
    # drop not needed variables
    arcon_0 = arcon_spec.drop(['date', 'div', 'team', 'season'], axis=1)
    arcon_1 = pd.get_dummies(arcon_0, columns=['home'])

    # variable seperation
    y = arcon_1['result'].values.reshape(-1, 1)
    X = arcon_1.drop('result', axis=1).values

    # setup the parameters and distributions to sample from..
    param_dist = {"max_depth": [9, None],
                  "max_features": randint(1, 6),
                  "min_samples_leaf": randint(1, 9),
                  "criterion": ["gini", "entropy"]}
    # instantiate a Decision Tree classifier
    tree = DecisionTreeClassifier()
    # instantiate the RandomizedSearchCV object
    tree_cv = RandomizedSearchCV(tree, param_dist, cv=5)
    # tree_cv = GridSearchCV(estimator=tree, param_grid=param_dist, cv=5)
    # fit it to the data
    tree_cv.fit(X, y)
    y_pp = tree_cv.predict_proba(X)
    y_pp = pd.DataFrame(y_pp, columns = tree_cv.classes_)
    stats.describe(y_pp)

    # add back id info
    res_0 = pd.concat([arcon_spec, y_pp], axis=1)
    res_0 = pd.concat([arcon_spec.loc[:, ['date', 'div', 'season', 'team']], y_pp], axis=1)


a = res_0.loc[:, ['date', 'div', 'season', 'team', 'win']]
a.rename(columns={'win': 'val'}, inplace=True)

odds_event = match_odds.query('field == "odds_win"')
gsf_pos = comp_mispriced(prob=a, odds=odds_event, prob_threshold=0.55, res_threshold=0.1)

# match_odds need to have long- & short version
# bet structuring strategies:
# 1) specific residuals
# 2) all significant residuals
# 3) hedging
# create a scatterplot of resid vs implied & coloured pnl

gsf_pnl = comp_pnl(positions=gsf_pos, odds=odds_event, results=res_wd, event='win', stake=10)

cu.plt_tsline(data=gsf_pnl.loc[:,['date', 'payoff_cum']],
              title="P&L of Goal Superiority Factor",
              subtitle="initial investment of 10$",
              var_names={'payoff_cum':'val'})


# 2) home advantage signal -----
# Q: Do teams that play at home win more often than when they play away?
data_ha = factor_library.query('field=="home"')
data_ha.rename(columns={'val': 'bucket'}, inplace=True)
res_custom = res_wd.query('field=="win"').drop('field', axis=1)
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
positions = factor_library.loc[factor_library.groupby(['div', 'season', 'date', 'field'])['val'].idxmax()].reset_index(drop=True)
positions = positions.loc[:,['div', 'season', 'date', 'team']]
# retrieve the right odds..
odds = match_odds.query('field == "odds_win"')
# calculate pnl
pnl_strats = comp_pnl(positions=positions, odds=odds, results=results, event='win', stake=10)












