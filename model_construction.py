# MODEL CONSTRUCTION --------------------------------------------------------------------------------------------------
import pandas as pd
from scipy import stats
from scipy.stats import randint
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import roc_auc_score

factor_library = pd.read_pickle('pro_data/flib_e0.pkl')
source_core = pd.read_pickle('pro_data/source_core.pkl')
match_odds = pd.read_pickle('pro_data/match_odds.pkl')
# datasets for evaluation
res_wd = con_res(data=source_core, obj='wdl', field='FTR')
results = con_res_wd(data=source_core, field=['FTR'], encoding=False)
arcon = con_mod_datset(scores=factor_library, results=results)


start_date = "2015"
est_dates = mest_dates


def est_hist_prob_rf(arcon, start_date = None, est_dates):
    """Estimate probability using a random forest classification model."""

    # global ml parameter settings
    # setup the parameters and distributions to sample from
    param_dist = {"max_depth": [9, None],
                  "max_features": randint(1, 6),
                  "min_samples_leaf": randint(1, 9),
                  "criterion": ["gini", "entropy"]}

    # construct date universe
    per_ind = est_dates[(est_dates['div'] == arcon['div'].iloc[0])]
    if start_date is not None:
        per_iter = per_ind[(est_dates['date'] >= start_date)]['date'].copy()
    else:
        per_iter = per_ind['date'].copy()


    res_f = pd.DataFrame()
    for t in per_iter:

        # last 3y of obervations
        # t = per_iter.iloc[0]
        per_ind_t = per_ind.query("date <= @t").set_index('date').last('156W').reset_index()
        arcon_spec = pd.merge(arcon, per_ind_t['date'], how="inner", on="date")
        # one-hot encoding
        arcon_spec = pd.get_dummies(arcon_spec, columns=['home'])

        # drop not needed variables
        as_train = arcon_spec[arcon_spec['date'] < t].reset_index(drop=True)
        as_train_0 = as_train.drop(['date', 'div', 'team', 'season'], axis=1)

        # prediction data set
        as_test = arcon_spec[arcon_spec['date'] == t].reset_index(drop=True)
        as_test_0 = as_test.drop(['date', 'div', 'team', 'season'], axis=1)

        # explanatory and target variables declarations
        # -- train
        y_train = as_train_0['result'].values.reshape(-1, 1)
        X_train = as_train_0.drop('result', axis=1).values
        # -- test
        X_test = as_test_0.drop('result', axis=1).values

        # instantiate a Decision Tree classifier
        tree = DecisionTreeClassifier()
        # instantiate the RandomizedSearchCV object
        tree_cv = RandomizedSearchCV(tree, param_dist, cv=5)
        # tree_cv = GridSearchCV(estimator=tree, param_grid=param_dist, cv=5)
        # fit it to the data
        tree_cv.fit(X_train, y_train)
        y_pp = tree_cv.predict_proba(X_test)
        y_pp = pd.DataFrame(y_pp, columns=tree_cv.classes_)
        # stats.describe(y_pp)

        # add back id info
        # res_0 = pd.concat([arcon_spec, y_pp], axis=1)
        res_0 = pd.concat([as_test.loc[:, ['date', 'div', 'season', 'team', 'result']], y_pp], axis=1)
        res_f = pd.concat([res_f, res_0])

        print(t)

    res_f.reset_index(drop=True, inplace=True)




event = "win"
event_of =  "odds_" + event
a = res_f.loc[:, ['date', 'div', 'season', 'team', event]]
a.rename(columns={event: 'val'}, inplace=True)

odds_event = match_odds.query('field == @event_of')
gsf_pos = comp_mispriced(prob=a, odds=odds_event, prob_threshold=0.5, res_threshold=0.10)
gsf_pnl = comp_pnl(positions=gsf_pos, odds=odds_event, results=res_wd, event=event, stake=10)


