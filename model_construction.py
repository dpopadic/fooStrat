# MODEL CONSTRUCTION --------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import random as rn
from scipy import stats
from scipy.stats import randint
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import roc_auc_score
from foostrat_utils import con_res, con_res_wd, con_est_dates, con_mod_datset_0, con_mod_datset_1, comp_mispriced, comp_pnl

factor_library = pd.read_pickle('pro_data/flib_e0.pkl')
source_core = pd.read_pickle('pro_data/source_core.pkl')
match_odds = pd.read_pickle('pro_data/match_odds.pkl')
game_day = pd.read_pickle('pro_data/game_day.pkl')

# datasets for evaluation
arcon = con_mod_datset_0(scores=factor_library, results=results)
res_wd = con_res(data=source_core, obj='wdl', field='FTR')
results = con_res_wd(data=source_core, field=['FTR'], encoding=False)
mest_dates = con_est_dates(data=game_day, k=5)

start_date = "2015-01-01"
est_dates = mest_dates




def est_hist_prob_rf(arcon, start_date=None, est_dates):
    """Estimate probability using a random forest classification model."""

    # global ml parameter settings
    # setup the parameters and distributions to sample from
    param_dist = {"max_depth": [10, None],
                  "max_features": ['log2', 'auto', 'sqrt'],
                  "min_samples_leaf": [2, 10, 20],
                  "criterion": ["gini", "entropy"]}

    # construct date universe
    per_ind = est_dates[(est_dates['div'] == arcon['div'].iloc[0])]
    if start_date is not None:
        per_iter = per_ind[(est_dates['date'] >= start_date)]['date']
    else:
        per_iter = per_ind['date']

    res_f = pd.DataFrame()
    for t in per_iter:
        # t = per_iter.iloc[0]
        X_train, X_test, y_train, id_test = con_mod_datset_1(data=arcon, per_ind=per_ind, t=t)
        # instantiate a Decision Tree classifier
        # tree = DecisionTreeClassifier()
        # instantiate the RandomizedSearchCV object
        # tree_cv = GridSearchCV(estimator=tree, param_grid=param_dist, cv=5)

        # instantiate ada..
        tree = DecisionTreeClassifier(max_depth=10,
                                      max_features="auto",
                                      min_samples_leaf=10,
                                      random_state=1)
        ada = AdaBoostClassifier(base_estimator=tree,
                                 n_estimators=10,
                                 random_state=1)
        ada.fit(X_train, y_train)
        y_pp = ada.predict_proba(X_test)
        y_pp = pd.DataFrame(y_pp, columns=ada.classes_)

        # fit it to the data
        #tree_cv.fit(X_train, y_train)
        #y_pp = tree_cv.predict_proba(X_test)
        #y_pp = pd.DataFrame(y_pp, columns=tree_cv.classes_)
        # stats.describe(y_pp)

        # add back id info
        # res_0 = pd.concat([arcon_spec, y_pp], axis=1)
        res_0 = pd.concat([id_test, y_pp], axis=1)
        res_f = pd.concat([res_f, res_0])

        print(t)

    res_f.reset_index(drop=True, inplace=True)


event = "draw"
event_of =  "odds_" + event
a = res_f.loc[:, ['date', 'div', 'season', 'team', event]]
a.rename(columns={event: 'val'}, inplace=True)

odds_event = match_odds.query('field == @event_of')
gsf_pos = comp_mispriced(prob=a, odds=odds_event, prob_threshold=0.5, res_threshold=0.10)
gsf_pnl = comp_pnl(positions=gsf_pos, odds=odds_event, results=res_wd, event=event, stake=10)




