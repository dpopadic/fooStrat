import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix
from sklearn.linear_model import LogisticRegression
from fooStrat.helpers import class_accuracy_stats
import fooStrat.servicers as fose


def est_prob(scores, result, field):
    """Estimate probability of an event occuring (eg. win) for a factor using a logit-model.

    Parameters:
    -----------
        scores (dataframe):     a dataframe with at least columns date, team, field, val (eg. goal_superiority)
        result (dataframe):     a dataframe with results and columns date, team & val (eg. 0/1 for loss/win)
        field (string):         the field in scores to uses to fit the model (eg. "goal_superiority")

    Returns:
    --------
        A few objects are returned:
                1. A dataframe with probabilities for each event
                2. Evaluation statistics

    # Details:
    ----------
        Note that the probabilities are related to the 1-event (eg. win).

    """
    acon = scores.pivot_table(index=['season', 'div', 'date', 'team'],
                              columns='field',
                              values='val').reset_index()
    # merge with results
    prob = pd.merge(result, acon,
                    on=['div', 'season', 'date', 'team'],
                    how='left')
    prob.dropna(inplace=True)
    # fit logit model
    y = prob['val'].values.ravel()
    X = prob[field].values.reshape(-1, 1)
    mod = LogisticRegression()
    mod.fit(X, y)
    y_pred = mod.predict(X)
    # retrieve probability
    # note: that output is 2d array with 1st (2nd) column probability for 0 (1) with 0.5 threshold
    y_pp = mod.predict_proba(X)[:, 1]
    # accurary evaluation
    conf_mat = confusion_matrix(y, y_pred)
    stats = class_accuracy_stats(conf_mat)
    # reshape results
    prob["val"] = y_pp
    del prob[field]

    return prob, stats



def con_mod_datset_0(scores, results):
    """Construct the modelling data set.

    Parameters:
    -----------
        scores:     pandas dataframe
                    signals for each team with columns season, div, date, team, field, val
        results:    pandas dataframe
                    results of games with columns season, div, date, team, val

    """
    # reshape to wide format
    acon = scores.pivot_table(index=['season', 'div', 'date', 'team'],
                              columns='field',
                              values='val').reset_index()

    rcon = results.drop(['field'], axis=1)
    rcon.rename(columns={'val': 'result'}, inplace=True)

    # signals and results
    arcon = pd.merge(rcon, acon,
                     on=['div', 'season', 'date', 'team'],
                     how='inner')

    # drop rows where variables have no data at all
    arcon = arcon.dropna().reset_index(level=0, drop=True)

    return arcon



def con_mod_datset_1(data, per_ind, t, per):
    """Construct the modelling dataset for a single model fit at time t. The default lookback
    period is 3 years. The model is only fitted at dates specified in per_ind.

    Parameters:
    -----------
        data:       pd dataframe
                    a table with factor data and key columns date, div, season, team, result, factor_1, .., factor_n
        per_ind:    pd dataframe
                    a table with columns div, date representing the dates on which games took place
        t:          datetime64
                    a date of interest for which to fit the model
        per:        str
                    a string indicating the lookback period to use for the model data set (eg. '52W')

    Details:
    --------
        For every point in time t, the last n observations are in X_train up to t-1 and X_test
        includes all observations for t that need to be predicted. The id_test output object
        provides all meta-data/keys for this prediction set.

    Returns:
    --------
        X_train, X_test, y_train, id_test
    """
    # consider only last n obervations
    per_ind_t = per_ind.query("date <= @t").set_index('date').last(per).reset_index()
    data_ed = pd.merge(data, per_ind_t['date'], how="inner", on="date")
    # one-hot encoding
    data_ed = pd.get_dummies(data_ed, columns=['home'])

    # drop not needed variables
    as_train = data_ed[data_ed['date'] < t].reset_index(drop=True)
    as_train_0 = as_train.drop(['date', 'div', 'team', 'season'], axis=1)

    # prediction data set
    as_test = data_ed[data_ed['date'] == t].reset_index(drop=True)
    as_test_0 = as_test.drop(['date', 'div', 'team', 'season'], axis=1)

    # explanatory and target variables declarations
    # -- train
    y_train = as_train_0['result'].values
    X_train = as_train_0.drop('result', axis=1).values
    # -- test
    X_test = as_test_0.drop('result', axis=1).values

    # meta data with keys
    id_test = as_test.loc[:, ['date', 'div', 'season', 'team', 'result']]

    return X_train, X_test, y_train, id_test




def est_hist_prob_rf(arcon, est_dates, start_date=None):
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

    res = pd.DataFrame()
    for t in per_iter:
        # t = per_iter.iloc[0]
        X_train, X_test, y_train, id_test = con_mod_datset_1(data=arcon,
                                                             per_ind=per_ind,
                                                             t=t,
                                                             per='312W')
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
        pred = ada.predict_proba(X_test)
        pred = pd.DataFrame(pred, columns=ada.classes_)

        # fit it to the data
        #tree_cv.fit(X_train, y_train)
        #y_pp = tree_cv.predict_proba(X_test)
        #y_pp = pd.DataFrame(y_pp, columns=tree_cv.classes_)
        # stats.describe(y_pp)

        # add back id info
        # res_0 = pd.concat([arcon_spec, y_pp], axis=1)
        tmp = pd.concat([id_test, pred], axis=1)
        res = pd.concat([res, tmp])

    res.reset_index(drop=True, inplace=True)
    return res




def comp_mispriced(prob, odds, prob_threshold, res_threshold):
    """
    Parameters
    ----------
    prob:   pandas dataframe
            implied probabilities from a model for each event with columns date, team
    odds:   pandas dataframe
            market odds from bookmaker
    prob_threshold: float
                    implied probability threshold for events to look at
    res_threshold:  float
                    magnitude of mispricing residual to look at
    Returns
    -------
    A pandas dataframe with mispriced events.

    """
    resi = pd.merge(odds.rename(columns={'val': 'odds'}),
                    prob.rename(columns={'val': 'implied'}),
                    on=["div", "season", "date", "team"],
                    how="left")
    resi["market"] = 1 / resi.loc[:, "odds"]
    resi["resid"] = resi["implied"] - resi["market"]
    pos = resi.query("resid>@res_threshold & implied>@prob_threshold").loc[:, ['season', 'div', 'date', 'team']]
    pos.reset_index(inplace=True, drop=True)
    return pos



