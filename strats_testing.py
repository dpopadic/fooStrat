# STRATEGY TESTING ----------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import con_res, comp_pnl, comp_edge, comp_bucket, info_coef
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix

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
# compute IC's
gsf_ic = info_coef(data=data_gsf, results=res_gd, byf=['div', 'season'])


# create info_coef function + derive implied probability via logit fit..
# a few options: entire dataset fit, expanding window, rolling window

A = data_gsf.pivot_table(index=['season', 'div', 'date', 'team'],
                         columns='field',
                         values='val').reset_index()
# merge with results
B = pd.merge(res_custom, A, on=['div', 'season', 'date', 'team'], how='left')

C = B.query('div=="Ireland Premier Division"')
del C['div']

y = C['val'].values.reshape(-1,1)
X = C['goal_superiority'].values.reshape(-1,1)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state=42)
mod = LogisticRegression()
# fit model..
mod.fit(X, y)
# predict the labels of the test set..
y_pred = mod.predict(X)
# probability
y_pp = mod.predict_proba(X)
y_pp.max()
y_pp.min()
y_pp.mean()
# model statistics..
conf_mat = confusion_matrix(y, y_pred)
cr = classification_report(y, y_pred)

def accuracy_stats(conf_mat):
    """Calculate relevant ratio's from the confusion matrix with two or more classes.

    Parameters:
    -----------
        conf_mat (array):   a confusion matrix with at least two classes

    Returns:
    --------
        Summary statistics in ratio format.

    Details:
    --------
    

    """

# i.   accuracy: (tp + tn) / (tp + tn + fp + fn)
# ii.  precision: tp / (tp + fp) (also called positive predictive value - PPV)
# iii. recall: tp / (tp + fn) (also called sensitivity, hit-rate, true-positive rate)
# iv.  F1 score: 2 * (precision * recall) / (precision + recall) -> harmonic mean of precision & recall
# .. high precision: not many real emails predicted as spam
# .. high recall: predicted most spam emails correctly

FP = conf_mat.sum(axis=0) - np.diag(conf_mat)
FN = conf_mat.sum(axis=1) - np.diag(conf_mat)
TP = np.diag(conf_mat)
TN = conf_mat.sum() - (FP + FN + TP)

# Sensitivity, hit rate, recall, or true positive rate
TPR = TP/(TP+FN)
# Specificity or true negative rate
TNR = TN/(TN+FP)
# Precision or positive predictive value
PPV = TP/(TP+FP)
# Negative predictive value
NPV = TN/(TN+FN)
# Fall out or false positive rate
FPR = FP/(FP+TN)
# False negative rate
FNR = FN/(TP+FN)
# False discovery rate
FDR = FP/(TP+FP)

# Overall accuracy
ACC = (TP+TN)/(TP+FP+FN+TN)


(1730+277)/(1730+277+212+945)






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








