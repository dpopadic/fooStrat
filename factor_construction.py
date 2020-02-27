# FACTOR CALCULATION ----------------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import fgoalsup, odds_fields, fodds, expand_field
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import zscore

# load source data..
source_core = pd.read_pickle('pro_data/source_core.pkl')
field_all = source_core['field'].unique()

source_core.query('field=="BbMx>2.5"')
a=source_core.query('div=="E0"')

# goal superiority rating -----------------------------------------------
# next: transform this score to a probability, 1st via constructing a z-score
# does the factor work as hypothesized?
# what are fair odds?

# compute factor
data_fct = fgoalsup(data=source_core, field=['FTHG', 'FTAG'], k=5)
# expand across time
factor_exp = expand_field(data=data_fct)
# impute across divisions
factor_exp['val'] = factor_exp.groupby('date')['val'].transform(lambda x: x.fillna(x.mean()))
# calculate cross-sectional z-score
factor_exp['val'] = factor_exp.groupby(['date'])['val'].transform(lambda x: zscore(x))
# calculate percentile
factor_exp['pval'] = factor_exp.groupby(['date'])['val'].rank(pct=True)
factor_exp['rval'] = factor_exp.groupby(['date'])['val'].rank(method='dense', ascending=False)
factor_exp['qval'] = factor_exp.groupby(['date'])['val'].transform(lambda x: pd.qcut(x, q=5, labels=range(1, 6), duplicates='drop'))

factor_exp['qval'] = factor_exp.groupby(['date'])['val'].apply(pd.qcut, q=5, labels=range(1, 6), duplicates='drop')

a = factor_exp.query('date=="2020-02-23"')
len(a)
a['qval'] = a.loc[:, 'val'].transform(lambda x: pd.qcut(x, q=5, labels=range(1, 6), duplicates='drop'))
a.sort_values('qval', inplace=True)

a = factor_exp.query('date=="2020-02-23"').sort_values('pval')
len(a)
x = pd.DataFrame(np.random.normal(size=1000), columns=['val'])
x['val2'] = pd.qcut(x['val'], q=10, labels=range(1, 11))
x.sort_values('val', inplace=True)


# problem: Chelsea missing on 22/02/2020!

# create function to transform factor to z-score
data_fct2 = data_fct
data_fct2['z'] = data_fct2.groupby(['div'])['val'].transform(lambda x: zscore(x))


# create a function to show the distribution

# across all leagues..
sns.distplot(data_fct.val, bins=100, kde=False)
# premier league vs bundesliga..
x0 = data_fct.query('div=="E0"').loc[:,'val']
x1 = data_fct.query('div=="D1"').loc[:,'val']
f, axes = plt.subplots(2, 1, figsize=(7, 7), sharex=True)
sns.distplot(x0, color="skyblue", ax=axes[0]).set_title('Premier League')
sns.distplot(x1, color="red", ax=axes[1]).set_title('Bundesliga')



# estimate beta to odds!




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












